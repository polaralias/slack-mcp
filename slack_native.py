from __future__ import annotations

import base64
import csv
import io
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import httpx


@dataclass(frozen=True)
class NativeUserSearchResult:
    user_id: str
    user_name: str
    real_name: str
    display_name: str
    email: str
    title: str
    dm_channel_id: str


@dataclass(frozen=True)
class NativeChannelResult:
    channel_id: str
    name: str
    topic: str
    purpose: str
    member_count: int
    cursor: str = ""


@dataclass(frozen=True)
class NativeMessageResult:
    msg_id: str
    user_id: str
    user_name: str
    real_name: str
    channel: str
    thread_ts: str
    text: str
    timestamp: str
    permalink: str
    reactions: str
    bot_name: str
    file_count: int
    attachment_ids: str
    has_media: bool
    cursor: str = ""


@dataclass(frozen=True)
class NativeUnreadResult:
    channel_id: str
    channel_name: str
    channel_type: str
    unread_count: int
    last_read: str
    latest: str


@dataclass(frozen=True)
class NativeSavedItemResult:
    item_id: str
    channel_id: str
    channel_name: str
    ts: str
    date_created: str
    date_due: str
    state: str


@dataclass(frozen=True)
class NativeUserGroupResult:
    id: str
    name: str
    handle: str
    description: str
    user_count: int
    is_external: bool
    date_create: str
    date_update: str
    users: str = ""


class SlackSessionClient:
    def __init__(
        self,
        *,
        xoxc_token: str,
        xoxd_token: str,
        user_agent: str,
        govslack: bool = False,
    ) -> None:
        self._base_url = f"https://{'slack-gov.com' if govslack else 'slack.com'}/api"
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=20.0, read=60.0, write=60.0, pool=20.0),
            headers={
                "Authorization": f"Bearer {xoxc_token}",
                "User-Agent": user_agent,
            },
            cookies={
                "d": quote(xoxd_token, safe="-._~%abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
                "d-s": str(int(time.time()) - 10),
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _post(self, method_name: str, *, data: dict[str, Any] | None = None) -> dict[str, Any]:
        response = await self._client.post(f"{self._base_url}/{method_name}", data=data)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"{method_name} returned a non-object response")
        if not payload.get("ok"):
            raise ValueError(f"{method_name} failed: {payload.get('error', 'unknown_error')}")
        return payload

    async def _get_bytes(self, url: str) -> bytes:
        response = await self._client.get(url)
        response.raise_for_status()
        return response.content

    async def _post_webclient(self, method_name: str, *, data: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "_x_mode": "online",
            "_x_sonic": "true",
            "_x_app_name": "client",
            **data,
        }
        return await self._post(method_name, data=payload)

    async def workspace_slug(self) -> str:
        payload = await self.auth_test()
        url = str(payload.get("url") or "").strip()
        match = re.match(r"https://([^.]+)\.", url)
        if match:
            return match.group(1)
        team = str(payload.get("team") or "").strip().lower().replace(" ", "-")
        return team or "workspace"

    async def auth_test(self) -> dict[str, Any]:
        return await self._post("auth.test")

    async def current_user_id(self) -> str:
        payload = await self.auth_test()
        return str(payload.get("user_id") or "")

    async def iter_users(self) -> list[dict[str, Any]]:
        members: list[dict[str, Any]] = []
        cursor = ""
        while True:
            payload = await self._post("users.list", data={"limit": "200", "cursor": cursor})
            page_members = payload.get("members") or []
            if isinstance(page_members, list):
                members.extend(member for member in page_members if isinstance(member, dict))
            cursor = _next_cursor(payload)
            if not cursor:
                return members

    async def list_im_channels(self) -> dict[str, str]:
        dm_by_user: dict[str, str] = {}
        cursor = ""
        while True:
            payload = await self._post(
                "conversations.list",
                data={"types": "im", "limit": "200", "cursor": cursor, "exclude_archived": "true"},
            )
            channels = payload.get("channels") or []
            if isinstance(channels, list):
                for channel in channels:
                    if not isinstance(channel, dict):
                        continue
                    user_id = str(channel.get("user") or "").strip()
                    channel_id = str(channel.get("id") or "").strip()
                    if user_id and channel_id:
                        dm_by_user[user_id] = channel_id
            cursor = _next_cursor(payload)
            if not cursor:
                return dm_by_user

    async def list_channels(
        self,
        *,
        channel_types: str,
        limit: int,
        only_joined: bool = False,
    ) -> list[NativeChannelResult]:
        results: list[NativeChannelResult] = []
        cursor = ""
        types = normalize_channel_types(channel_types)
        page_size = min(max(limit, 1), 200) if limit > 0 else 200

        while True:
            payload = await self._post(
                "conversations.list",
                data={
                    "types": types,
                    "limit": str(page_size),
                    "cursor": cursor,
                    "exclude_archived": "true",
                },
            )
            channels = payload.get("channels") or []
            if isinstance(channels, list):
                for channel in channels:
                    if not isinstance(channel, dict):
                        continue
                    if only_joined and not bool(channel.get("is_member")):
                        continue
                    results.append(map_channel(channel))
                    if limit > 0 and len(results) >= limit:
                        return results
            cursor = _next_cursor(payload)
            if not cursor:
                return results

    async def resolve_channel_id(self, raw_channel: str) -> str:
        channel = raw_channel.strip()
        if not channel:
            raise ValueError("channel_id is required")
        if re.match(r"^[CDG][A-Z0-9]+$", channel):
            return channel
        if channel.startswith("#"):
            needle = channel[1:].lower()
            channels = await self.list_channels(channel_types="public_channel,private_channel", limit=0)
            for candidate in channels:
                if candidate.name.lstrip("#").lower() == needle:
                    return candidate.channel_id
            raise ValueError(f"channel {channel!r} not found")
        if channel.startswith("@"):
            needle = channel[1:]
            if needle.endswith("_dm"):
                needle = needle[:-3]
            users = await self.iter_users()
            dm_by_user = await self.list_im_channels()
            for user in users:
                user_name = str(user.get("name") or "")
                if user_name.lower() != needle.lower():
                    continue
                user_id = str(user.get("id") or "")
                dm_channel_id = dm_by_user.get(user_id, "")
                if dm_channel_id:
                    return dm_channel_id
            raise ValueError(f"channel {channel!r} not found")
        return channel

    async def conversations_history(
        self,
        *,
        channel_id: str,
        limit: int,
        cursor: str = "",
        oldest: str = "",
        latest: str = "",
    ) -> list[dict[str, Any]]:
        payload = await self._post(
            "conversations.history",
            data={
                "channel": channel_id,
                "limit": str(limit),
                "cursor": cursor,
                "oldest": oldest,
                "latest": latest,
                "inclusive": "true",
            },
        )
        messages = payload.get("messages") or []
        return [message for message in messages if isinstance(message, dict)]

    async def search_messages(self, *, query: str, count: int, page: int) -> list[dict[str, Any]]:
        payload = await self._post(
            "search.messages",
            data={"query": query, "count": str(count), "page": str(page)},
        )
        messages_payload = payload.get("messages") or {}
        matches = messages_payload.get("matches") if isinstance(messages_payload, dict) else []
        return [message for message in matches or [] if isinstance(message, dict)]

    async def unread_summaries(
        self,
        *,
        channel_types: str,
        max_channels: int,
        include_muted: bool,
    ) -> list[NativeUnreadResult]:
        channels = await self.list_channels(channel_types=channel_types, limit=0)
        payload = await self._post(
            "conversations.list",
            data={"types": normalize_channel_types(channel_types), "limit": "200", "exclude_archived": "true"},
        )
        raw_channels = payload.get("channels") or []
        summary_by_id: dict[str, NativeUnreadResult] = {}
        for channel in raw_channels:
            if not isinstance(channel, dict):
                continue
            if not include_muted and bool(channel.get("is_muted")):
                continue
            unread_count = int(channel.get("unread_count_display") or channel.get("unread_count") or 0)
            if unread_count <= 0:
                continue
            channel_id = str(channel.get("id") or "")
            latest = str((channel.get("latest") or {}).get("ts") or "") if isinstance(channel.get("latest"), dict) else ""
            summary_by_id[channel_id] = NativeUnreadResult(
                channel_id=channel_id,
                channel_name=map_channel(channel).name,
                channel_type=channel_type_label(channel),
                unread_count=unread_count,
                last_read=str(channel.get("last_read") or ""),
                latest=latest,
            )
        ordered = [summary_by_id[channel.channel_id] for channel in channels if channel.channel_id in summary_by_id]
        if max_channels > 0:
            return ordered[:max_channels]
        return ordered

    async def saved_list(self, *, filter_name: str, limit: int, cursor: str = "") -> dict[str, Any]:
        return await self._post_webclient(
            "saved.list",
            data={
                "_x_reason": "saved-api/savedList",
                "filter": filter_name,
                "limit": str(limit),
                "cursor": cursor,
                "include_tombstones": "true",
            },
        )

    async def saved_update(
        self,
        *,
        item_id: str,
        ts: str,
        mark: str = "",
        date_due: int = 0,
    ) -> None:
        payload = {
            "_x_reason": "saved-api/updateSavedMessage",
            "item_type": "message",
            "item_id": item_id,
            "ts": ts,
        }
        if mark:
            payload["mark"] = mark
        if date_due:
            payload["date_due"] = str(date_due)
        await self._post_webclient("saved.update", data=payload)

    async def saved_clear_completed(self) -> None:
        await self._post_webclient(
            "saved.clearCompleted",
            data={"_x_reason": "manually_marked_all_completed"},
        )

    async def post_message(
        self,
        *,
        channel_id: str,
        text: str,
        thread_ts: str = "",
        content_type: str = "text/markdown",
        blocks: str = "",
    ) -> tuple[str, str]:
        payload: dict[str, Any] = {
            "channel": await self.resolve_channel_id(channel_id),
            "text": text,
            "unfurl_links": "false",
            "unfurl_media": "false",
        }
        if thread_ts:
            payload["thread_ts"] = thread_ts
        if blocks.strip():
            try:
                parsed = json.loads(blocks)
            except json.JSONDecodeError as exc:
                raise ValueError(f"blocks must be valid JSON: {exc}") from exc
            if not isinstance(parsed, list):
                raise ValueError("blocks must be a JSON array")
            payload["blocks"] = json.dumps(parsed, separators=(",", ":"))
        elif content_type == "text/plain":
            payload["mrkdwn"] = "false"
        elif content_type != "text/markdown":
            raise ValueError("content_type must be either 'text/plain' or 'text/markdown'")

        response = await self._post("chat.postMessage", data=payload)
        return str(response.get("channel") or payload["channel"]), str(response.get("ts") or "")

    async def mark_conversation(self, *, channel_id: str, ts: str = "") -> str:
        resolved_channel_id = await self.resolve_channel_id(channel_id)
        mark_ts = ts.strip()
        if not mark_ts:
            messages = await self.conversations_history(channel_id=resolved_channel_id, limit=1)
            if messages:
                mark_ts = str(messages[0].get("ts") or "")
        if not mark_ts:
            mark_ts = f"{int(time.time())}.000000"
        await self._post("conversations.mark", data={"channel": resolved_channel_id, "ts": mark_ts})
        return mark_ts

    async def add_reaction(self, *, channel_id: str, timestamp: str, emoji: str) -> str:
        resolved_channel_id = await self.resolve_channel_id(channel_id)
        name = emoji.strip().strip(":")
        if not name:
            raise ValueError("emoji is required")
        await self._post(
            "reactions.add",
            data={"channel": resolved_channel_id, "timestamp": timestamp.strip(), "name": name},
        )
        return resolved_channel_id

    async def remove_reaction(self, *, channel_id: str, timestamp: str, emoji: str) -> str:
        resolved_channel_id = await self.resolve_channel_id(channel_id)
        name = emoji.strip().strip(":")
        if not name:
            raise ValueError("emoji is required")
        await self._post(
            "reactions.remove",
            data={"channel": resolved_channel_id, "timestamp": timestamp.strip(), "name": name},
        )
        return resolved_channel_id

    async def join_conversation(self, *, channel_id: str) -> str:
        resolved_channel_id = await self.resolve_channel_id(channel_id)
        payload = await self._post("conversations.join", data={"channel": resolved_channel_id})
        channel = payload.get("channel") if isinstance(payload.get("channel"), dict) else {}
        return str(channel.get("id") or resolved_channel_id)

    async def leave_conversation(self, *, channel_id: str) -> str:
        resolved_channel_id = await self.resolve_channel_id(channel_id)
        await self._post("conversations.leave", data={"channel": resolved_channel_id})
        return resolved_channel_id

    async def file_info(self, *, file_id: str) -> dict[str, Any]:
        payload = await self._post("files.info", data={"file": file_id})
        file_info = payload.get("file")
        if not isinstance(file_info, dict):
            raise ValueError("files.info returned no file object")
        return file_info

    async def attachment_data(self, *, file_id: str, max_size_bytes: int = 5 * 1024 * 1024) -> dict[str, Any]:
        file_info = await self.file_info(file_id=file_id)
        size = int(file_info.get("size") or 0)
        if size > max_size_bytes:
            raise ValueError(
                f"file size {size} bytes exceeds maximum allowed size of {max_size_bytes} bytes"
            )
        download_url = str(file_info.get("url_private_download") or file_info.get("url_private") or "")
        if not download_url:
            raise ValueError("file has no downloadable URL")
        content = await self._get_bytes(download_url)
        mimetype = str(file_info.get("mimetype") or "")
        if is_text_mimetype(mimetype):
            encoding = "none"
            content_text = content.decode("utf-8", errors="replace")
        else:
            encoding = "base64"
            content_text = base64.b64encode(content).decode("ascii")
        return {
            "file_id": str(file_info.get("id") or file_id),
            "filename": str(file_info.get("name") or ""),
            "mimetype": mimetype,
            "size": len(content),
            "encoding": encoding,
            "content": content_text,
        }

    async def usergroups_list(
        self,
        *,
        include_users: bool = False,
        include_count: bool = True,
        include_disabled: bool = False,
    ) -> list[dict[str, Any]]:
        payload = await self._post(
            "usergroups.list",
            data={
                "include_users": str(include_users).lower(),
                "include_count": str(include_count).lower(),
                "include_disabled": str(include_disabled).lower(),
            },
        )
        groups = payload.get("usergroups") or []
        return [group for group in groups if isinstance(group, dict)]

    async def usergroups_create(
        self,
        *,
        name: str,
        handle: str = "",
        description: str = "",
        channels: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name}
        if handle:
            payload["handle"] = handle
        if description:
            payload["description"] = description
        if channels:
            payload["channels"] = channels
        response = await self._post("usergroups.create", data=payload)
        usergroup = response.get("usergroup")
        if not isinstance(usergroup, dict):
            raise ValueError("usergroups.create returned no usergroup object")
        return usergroup

    async def usergroups_update(
        self,
        *,
        usergroup_id: str,
        name: str = "",
        handle: str = "",
        description: str = "",
        channels: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"usergroup": usergroup_id}
        if name:
            payload["name"] = name
        if handle:
            payload["handle"] = handle
        if description:
            payload["description"] = description
        if channels:
            payload["channels"] = channels
        response = await self._post("usergroups.update", data=payload)
        usergroup = response.get("usergroup")
        if not isinstance(usergroup, dict):
            raise ValueError("usergroups.update returned no usergroup object")
        return usergroup

    async def usergroup_members(self, *, usergroup_id: str) -> list[str]:
        payload = await self._post("usergroups.users.list", data={"usergroup": usergroup_id})
        users = payload.get("users") or []
        return [str(user_id) for user_id in users if str(user_id)]

    async def usergroups_users_update(self, *, usergroup_id: str, users: str) -> dict[str, Any]:
        response = await self._post("usergroups.users.update", data={"usergroup": usergroup_id, "users": users})
        usergroup = response.get("usergroup")
        if not isinstance(usergroup, dict):
            raise ValueError("usergroups.users.update returned no usergroup object")
        return usergroup


def _next_cursor(payload: dict[str, Any]) -> str:
    response_metadata = payload.get("response_metadata") or {}
    if isinstance(response_metadata, dict):
        return str(response_metadata.get("next_cursor") or "")
    return ""


def normalize_channel_types(channel_types: str) -> str:
    cleaned = (channel_types or "").strip().lower()
    if not cleaned or cleaned == "all":
        return "public_channel,private_channel,im,mpim"
    return cleaned


def map_channel(channel: dict[str, Any]) -> NativeChannelResult:
    name = str(channel.get("name") or "").strip()
    is_im = bool(channel.get("is_im"))
    is_mpim = bool(channel.get("is_mpim"))
    if name and not is_im and not is_mpim and not name.startswith("#"):
        name = f"#{name}"
    if not name:
        if is_im:
            name = str(channel.get("user") or "direct-message").strip() or "direct-message"
        elif is_mpim:
            name = str(channel.get("name") or "group-dm").strip() or "group-dm"

    topic = ""
    if isinstance(channel.get("topic"), dict):
        topic = str(channel["topic"].get("value") or "")

    purpose = ""
    if isinstance(channel.get("purpose"), dict):
        purpose = str(channel["purpose"].get("value") or "")

    member_count = int(channel.get("num_members") or 0)
    return NativeChannelResult(
        channel_id=str(channel.get("id") or ""),
        name=name,
        topic=topic,
        purpose=purpose,
        member_count=member_count,
    )


def channel_type_label(channel: dict[str, Any]) -> str:
    if bool(channel.get("is_im")):
        return "dm"
    if bool(channel.get("is_mpim")):
        return "mpim"
    if bool(channel.get("is_private")):
        return "private_channel"
    return "public_channel"


def search_users(
    users: list[dict[str, Any]],
    dm_by_user: dict[str, str],
    *,
    query: str,
    limit: int,
) -> list[NativeUserSearchResult]:
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    results: list[NativeUserSearchResult] = []
    for user in users:
        if user.get("deleted"):
            continue

        profile = user.get("profile") if isinstance(user.get("profile"), dict) else {}
        user_name = str(user.get("name") or "")
        real_name = str(user.get("real_name") or "")
        display_name = str(profile.get("display_name") or "")
        email = str(profile.get("email") or "")

        if not any(pattern.search(value) for value in (user_name, real_name, display_name, email)):
            continue

        user_id = str(user.get("id") or "")
        results.append(
            NativeUserSearchResult(
                user_id=user_id,
                user_name=user_name,
                real_name=real_name,
                display_name=display_name,
                email=email,
                title=str(profile.get("title") or ""),
                dm_channel_id=dm_by_user.get(user_id, ""),
            )
        )
        if len(results) >= limit:
            return results
    return results


def _profile_lookup(users: list[dict[str, Any]]) -> dict[str, tuple[str, str]]:
    lookup: dict[str, tuple[str, str]] = {}
    for user in users:
        profile = user.get("profile") if isinstance(user.get("profile"), dict) else {}
        lookup[str(user.get("id") or "")] = (
            str(user.get("name") or ""),
            str(user.get("real_name") or profile.get("real_name") or ""),
        )
    return lookup


def _iso_timestamp(ts: str) -> str:
    try:
        return datetime.fromtimestamp(float(ts), UTC).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError):
        return ""


def _fmt_unix(ts: int | str | None) -> str:
    if ts in (None, "", 0, "0"):
        return ""
    try:
        return datetime.fromtimestamp(int(ts), UTC).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return ""


def _fmt_json_time(ts: int | str | None) -> str:
    if ts in (None, "", 0, "0"):
        return ""
    try:
        return datetime.fromtimestamp(int(ts), UTC).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError):
        return ""


def _reaction_summary(message: dict[str, Any]) -> str:
    reactions = message.get("reactions") or []
    parts: list[str] = []
    if isinstance(reactions, list):
        for reaction in reactions:
            if not isinstance(reaction, dict):
                continue
            name = str(reaction.get("name") or "")
            count = reaction.get("count")
            if name:
                parts.append(f":{name}:{f' x{count}' if count else ''}".strip())
    return ", ".join(parts)


def _attachment_ids(message: dict[str, Any]) -> str:
    files = message.get("files") or []
    ids = [str(file.get("id") or "") for file in files if isinstance(file, dict) and str(file.get("id") or "")]
    return ",".join(ids)


def map_history_messages(
    messages: list[dict[str, Any]],
    *,
    channel_id: str,
    users: list[dict[str, Any]],
) -> list[NativeMessageResult]:
    users_by_id = _profile_lookup(users)
    results: list[NativeMessageResult] = []
    for message in messages:
        user_id = str(message.get("user") or "")
        user_name, real_name = users_by_id.get(user_id, ("", ""))
        files = message.get("files") or []
        results.append(
            NativeMessageResult(
                msg_id=str(message.get("ts") or ""),
                user_id=user_id,
                user_name=user_name,
                real_name=real_name,
                channel=channel_id,
                thread_ts=str(message.get("thread_ts") or ""),
                text=str(message.get("text") or ""),
                timestamp=_iso_timestamp(str(message.get("ts") or "")),
                permalink=str(message.get("permalink") or ""),
                reactions=_reaction_summary(message),
                bot_name=str((message.get("bot_profile") or {}).get("name") or "") if isinstance(message.get("bot_profile"), dict) else "",
                file_count=len(files) if isinstance(files, list) else 0,
                attachment_ids=_attachment_ids(message),
                has_media=bool(files),
            )
        )
    return results


def map_search_messages(messages: list[dict[str, Any]]) -> list[NativeMessageResult]:
    results: list[NativeMessageResult] = []
    for message in messages:
        channel = message.get("channel") if isinstance(message.get("channel"), dict) else {}
        channel_id = str(channel.get("id") or "")
        channel_name = str(channel.get("name") or "")
        channel_label = channel_id
        if channel_id and channel_name:
            channel_label = f"{channel_id} (#{channel_name})"
        elif channel_name:
            channel_label = f"#{channel_name}"
        files = message.get("files") or []
        results.append(
            NativeMessageResult(
                msg_id=str(message.get("ts") or ""),
                user_id=str(message.get("user") or ""),
                user_name=str(message.get("username") or ""),
                real_name=str(message.get("username") or ""),
                channel=channel_label,
                thread_ts=str(message.get("thread_ts") or ""),
                text=str(message.get("text") or ""),
                timestamp=_iso_timestamp(str(message.get("ts") or "")),
                permalink=str(message.get("permalink") or ""),
                reactions=_reaction_summary(message),
                bot_name=str(message.get("bot_name") or ""),
                file_count=len(files) if isinstance(files, list) else 0,
                attachment_ids=_attachment_ids(message),
                has_media=bool(files),
            )
        )
    return results


def render_users_search_csv(results: list[NativeUserSearchResult]) -> str:
    if not results:
        return "No users found matching the query."

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["UserID", "UserName", "RealName", "DisplayName", "Email", "Title", "DMChannelID"])
    for result in results:
        writer.writerow(
            [
                result.user_id,
                result.user_name,
                result.real_name,
                result.display_name,
                result.email,
                result.title,
                result.dm_channel_id,
            ]
        )
    return buffer.getvalue().strip()


def render_channels_csv(results: list[NativeChannelResult]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["ID", "Name", "Topic", "Purpose", "MemberCount", "Cursor"])
    for result in results:
        writer.writerow(
            [
                result.channel_id,
                result.name,
                result.topic,
                result.purpose,
                str(result.member_count),
                result.cursor,
            ]
        )
    return buffer.getvalue().strip()


def render_messages_csv(results: list[NativeMessageResult]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "MsgID",
            "UserID",
            "UserName",
            "RealName",
            "Channel",
            "ThreadTs",
            "Text",
            "Time",
            "Permalink",
            "Reactions",
            "BotName",
            "FileCount",
            "AttachmentIDs",
            "HasMedia",
            "Cursor",
        ]
    )
    for result in results:
        writer.writerow(
            [
                result.msg_id,
                result.user_id,
                result.user_name,
                result.real_name,
                result.channel,
                result.thread_ts,
                result.text,
                result.timestamp,
                result.permalink,
                result.reactions,
                result.bot_name,
                str(result.file_count),
                result.attachment_ids,
                str(result.has_media).lower(),
                result.cursor,
            ]
        )
    return buffer.getvalue().strip()


def render_unreads_csv(results: list[NativeUnreadResult]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["ChannelID", "ChannelName", "ChannelType", "UnreadCount", "LastRead", "Latest"])
    for result in results:
        writer.writerow(
            [
                result.channel_id,
                result.channel_name,
                result.channel_type,
                str(result.unread_count),
                result.last_read,
                result.latest,
            ]
        )
    return buffer.getvalue().strip()


def map_saved_items(
    payload: dict[str, Any],
    *,
    channels_by_id: dict[str, NativeChannelResult],
) -> list[NativeSavedItemResult]:
    items = payload.get("saved_items") or []
    results: list[NativeSavedItemResult] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("item_id") or "")
        channel = channels_by_id.get(item_id)
        results.append(
            NativeSavedItemResult(
                item_id=item_id,
                channel_id=item_id,
                channel_name=channel.name if channel else item_id,
                ts=str(item.get("ts") or ""),
                date_created=_fmt_unix(item.get("date_created")),
                date_due=_fmt_unix(item.get("date_due")),
                state=str(item.get("state") or ""),
            )
        )
    return results


def render_saved_items_csv(results: list[NativeSavedItemResult]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["ItemID", "ChannelID", "ChannelName", "Ts", "DateCreated", "DateDue", "State"])
    for result in results:
        writer.writerow(
            [
                result.item_id,
                result.channel_id,
                result.channel_name,
                result.ts,
                result.date_created,
                result.date_due,
                result.state,
            ]
        )
    return buffer.getvalue().strip()


def render_users_resource_csv(users: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["UserID", "UserName", "RealName", "DisplayName", "Email", "Title"])
    for user in users:
        if user.get("deleted"):
            continue
        profile = user.get("profile") if isinstance(user.get("profile"), dict) else {}
        writer.writerow(
            [
                str(user.get("id") or ""),
                str(user.get("name") or ""),
                str(user.get("real_name") or ""),
                str(profile.get("display_name") or ""),
                str(profile.get("email") or ""),
                str(profile.get("title") or ""),
            ]
        )
    return buffer.getvalue().strip()


def map_usergroups(groups: list[dict[str, Any]]) -> list[NativeUserGroupResult]:
    results: list[NativeUserGroupResult] = []
    for group in groups:
        users = group.get("users") or []
        results.append(
            NativeUserGroupResult(
                id=str(group.get("id") or ""),
                name=str(group.get("name") or ""),
                handle=str(group.get("handle") or ""),
                description=str(group.get("description") or ""),
                user_count=int(group.get("user_count") or 0),
                is_external=bool(group.get("is_external")),
                date_create=_fmt_json_time(group.get("date_create")),
                date_update=_fmt_json_time(group.get("date_update")),
                users=",".join(str(user_id) for user_id in users if str(user_id)),
            )
        )
    return results


def render_usergroups_csv(results: list[NativeUserGroupResult]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        ["id", "name", "handle", "description", "user_count", "is_external", "date_create", "date_update"]
    )
    for result in results:
        writer.writerow(
            [
                result.id,
                result.name,
                result.handle,
                result.description,
                str(result.user_count),
                str(result.is_external).lower(),
                result.date_create,
                result.date_update,
            ]
        )
    return buffer.getvalue().strip()


def usergroup_result_json(group: dict[str, Any], *, include_users: bool = False) -> str:
    result = NativeUserGroupResult(
        id=str(group.get("id") or ""),
        name=str(group.get("name") or ""),
        handle=str(group.get("handle") or ""),
        description=str(group.get("description") or ""),
        user_count=int(group.get("user_count") or 0),
        is_external=bool(group.get("is_external")),
        date_create=_fmt_json_time(group.get("date_create")),
        date_update=_fmt_json_time(group.get("date_update")),
        users=",".join(str(user_id) for user_id in (group.get("users") or []) if str(user_id)),
    )
    payload = asdict(result)
    if not include_users:
        payload.pop("users", None)
    return json.dumps(payload, separators=(",", ":"))


def usergroup_membership_result_json(*, message: str, group_id: str, group_name: str, user_count: int) -> str:
    return json.dumps(
        {
            "message": message,
            "group_id": group_id,
            "group_name": group_name,
            "user_count": user_count,
        },
        separators=(",", ":"),
    )


def is_text_mimetype(mimetype: str) -> bool:
    if mimetype.startswith("text/"):
        return True
    return mimetype in {
        "application/json",
        "application/xml",
        "application/javascript",
        "application/x-yaml",
        "application/x-sh",
    }
