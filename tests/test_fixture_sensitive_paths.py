from __future__ import annotations

import asyncio
import base64
import json
import os
import time

from fastmcp import Client
from slack_native import SlackSessionClient

from tests.harness.base import LiveHarnessTestCase
from tests.harness.discovery import (
    choose_history_channel_id,
    csv_rows,
    discover_channels,
    discover_history_rows,
)
from tests.harness.normalize import tool_result_has_payload, tool_result_is_error, tool_result_text
from tests.harness.runtime import HarnessRuntime


class FixtureSensitivePathTests(LiveHarnessTestCase):
    async def _joinable_public_channel_id(self, client: Client) -> str | None:
        all_channels = await discover_channels(client)
        joined_rows = csv_rows(tool_result_text(await client.call_tool("channels_me", {"limit": 50})))
        joined_ids = {row.get("ID", "") for row in joined_rows}
        preferred_names = {"#new-channel"}
        for row in all_channels:
            channel_id = row.get("ID", "")
            name = row.get("Name", "")
            if channel_id.startswith("C") and channel_id not in joined_ids and name in preferred_names:
                return channel_id
        for row in all_channels:
            channel_id = row.get("ID", "")
            name = row.get("Name", "")
            if channel_id.startswith("C") and channel_id not in joined_ids and name != "#general":
                return channel_id
        return None

    async def test_harness_upload_text_file_enables_attachment_success_path(self) -> None:
        runtime = HarnessRuntime(enable_harness_upload_tool=True).start()
        try:
            async with Client(runtime.mcp_url, timeout=60) as client:
                upload_result = await client.call_tool(
                    "harness_upload_text_file",
                    {
                        "filename": "codex-harness-upload.txt",
                        "content": "codex attachment fixture content",
                    },
                )

                self.assertFalse(tool_result_is_error(upload_result), tool_result_text(upload_result))
                upload_payload = (
                    getattr(upload_result, "structured_content", None)
                    or getattr(upload_result, "structuredContent", None)
                    or {}
                )
                self.assertEqual(upload_payload.get("ok"), True)
                file_id = upload_payload.get("file_id")
                self.assertTrue(isinstance(file_id, str) and file_id.startswith("F"))

                attachment_result = await client.call_tool("attachment_get_data", {"file_id": file_id})

            self.assertFalse(tool_result_is_error(attachment_result), tool_result_text(attachment_result))
            attachment_payload = json.loads(tool_result_text(attachment_result))
            self.assertEqual(attachment_payload["file_id"], file_id)
            if attachment_payload["encoding"] == "none":
                downloaded_content = attachment_payload["content"]
            else:
                downloaded_content = base64.b64decode(attachment_payload["content"]).decode("utf-8")
            self.assertIn("codex attachment fixture content", downloaded_content)
        finally:
            runtime.stop()

    async def test_saved_list_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            result = await client.call_tool("saved_list", {})

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_harness_save_message_for_later_closes_saved_item_success_paths(self) -> None:
        runtime = HarnessRuntime(enable_harness_saved_tool=True).start()
        try:
            async with Client(runtime.mcp_url, timeout=60) as client:
                channels = await discover_channels(client)
                channel_id = choose_history_channel_id(channels)
                self.assertTrue(channel_id, "No suitable public channel was available for saved-item validation")

                marker = f"saved-fixture-{int(time.time())}"
                post_result = await client.call_tool(
                    "conversations_add_message",
                    {"channel_id": channel_id, "text": marker},
                )
                self.assertFalse(tool_result_is_error(post_result), tool_result_text(post_result))

                target_row = None
                for _ in range(5):
                    history_rows = await discover_history_rows(client, channel_id, limit="10")
                    target_row = next((row for row in history_rows if row.get("Text") == marker), None)
                    if target_row is not None:
                        break
                    await asyncio.sleep(1)

                self.assertIsNotNone(target_row, "Newly posted saved-item fixture message was not found in history")
                ts = str(target_row["MsgID"])

                save_result = await client.call_tool(
                    "harness_save_message_for_later",
                    {"channel_id": channel_id, "ts": ts},
                )
                self.assertFalse(tool_result_is_error(save_result), tool_result_text(save_result))
                save_payload = (
                    getattr(save_result, "structured_content", None)
                    or getattr(save_result, "structuredContent", None)
                    or {}
                )
                self.assertEqual(save_payload.get("ok"), True)

                archived_rows = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "archived", "include_messages": False})
                    )
                )
                self.assertTrue(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in archived_rows),
                    "Saved fixture message was not listed in archived saved items after harness save",
                )

                due_date = int(time.time()) + 86400
                update_result = await client.call_tool(
                    "saved_update",
                    {"item_id": channel_id, "ts": ts, "date_due": due_date},
                )
                self.assertFalse(tool_result_is_error(update_result), tool_result_text(update_result))

                active_rows = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "saved", "include_messages": False})
                    )
                )
                self.assertTrue(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in active_rows),
                    "Saved fixture message was not listed in active saved items after due-date update",
                )

                complete_result = await client.call_tool(
                    "saved_update",
                    {"item_id": channel_id, "ts": ts, "mark": "completed"},
                )
                self.assertFalse(tool_result_is_error(complete_result), tool_result_text(complete_result))

                completed_rows = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "completed", "include_messages": False})
                    )
                )
                self.assertTrue(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in completed_rows),
                    "Saved fixture message was not listed in completed saved items after mark=completed",
                )

                clear_result = await client.call_tool("saved_clear_completed", {})
                self.assertFalse(tool_result_is_error(clear_result), tool_result_text(clear_result))

                completed_rows_after_clear = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "completed", "include_messages": False})
                    )
                )
                self.assertFalse(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in completed_rows_after_clear),
                    "Completed saved fixture message remained after saved_clear_completed",
                )
        finally:
            runtime.stop()

    async def test_native_runtime_supports_saved_tools(self) -> None:
        runtime = HarnessRuntime(
            enabled_tools="channels_list,conversations_history,saved_list,saved_update,saved_clear_completed",
        ).start()
        try:
            async with Client(runtime.mcp_url, timeout=60) as client:
                channels = await discover_channels(client)
                channel_id = choose_history_channel_id(channels)
                self.assertTrue(channel_id, "No suitable public channel was available for native saved-item validation")

                history_rows = await discover_history_rows(client, channel_id, limit="20")
                self.assertTrue(history_rows, "No history rows were available for native saved-item validation")

                ts = None
                native_fixture_client = SlackSessionClient(
                    xoxc_token=os.environ["SLACK_MCP_XOXC_TOKEN"],
                    xoxd_token=os.environ["SLACK_MCP_XOXD_TOKEN"],
                    user_agent="slack-mcp-native-test/1.0",
                )
                try:
                    for row in history_rows:
                        candidate_ts = str(row["MsgID"])
                        try:
                            await native_fixture_client._post("stars.add", data={"channel": channel_id, "timestamp": candidate_ts})
                            ts = candidate_ts
                            break
                        except ValueError as exc:
                            if "already_starred" not in str(exc):
                                raise
                finally:
                    await native_fixture_client.aclose()
                self.assertIsNotNone(ts, "Could not find an unsaved history message for native saved-item validation")
                assert ts is not None

                archived_rows = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "archived", "include_messages": False})
                    )
                )
                self.assertTrue(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in archived_rows),
                    "Native saved_list did not return the archived saved fixture",
                )

                due_date = int(time.time()) + 86400
                update_result = await client.call_tool(
                    "saved_update",
                    {"item_id": channel_id, "ts": ts, "date_due": due_date},
                )
                self.assertFalse(tool_result_is_error(update_result), tool_result_text(update_result))

                active_rows = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "saved", "include_messages": False})
                    )
                )
                self.assertTrue(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in active_rows),
                    "Native saved_list did not return the active saved fixture after due-date update",
                )

                complete_result = await client.call_tool(
                    "saved_update",
                    {"item_id": channel_id, "ts": ts, "mark": "completed"},
                )
                self.assertFalse(tool_result_is_error(complete_result), tool_result_text(complete_result))

                completed_rows = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "completed", "include_messages": False})
                    )
                )
                self.assertTrue(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in completed_rows),
                    "Native saved_list did not return the completed saved fixture after mark=completed",
                )

                clear_result = await client.call_tool("saved_clear_completed", {})
                self.assertFalse(tool_result_is_error(clear_result), tool_result_text(clear_result))

                completed_rows_after_clear = csv_rows(
                    tool_result_text(
                        await client.call_tool("saved_list", {"filter": "completed", "include_messages": False})
                    )
                )
                self.assertFalse(
                    any(row.get("ItemID") == channel_id and row.get("Ts") == ts for row in completed_rows_after_clear),
                    "Native saved fixture remained after saved_clear_completed",
                )
        finally:
            runtime.stop()

    async def test_native_runtime_supports_write_and_attachment_tools(self) -> None:
        runtime = HarnessRuntime(
            enabled_tools="all",
            enable_harness_upload_tool=True,
        ).start()
        try:
            async with Client(runtime.mcp_url, timeout=60) as client:
                channels = await discover_channels(client)
                channel_id = choose_history_channel_id(channels)
                self.assertTrue(channel_id, "No suitable public channel was available for native write validation")

                marker = f"native-write-{int(time.time())}"
                post_result = await client.call_tool(
                    "conversations_add_message",
                    {"channel_id": channel_id, "text": marker},
                )
                self.assertFalse(tool_result_is_error(post_result), tool_result_text(post_result))

                target_row = None
                for _ in range(5):
                    history_rows = await discover_history_rows(client, channel_id, limit="10")
                    target_row = next((row for row in history_rows if row.get("Text") == marker), None)
                    if target_row is not None:
                        break
                    await asyncio.sleep(1)
                self.assertIsNotNone(target_row, "Native add-message fixture was not found in history")
                assert target_row is not None

                ts = str(target_row["MsgID"])

                mark_result = await client.call_tool("conversations_mark", {"channel_id": channel_id, "ts": ts})
                self.assertFalse(tool_result_is_error(mark_result), tool_result_text(mark_result))

                add_reaction_result = await client.call_tool(
                    "reactions_add",
                    {"channel_id": channel_id, "timestamp": ts, "emoji": "rocket"},
                )
                self.assertFalse(tool_result_is_error(add_reaction_result), tool_result_text(add_reaction_result))

                history_with_reaction = await discover_history_rows(client, channel_id, limit="10")
                reacted_row = next((row for row in history_with_reaction if row.get("MsgID") == ts), None)
                self.assertIsNotNone(reacted_row, "Reaction fixture message disappeared from history")
                self.assertIn(":rocket:", reacted_row.get("Reactions", ""))

                remove_reaction_result = await client.call_tool(
                    "reactions_remove",
                    {"channel_id": channel_id, "timestamp": ts, "emoji": "rocket"},
                )
                self.assertFalse(tool_result_is_error(remove_reaction_result), tool_result_text(remove_reaction_result))

                joinable_channel_id = await self._joinable_public_channel_id(client)
                if joinable_channel_id:
                    join_result = await client.call_tool("conversations_join", {"channel_id": joinable_channel_id})
                    self.assertFalse(tool_result_is_error(join_result), tool_result_text(join_result))
                    leave_result = await client.call_tool("conversations_leave", {"channel_id": joinable_channel_id})
                    self.assertFalse(tool_result_is_error(leave_result), tool_result_text(leave_result))

                upload_result = await client.call_tool(
                    "harness_upload_text_file",
                    {
                        "filename": "codex-native-upload.txt",
                        "content": "codex native attachment fixture",
                    },
                )
                self.assertFalse(tool_result_is_error(upload_result), tool_result_text(upload_result))
                upload_payload = (
                    getattr(upload_result, "structured_content", None)
                    or getattr(upload_result, "structuredContent", None)
                    or {}
                )
                file_id = str(upload_payload.get("file_id") or "")
                self.assertTrue(file_id.startswith("F"))

                attachment_result = await client.call_tool("attachment_get_data", {"file_id": file_id})
                self.assertFalse(tool_result_is_error(attachment_result), tool_result_text(attachment_result))
                attachment_payload = json.loads(tool_result_text(attachment_result))
                if attachment_payload["encoding"] == "none":
                    downloaded_content = attachment_payload["content"]
                else:
                    downloaded_content = base64.b64decode(attachment_payload["content"]).decode("utf-8")
                self.assertIn("codex native attachment fixture", downloaded_content)
        finally:
            runtime.stop()

    async def test_native_runtime_supports_usergroups_tools(self) -> None:
        runtime = HarnessRuntime(enabled_tools="all").start()
        try:
            async with Client(runtime.mcp_url, timeout=60) as client:
                token = f"native-group-{int(time.time())}"
                create_result = await client.call_tool(
                    "usergroups_create",
                    {
                        "name": token,
                        "handle": token.replace("-", "")[:21],
                        "description": "native usergroups fixture",
                    },
                )
                self.assertFalse(tool_result_is_error(create_result), tool_result_text(create_result))
                created_group = json.loads(tool_result_text(create_result))
                usergroup_id = str(created_group["id"])

                list_result = await client.call_tool(
                    "usergroups_list",
                    {"include_users": False, "include_count": True, "include_disabled": False},
                )
                self.assertFalse(tool_result_is_error(list_result), tool_result_text(list_result))
                listed_groups = csv_rows(tool_result_text(list_result))
                self.assertTrue(any(row.get("id") == usergroup_id for row in listed_groups))

                join_result = await client.call_tool("usergroups_me", {"action": "join", "usergroup_id": usergroup_id})
                self.assertFalse(tool_result_is_error(join_result), tool_result_text(join_result))
                join_payload = json.loads(tool_result_text(join_result))
                self.assertEqual(join_payload["group_id"], usergroup_id)

                me_list_result = await client.call_tool("usergroups_me", {"action": "list"})
                self.assertFalse(tool_result_is_error(me_list_result), tool_result_text(me_list_result))
                my_groups = csv_rows(tool_result_text(me_list_result))
                self.assertTrue(any(row.get("id") == usergroup_id for row in my_groups))

                update_result = await client.call_tool(
                    "usergroups_update",
                    {
                        "usergroup_id": usergroup_id,
                        "description": "native usergroups fixture updated",
                    },
                )
                self.assertFalse(tool_result_is_error(update_result), tool_result_text(update_result))
                updated_group = json.loads(tool_result_text(update_result))
                self.assertEqual(updated_group["id"], usergroup_id)
                self.assertEqual(updated_group["description"], "native usergroups fixture updated")

                current_user_id = ""
                native_fixture_client = SlackSessionClient(
                    xoxc_token=os.environ["SLACK_MCP_XOXC_TOKEN"],
                    xoxd_token=os.environ["SLACK_MCP_XOXD_TOKEN"],
                    user_agent="slack-mcp-native-test/1.0",
                )
                try:
                    current_user_id = await native_fixture_client.current_user_id()
                    users = await native_fixture_client.iter_users()
                finally:
                    await native_fixture_client.aclose()
                self.assertTrue(current_user_id.startswith(("U", "W")))

                alternate_user_id = next(
                    (
                        str(user.get("id") or "")
                        for user in users
                        if str(user.get("id") or "")
                        and str(user.get("id") or "") != current_user_id
                        and not bool(user.get("deleted"))
                        and not bool(user.get("is_bot"))
                    ),
                    "",
                )

                members_update_result = await client.call_tool(
                    "usergroups_users_update",
                    {
                        "usergroup_id": usergroup_id,
                        "users": ",".join(filter(None, [current_user_id, alternate_user_id])),
                    },
                )
                self.assertFalse(tool_result_is_error(members_update_result), tool_result_text(members_update_result))
                members_updated_group = json.loads(tool_result_text(members_update_result))
                self.assertEqual(members_updated_group["id"], usergroup_id)
                if alternate_user_id:
                    self.assertEqual(
                        set(str(members_updated_group.get("users") or "").split(",")),
                        {current_user_id, alternate_user_id},
                    )

                    leave_result = await client.call_tool(
                        "usergroups_me",
                        {"action": "leave", "usergroup_id": usergroup_id},
                    )
                    self.assertFalse(tool_result_is_error(leave_result), tool_result_text(leave_result))
                    leave_payload = json.loads(tool_result_text(leave_result))
                    self.assertEqual(leave_payload["group_id"], usergroup_id)
        finally:
            runtime.stop()
