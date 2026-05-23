from __future__ import annotations

import os
import re
import secrets
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, cast
from urllib.parse import quote

import httpx
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier
from starlette.responses import JSONResponse

from backend_runtime import (
    DEFAULT_ENABLED_TOOLS,
    configured_enabled_tools,
    effective_enabled_tools,
    validate_auth_environment,
)
from slack_native import (
    SlackSessionClient,
    map_usergroups,
    map_saved_items,
    render_channels_csv,
    render_messages_csv,
    render_saved_items_csv,
    render_unreads_csv,
    render_usergroups_csv,
    render_users_resource_csv,
    render_users_search_csv,
    map_history_messages,
    map_search_messages,
    search_users,
    usergroup_membership_result_json,
    usergroup_result_json,
)

RUNTIME_PLACEHOLDER_RE = re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$")
REPO_ROOT = Path(__file__).resolve().parent


def _runtime_env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        cleaned = value.strip()
        if not cleaned or RUNTIME_PLACEHOLDER_RE.fullmatch(cleaned):
            continue
        return cleaned
    return default


def _split_csv(value: str) -> list[str]:
    return [token.strip() for token in value.split(",") if token.strip()]


def _env_flag(name: str) -> bool:
    return _runtime_env(name, default="").strip().lower() in {"1", "true", "yes", "on"}


def _slack_domain() -> str:
    return "slack-gov.com" if _env_flag("SLACK_MCP_GOVSLACK") else "slack.com"


def _slack_api_url(method_name: str) -> str:
    return f"https://{_slack_domain()}/api/{method_name}"


def _slack_session_auth_headers() -> dict[str, str]:
    token = _runtime_env("SLACK_MCP_XOXC_TOKEN")
    if not token:
        raise ValueError("SLACK_MCP_XOXC_TOKEN is required for harness Slack session operations.")
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": _runtime_env("SLACK_MCP_USER_AGENT", default="slack-mcp-harness/1.0"),
    }


def _slack_session_cookies() -> dict[str, str]:
    cookie = _runtime_env("SLACK_MCP_XOXD_TOKEN")
    if not cookie:
        raise ValueError("SLACK_MCP_XOXD_TOKEN is required for harness Slack session operations.")
    encoded_cookie = quote(cookie, safe="-._~%abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return {
        "d": encoded_cookie,
        "d-s": str(int(time.time()) - 10),
    }


def _httpx_timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=20.0, read=60.0, write=60.0, pool=20.0)


_effective_tools = effective_enabled_tools()


def _tool_enabled(name: str) -> bool:
    return _effective_tools == "all" or name in _effective_tools


def _native_tool_overrides() -> list[str]:
    tools = list(DEFAULT_ENABLED_TOOLS) if _effective_tools == "all" else list(_effective_tools)
    return [name for name in tools if _tool_enabled(name)]


def _native_resource_overrides() -> list[str]:
    return ["channels", "users"]


def _load_api_keys() -> list[str]:
    api_key_mode = _runtime_env("API_KEY_MODE", default="").strip().lower()
    if api_key_mode == "disabled":
        return []

    keys: list[str] = []
    for key in (_runtime_env("SLACK_MCP_API_KEY"), _runtime_env("MCP_API_KEY")):
        if key:
            keys.append(key)

    multi = _runtime_env("MCP_API_KEYS")
    if multi:
        keys.extend(_split_csv(multi))

    return list(dict.fromkeys(keys))


class StaticApiKeyVerifier(TokenVerifier):
    def __init__(self, api_keys: Iterable[str], base_url: str | None = None) -> None:
        super().__init__(base_url=base_url or None)
        self._api_keys = [key for key in api_keys if key]

    async def verify_token(self, token: str) -> AccessToken | None:
        for key in self._api_keys:
            if secrets.compare_digest(token, key):
                return AccessToken(token=token, client_id="slack-mcp", scopes=[])
        return None


validate_auth_environment()

api_keys = _load_api_keys()
auth = StaticApiKeyVerifier(api_keys=api_keys, base_url=_runtime_env("BASE_URL")) if api_keys else None
server = FastMCP(name="slack-mcp", auth=auth)
mcp = server


def _configured_enabled_tools_payload() -> list[str] | str:
    configured = configured_enabled_tools()
    if configured is None:
        return "default-all"
    return configured


def _effective_enabled_tools_payload() -> list[str] | str:
    effective = effective_enabled_tools()
    if effective == "all":
        return "all"
    return list(effective)


def _health_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "server": "slack-mcp",
        "implementation": "fastmcp-python-native",
        "backendMode": "native",
        "backendCommand": None,
        "defaultEnabledTools": list(DEFAULT_ENABLED_TOOLS),
        "configuredEnabledTools": _configured_enabled_tools_payload(),
        "effectiveEnabledTools": _effective_enabled_tools_payload(),
        "apiKeyAuthConfigured": bool(api_keys),
        "pythonNativeTools": _native_tool_overrides(),
        "pythonNativeResources": _native_resource_overrides(),
    }


def _native_session_client() -> SlackSessionClient:
    return SlackSessionClient(
        xoxc_token=_runtime_env("SLACK_MCP_XOXC_TOKEN"),
        xoxd_token=_runtime_env("SLACK_MCP_XOXD_TOKEN"),
        user_agent=_runtime_env("SLACK_MCP_USER_AGENT", default="slack-mcp-native/1.0"),
        govslack=_env_flag("SLACK_MCP_GOVSLACK"),
    )


@server.custom_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def root_health(_request):
    return JSONResponse(_health_payload())


@server.custom_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
async def health(_request):
    return JSONResponse(_health_payload())


@server.custom_route("/healthz", methods=["GET", "HEAD"], include_in_schema=False)
async def healthz(_request):
    return JSONResponse(_health_payload())


if _tool_enabled("channels_list"):

    @server.tool(
        name="channels_list",
        description="List Slack channels, DMs, and MPIMs as CSV.",
    )
    async def native_channels_list(channel_types: str = "public_channel,private_channel,im,mpim", limit: int = 100) -> str:
        if limit <= 0:
            limit = 100
        client = _native_session_client()
        try:
            channels = await client.list_channels(channel_types=channel_types, limit=limit)
        finally:
            await client.aclose()
        return render_channels_csv(channels)

if _tool_enabled("channels_me"):

    @server.tool(
        name="channels_me",
        description="List joined Slack channels as CSV.",
    )
    async def native_channels_me(limit: int = 100) -> str:
        if limit <= 0:
            limit = 100
        client = _native_session_client()
        try:
            channels = await client.list_channels(
                channel_types="public_channel,private_channel,im,mpim",
                limit=limit,
                only_joined=True,
            )
        finally:
            await client.aclose()
        return render_channels_csv(channels)


if _tool_enabled("users_search"):

    @server.tool(
        name="users_search",
        description="Search Slack users by username, real name, display name, or email.",
    )
    async def native_users_search(query: str, limit: int = 10) -> str:
        query = query.strip()
        if not query:
            raise ValueError("query is required")
        if limit <= 0:
            limit = 10
        if limit > 100:
            limit = 100

        client = _native_session_client()
        try:
            users, dm_by_user = await client.iter_users(), await client.list_im_channels()
        finally:
            await client.aclose()

        return render_users_search_csv(search_users(users, dm_by_user, query=query, limit=limit))


if _tool_enabled("conversations_history"):

    @server.tool(
        name="conversations_history",
        description="Return recent channel history as CSV.",
    )
    async def native_conversations_history(channel_id: str, limit: str = "50") -> str:
        numeric_limit = int(limit) if str(limit).isdigit() else 50
        if numeric_limit <= 0:
            numeric_limit = 50
        client = _native_session_client()
        try:
            users = await client.iter_users()
            messages = await client.conversations_history(channel_id=channel_id, limit=numeric_limit)
        finally:
            await client.aclose()
        return render_messages_csv(map_history_messages(messages, channel_id=channel_id, users=users))

if _tool_enabled("conversations_replies"):

    @server.tool(
        name="conversations_replies",
        description="Return thread replies as CSV.",
    )
    async def native_conversations_replies(channel_id: str, thread_ts: str, limit: str = "50") -> str:
        numeric_limit = int(limit) if str(limit).isdigit() else 50
        if numeric_limit <= 0:
            numeric_limit = 50
        client = _native_session_client()
        try:
            users = await client.iter_users()
            messages = await client.conversations_history(
                channel_id=channel_id,
                limit=numeric_limit,
                oldest=thread_ts,
                latest=thread_ts,
            )
            if not messages:
                messages = await client._post(
                    "conversations.replies",
                    data={"channel": channel_id, "ts": thread_ts, "limit": str(numeric_limit)},
                )
                messages = [message for message in (messages.get("messages") or []) if isinstance(message, dict)]
        finally:
            await client.aclose()
        return render_messages_csv(map_history_messages(messages, channel_id=channel_id, users=users))

if _tool_enabled("conversations_search_messages"):

    @server.tool(
        name="conversations_search_messages",
        description="Search Slack messages and return CSV rows.",
    )
    async def native_conversations_search_messages(search_query: str, limit: int = 100) -> str:
        if not search_query.strip():
            raise ValueError("search_query is required")
        if limit <= 0:
            limit = 100
        client = _native_session_client()
        try:
            matches = await client.search_messages(query=search_query.strip(), count=limit, page=1)
        finally:
            await client.aclose()
        return render_messages_csv(map_search_messages(matches))

if _tool_enabled("conversations_unreads"):

    @server.tool(
        name="conversations_unreads",
        description="Return unread conversation summary as CSV.",
    )
    async def native_conversations_unreads(
        include_messages: bool = True,
        channel_types: str = "all",
        max_channels: int = 50,
        max_messages_per_channel: int = 10,
        mentions_only: bool = False,
        include_muted: bool = False,
    ) -> str:
        del include_messages, max_messages_per_channel, mentions_only
        if max_channels <= 0:
            max_channels = 50
        client = _native_session_client()
        try:
            rows = await client.unread_summaries(
                channel_types=channel_types,
                max_channels=max_channels,
                include_muted=include_muted,
            )
        finally:
            await client.aclose()
        return render_unreads_csv(rows)


if _tool_enabled("conversations_add_message"):

    @server.tool(
        name="conversations_add_message",
        description="Add a message to a public channel, private channel, or direct message conversation.",
    )
    async def native_conversations_add_message(
        channel_id: str,
        text: str = "",
        thread_ts: str = "",
        content_type: str = "text/markdown",
        blocks: str = "",
    ) -> str:
        body = text.strip()
        if not body and not blocks.strip():
            raise ValueError("text or blocks is required")
        client = _native_session_client()
        try:
            resolved_channel_id, message_ts = await client.post_message(
                channel_id=channel_id,
                text=body,
                thread_ts=thread_ts.strip(),
                content_type=content_type.strip() or "text/markdown",
                blocks=blocks,
            )
        finally:
            await client.aclose()
        return f"Successfully posted message to {resolved_channel_id} at {message_ts}"


if _tool_enabled("conversations_mark"):

    @server.tool(
        name="conversations_mark",
        description="Mark a channel or DM as read.",
    )
    async def native_conversations_mark(channel_id: str, ts: str = "") -> str:
        client = _native_session_client()
        try:
            resolved_channel_id = await client.resolve_channel_id(channel_id)
            mark_ts = await client.mark_conversation(channel_id=resolved_channel_id, ts=ts)
        finally:
            await client.aclose()
        return f"Successfully marked channel {resolved_channel_id} as read up to {mark_ts}"


if _tool_enabled("reactions_add"):

    @server.tool(
        name="reactions_add",
        description="Add an emoji reaction to a Slack message.",
    )
    async def native_reactions_add(channel_id: str, timestamp: str, emoji: str) -> str:
        if not timestamp.strip():
            raise ValueError("timestamp is required")
        client = _native_session_client()
        try:
            resolved_channel_id = await client.add_reaction(channel_id=channel_id, timestamp=timestamp, emoji=emoji)
        finally:
            await client.aclose()
        cleaned = emoji.strip().strip(":")
        return f"Successfully added :{cleaned}: reaction to message {timestamp} in channel {resolved_channel_id}"


if _tool_enabled("reactions_remove"):

    @server.tool(
        name="reactions_remove",
        description="Remove an emoji reaction from a Slack message.",
    )
    async def native_reactions_remove(channel_id: str, timestamp: str, emoji: str) -> str:
        if not timestamp.strip():
            raise ValueError("timestamp is required")
        client = _native_session_client()
        try:
            resolved_channel_id = await client.remove_reaction(
                channel_id=channel_id,
                timestamp=timestamp,
                emoji=emoji,
            )
        finally:
            await client.aclose()
        cleaned = emoji.strip().strip(":")
        return f"Successfully removed :{cleaned}: reaction from message {timestamp} in channel {resolved_channel_id}"


if _tool_enabled("conversations_join"):

    @server.tool(
        name="conversations_join",
        description="Join a public Slack channel.",
    )
    async def native_conversations_join(channel_id: str) -> str:
        client = _native_session_client()
        try:
            resolved_channel_id = await client.join_conversation(channel_id=channel_id)
        finally:
            await client.aclose()
        return f"Successfully joined channel {resolved_channel_id}"


if _tool_enabled("conversations_leave"):

    @server.tool(
        name="conversations_leave",
        description="Leave a Slack conversation.",
    )
    async def native_conversations_leave(channel_id: str) -> str:
        client = _native_session_client()
        try:
            resolved_channel_id = await client.leave_conversation(channel_id=channel_id)
        finally:
            await client.aclose()
        return f"Successfully left channel {resolved_channel_id}"


if _tool_enabled("attachment_get_data"):

    @server.tool(
        name="attachment_get_data",
        description="Download attachment metadata and content by file ID.",
    )
    async def native_attachment_get_data(file_id: str) -> str:
        if not file_id.strip():
            raise ValueError("file_id is required")
        client = _native_session_client()
        try:
            payload = await client.attachment_data(file_id=file_id.strip())
        finally:
            await client.aclose()
        return JSONResponse(payload).body.decode("utf-8")


if _tool_enabled("saved_list"):

    @server.tool(
        name="saved_list",
        description="List saved items as CSV.",
    )
    async def native_saved_list(
        filter: str = "saved",
        limit: int = 50,
        include_messages: bool = True,
        max_messages_per_item: int = 5,
    ) -> str:
        del include_messages, max_messages_per_item
        if limit <= 0:
            limit = 50
        if limit > 200:
            limit = 200
        client = _native_session_client()
        try:
            channels = await client.list_channels(channel_types="public_channel,private_channel,im,mpim", limit=0)
            payload = await client.saved_list(filter_name=filter, limit=limit)
        finally:
            await client.aclose()
        channels_by_id = {channel.channel_id: channel for channel in channels}
        return render_saved_items_csv(map_saved_items(payload, channels_by_id=channels_by_id))

if _tool_enabled("saved_update"):

    @server.tool(
        name="saved_update",
        description="Update a saved item.",
    )
    async def native_saved_update(item_id: str, ts: str, mark: str = "", date_due: int = 0) -> str:
        if not item_id.strip() or not ts.strip():
            raise ValueError("item_id and ts are required parameters")
        if not mark and not date_due:
            raise ValueError("at least one of mark or date_due must be provided")
        client = _native_session_client()
        try:
            await client.saved_update(item_id=item_id.strip(), ts=ts.strip(), mark=mark.strip(), date_due=date_due)
        finally:
            await client.aclose()

        action = "updated"
        if mark == "completed":
            action = "marked as completed"
        if date_due > 0:
            due_time = datetime.fromtimestamp(date_due, UTC).strftime("%Y-%m-%d %H:%M")
            action += f", due date set to {due_time}"
        return f"Successfully {action} saved item (item_id={item_id}, ts={ts})"

if _tool_enabled("saved_clear_completed"):

    @server.tool(
        name="saved_clear_completed",
        description="Clear completed saved items.",
    )
    async def native_saved_clear_completed() -> str:
        client = _native_session_client()
        try:
            await client.saved_clear_completed()
        finally:
            await client.aclose()
        return "Successfully cleared all completed saved items"


if _tool_enabled("usergroups_list"):

    @server.tool(
        name="usergroups_list",
        description="List Slack user groups as CSV.",
    )
    async def native_usergroups_list(
        include_users: bool = False,
        include_count: bool = True,
        include_disabled: bool = False,
    ) -> str:
        client = _native_session_client()
        try:
            groups = await client.usergroups_list(
                include_users=include_users,
                include_count=include_count,
                include_disabled=include_disabled,
            )
        finally:
            await client.aclose()
        return render_usergroups_csv(map_usergroups(groups))


if _tool_enabled("usergroups_create"):

    @server.tool(
        name="usergroups_create",
        description="Create a Slack user group.",
    )
    async def native_usergroups_create(
        name: str,
        handle: str = "",
        description: str = "",
        channels: str = "",
    ) -> str:
        if not name.strip():
            raise ValueError("name is required")
        client = _native_session_client()
        try:
            group = await client.usergroups_create(
                name=name.strip(),
                handle=handle.strip(),
                description=description.strip(),
                channels=channels.strip(),
            )
        finally:
            await client.aclose()
        return usergroup_result_json(group)


if _tool_enabled("usergroups_update"):

    @server.tool(
        name="usergroups_update",
        description="Update Slack user group metadata.",
    )
    async def native_usergroups_update(
        usergroup_id: str,
        name: str = "",
        handle: str = "",
        description: str = "",
        channels: str = "",
    ) -> str:
        if not usergroup_id.strip():
            raise ValueError("usergroup_id is required")
        if not any(value.strip() for value in (name, handle, description, channels)):
            raise ValueError("at least one update field (name, handle, description, or channels) is required")
        client = _native_session_client()
        try:
            group = await client.usergroups_update(
                usergroup_id=usergroup_id.strip(),
                name=name.strip(),
                handle=handle.strip(),
                description=description.strip(),
                channels=channels.strip(),
            )
        finally:
            await client.aclose()
        return usergroup_result_json(group)


if _tool_enabled("usergroups_users_update"):

    @server.tool(
        name="usergroups_users_update",
        description="Replace Slack user group members.",
    )
    async def native_usergroups_users_update(usergroup_id: str, users: str) -> str:
        if not usergroup_id.strip():
            raise ValueError("usergroup_id is required")
        if not users.strip():
            raise ValueError("users is required")
        client = _native_session_client()
        try:
            group = await client.usergroups_users_update(usergroup_id=usergroup_id.strip(), users=users.strip())
        finally:
            await client.aclose()
        return usergroup_result_json(group, include_users=True)


if _tool_enabled("usergroups_me"):

    @server.tool(
        name="usergroups_me",
        description="Manage current user Slack user group membership.",
    )
    async def native_usergroups_me(action: str, usergroup_id: str = "") -> str:
        selected_action = action.strip().lower()
        if selected_action not in {"list", "join", "leave"}:
            raise ValueError("action must be 'list', 'join', or 'leave'")

        client = _native_session_client()
        try:
            current_user_id = await client.current_user_id()
            if selected_action == "list":
                groups = await client.usergroups_list(include_users=True, include_count=True, include_disabled=False)
                my_groups = [
                    group
                    for group in groups
                    if current_user_id and current_user_id in [str(user_id) for user_id in (group.get("users") or [])]
                ]
                return render_usergroups_csv(map_usergroups(my_groups))

            if not usergroup_id.strip():
                raise ValueError("usergroup_id is required for join/leave actions")

            members = await client.usergroup_members(usergroup_id=usergroup_id.strip())
            is_member = current_user_id in members
            if selected_action == "join" and is_member:
                return "You are already a member of this user group."
            if selected_action == "leave" and not is_member:
                return "You are not a member of this user group."

            new_members = list(members)
            if selected_action == "join":
                new_members.append(current_user_id)
                message = "Successfully joined the user group."
            else:
                new_members = [member for member in members if member != current_user_id]
                message = "Successfully left the user group."

            group = await client.usergroups_users_update(
                usergroup_id=usergroup_id.strip(),
                users=",".join(new_members),
            )
        finally:
            await client.aclose()

        return usergroup_membership_result_json(
            message=message,
            group_id=str(group.get("id") or usergroup_id.strip()),
            group_name=str(group.get("name") or ""),
            user_count=int(group.get("user_count") or 0),
        )


channels_resource_uri = f"slack://{_runtime_env('SLACK_MCP_WORKSPACE', default='workspace')}/channels"
users_resource_uri = f"slack://{_runtime_env('SLACK_MCP_WORKSPACE', default='workspace')}/users"

@server.resource(channels_resource_uri, mime_type="text/csv", name="slack_channels")
async def native_channels_resource() -> str:
    client = _native_session_client()
    try:
        channels = await client.list_channels(channel_types="public_channel,private_channel,im,mpim", limit=0)
    finally:
        await client.aclose()
    return render_channels_csv(channels)

@server.resource(users_resource_uri, mime_type="text/csv", name="slack_users")
async def native_users_resource() -> str:
    client = _native_session_client()
    try:
        users = await client.iter_users()
    finally:
        await client.aclose()
    return render_users_resource_csv(users)


if _env_flag("SLACK_MCP_HARNESS_UPLOAD_TOOL"):

    @server.tool(
        name="harness_upload_text_file",
        description=(
            "Harness-only helper that uploads a small UTF-8 text file to Slack using "
            "files.getUploadURLExternal and files.completeUploadExternal, then returns the file_id."
        ),
    )
    async def harness_upload_text_file(
        filename: str,
        content: str,
        title: str | None = None,
        channel_id: str | None = None,
        initial_comment: str | None = None,
        thread_ts: str | None = None,
    ) -> dict[str, Any]:
        file_bytes = content.encode("utf-8")
        cookies = _slack_session_cookies()
        headers = _slack_session_auth_headers()

        with httpx.Client(timeout=_httpx_timeout(), headers=headers, cookies=cookies) as client:
            get_url_response = client.post(
                _slack_api_url("files.getUploadURLExternal"),
                data={"filename": filename, "length": str(len(file_bytes))},
            )
            get_url_response.raise_for_status()
            get_url_data = cast(dict[str, Any], get_url_response.json())
            if not get_url_data.get("ok"):
                raise ValueError(
                    f"files.getUploadURLExternal failed: {get_url_data.get('error', 'unknown_error')}"
                )

            upload_url = str(get_url_data["upload_url"])
            file_id = str(get_url_data["file_id"])

            upload_response = client.post(
                upload_url,
                content=file_bytes,
                headers={"Content-Type": "text/plain; charset=utf-8"},
            )
            if upload_response.status_code != 200:
                multipart_response = client.post(
                    upload_url,
                    files={"filename": (filename, file_bytes, "text/plain; charset=utf-8")},
                )
                multipart_response.raise_for_status()
            else:
                upload_response.raise_for_status()

            complete_payload: dict[str, Any] = {
                "files": [{"id": file_id, "title": title or filename}],
            }
            if channel_id:
                complete_payload["channel_id"] = channel_id
            if initial_comment:
                complete_payload["initial_comment"] = initial_comment
            if thread_ts:
                complete_payload["thread_ts"] = thread_ts

            complete_response = client.post(
                _slack_api_url("files.completeUploadExternal"),
                json=complete_payload,
            )
            complete_response.raise_for_status()
            complete_data = cast(dict[str, Any], complete_response.json())
            if not complete_data.get("ok"):
                raise ValueError(
                    f"files.completeUploadExternal failed: {complete_data.get('error', 'unknown_error')}"
                )

        files = complete_data.get("files") or []
        uploaded_file = files[0] if files else {"id": file_id, "title": title or filename}
        return {
            "ok": True,
            "file_id": uploaded_file.get("id", file_id),
            "title": uploaded_file.get("title", title or filename),
            "filename": filename,
            "channel_id": channel_id,
            "shared": bool(channel_id),
        }


if _env_flag("SLACK_MCP_HARNESS_SAVED_TOOL"):

    @server.tool(
        name="harness_save_message_for_later",
        description=(
            "Harness-only helper that creates a Save for Later fixture for a Slack message "
            "through the deprecated-but-still-working stars.add API, then returns the observed saved state."
        ),
    )
    async def harness_save_message_for_later(channel_id: str, ts: str) -> dict[str, Any]:
        cookies = _slack_session_cookies()
        headers = _slack_session_auth_headers()

        with httpx.Client(timeout=_httpx_timeout(), headers=headers, cookies=cookies) as client:
            save_response = client.post(
                _slack_api_url("stars.add"),
                data={"channel": channel_id, "timestamp": ts},
            )
            save_response.raise_for_status()
            save_data = cast(dict[str, Any], save_response.json())
            if not save_data.get("ok"):
                raise ValueError(f"stars.add failed: {save_data.get('error', 'unknown_error')}")

            history_response = client.post(
                _slack_api_url("conversations.history"),
                data={
                    "channel": channel_id,
                    "latest": ts,
                    "oldest": ts,
                    "inclusive": "true",
                    "limit": "1",
                },
            )
            history_response.raise_for_status()
            history_data = cast(dict[str, Any], history_response.json())
            if not history_data.get("ok"):
                raise ValueError(
                    "conversations.history failed after stars.add: "
                    f"{history_data.get('error', 'unknown_error')}"
                )

        messages = history_data.get("messages") or []
        message = messages[0] if messages else {}
        saved_state = message.get("saved") or {}
        return {
            "ok": True,
            "channel_id": channel_id,
            "ts": ts,
            "saved": saved_state,
        }


def main() -> None:
    transport_name = _runtime_env("FASTMCP_TRANSPORT", default="streamable-http").lower()
    if transport_name == "http":
        transport_name = "streamable-http"
    if transport_name == "stdio":
        server.run()
    else:
        host = _runtime_env("HOST", default="127.0.0.1")
        port = int(_runtime_env("PORT", default="3005"))
        path = _runtime_env("MCP_PATH", default="/mcp")
        server.run(
            transport=transport_name,
            host=host,
            port=port,
            path=path,
            show_banner=False,
        )


if __name__ == "__main__":
    main()
