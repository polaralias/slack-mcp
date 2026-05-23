from __future__ import annotations

import unittest

from fastmcp import Client

from tests.harness.base import LiveHarnessTestCase
from tests.harness.contract import EXPECTED_LIVE_RUNTIME_TOOLS
from tests.harness.discovery import (
    choose_history_channel_id,
    choose_search_query,
    choose_thread_ts,
    choose_user_query,
    discover_channels,
    discover_history_rows,
    discover_users_resource_rows,
)
from tests.harness.normalize import (
    resource_contents_have_payload,
    resource_contents_text,
    tool_result_is_error,
    tool_result_has_payload,
    tool_result_text,
)
from tests.harness.runtime import HarnessRuntime
from tests.harness.tools import required_tool_args, tools_by_name


class StableReadPathTests(LiveHarnessTestCase):
    async def _history_channel_id(self, client: Client) -> str:
        configured = self._optional_env("HISTORY_CHANNEL_ID")
        if configured:
            return configured
        channels = await discover_channels(client)
        channel_id = choose_history_channel_id(channels)
        if channel_id is None:
            raise unittest.SkipTest("Could not auto-discover a stable public channel for history tests")
        return channel_id

    async def _replies_target(self, client: Client) -> tuple[str, str]:
        configured_channel = self._optional_env("REPLIES_CHANNEL_ID")
        configured_thread = self._optional_env("REPLIES_THREAD_TS")
        if configured_channel and configured_thread:
            return configured_channel, configured_thread

        channel_id = configured_channel or await self._history_channel_id(client)
        history_rows = await discover_history_rows(client, channel_id)
        thread_ts = configured_thread or choose_thread_ts(history_rows)
        if thread_ts is None:
            raise unittest.SkipTest("Could not auto-discover a thread timestamp for replies tests")
        return channel_id, thread_ts

    async def _search_query(self, client: Client) -> str:
        configured = self._optional_env("SEARCH_QUERY")
        if configured:
            return configured
        channel_id = await self._history_channel_id(client)
        history_rows = await discover_history_rows(client, channel_id)
        search_query = choose_search_query(history_rows)
        if search_query is None:
            raise unittest.SkipTest("Could not auto-discover a stable search query")
        return search_query

    async def _users_search_query(self, client: Client) -> str:
        configured = self._optional_env("USERS_SEARCH_QUERY")
        if configured:
            return configured
        user_rows = await discover_users_resource_rows(client)
        query = choose_user_query(user_rows)
        if query is None:
            raise unittest.SkipTest("Could not auto-discover a stable users_search query")
        return query

    @staticmethod
    def _optional_env(name: str) -> str | None:
        import os

        value = os.getenv(f"SLACK_MCP_HARNESS_{name}", "").strip()
        return value or None

    async def test_channels_list_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            result = await client.call_tool(
                "channels_list",
                {"channel_types": "public_channel,private_channel,im,mpim", "limit": 20},
            )

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_channels_me_returns_payload_when_no_required_args(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            tool = (await tools_by_name(client))["channels_me"]
            required_args = required_tool_args(tool)
            if required_args:
                raise unittest.SkipTest(
                    "channels_me requires arguments in the live runtime; update the harness "
                    f"with explicit fixtures for: {', '.join(required_args)}"
                )
            result = await client.call_tool("channels_me", {})

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_users_search_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            query = await self._users_search_query(client)
            result = await client.call_tool("users_search", {"query": query, "limit": 10})

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_runtime_can_limit_tool_surface_while_remaining_native(self) -> None:
        runtime = HarnessRuntime(
            enabled_tools="channels_list,channels_me,users_search",
        ).start()
        try:
            doctor = runtime.doctor_snapshot
            self.assertIsNotNone(doctor)
            assert doctor is not None
            self.assertEqual(doctor.fields.get("backend_mode"), "native")
            self.assertEqual(doctor.fields.get("backend_command"), "")
            self.assertEqual(doctor.fields.get("python_native_tools"), "channels_list,channels_me,users_search")
            self.assertEqual(doctor.fields.get("python_native_resources"), "channels,users")

            health = runtime.health_payload()
            self.assertEqual(health.get("backendMode"), "native")
            self.assertEqual(health.get("pythonNativeTools"), ["channels_list", "channels_me", "users_search"])
            self.assertEqual(health.get("pythonNativeResources"), ["channels", "users"])

            async with Client(runtime.mcp_url, timeout=30) as client:
                tool_names = {tool.name for tool in await client.list_tools()}
                self.assertSetEqual(tool_names, {"channels_list", "channels_me", "users_search"})

                resources = await client.list_resources()
                resource_uris = {str(resource.uri) for resource in resources}
                self.assertEqual(len(resource_uris), 2)
                self.assertTrue(any(uri.endswith("/channels") for uri in resource_uris))
                self.assertTrue(any(uri.endswith("/users") for uri in resource_uris))

                channel_result = await client.call_tool(
                    "channels_list",
                    {"channel_types": "public_channel,private_channel,im,mpim", "limit": 10},
                )
                me_result = await client.call_tool("channels_me", {})
                query = await self._users_search_query(client)
                user_result = await client.call_tool("users_search", {"query": query, "limit": 10})

            self.assertFalse(tool_result_is_error(channel_result), tool_result_text(channel_result))
            self.assertTrue(tool_result_has_payload(channel_result))
            self.assertFalse(tool_result_is_error(me_result), tool_result_text(me_result))
            self.assertTrue(tool_result_has_payload(me_result))
            self.assertFalse(tool_result_is_error(user_result), tool_result_text(user_result))
            self.assertTrue(tool_result_has_payload(user_result))
        finally:
            runtime.stop()

    async def test_runtime_can_limit_to_conversation_read_slice_while_remaining_native(self) -> None:
        runtime = HarnessRuntime(
            enabled_tools="channels_list,channels_me,users_search,conversations_history,conversations_replies,conversations_search_messages,conversations_unreads",
        ).start()
        try:
            doctor = runtime.doctor_snapshot
            self.assertIsNotNone(doctor)
            assert doctor is not None
            self.assertEqual(
                doctor.fields.get("python_native_tools"),
                "channels_list,channels_me,conversations_history,conversations_replies,conversations_search_messages,conversations_unreads,users_search",
            )

            async with Client(runtime.mcp_url, timeout=30) as client:
                tool_names = {tool.name for tool in await client.list_tools()}
                self.assertSetEqual(
                    tool_names,
                    {
                        "channels_list",
                        "channels_me",
                        "conversations_history",
                        "conversations_replies",
                        "conversations_search_messages",
                        "conversations_unreads",
                        "users_search",
                    },
                )

                channel_id = await self._history_channel_id(client)
                history_result = await client.call_tool(
                    "conversations_history",
                    {"channel_id": channel_id, "limit": "20"},
                )
                replies_channel_id, thread_ts = await self._replies_target(client)
                replies_result = await client.call_tool(
                    "conversations_replies",
                    {"channel_id": replies_channel_id, "thread_ts": thread_ts, "limit": "20"},
                )
                search_query = await self._search_query(client)
                search_result = await client.call_tool(
                    "conversations_search_messages",
                    {"search_query": search_query, "limit": 10},
                )
                unreads_result = await client.call_tool(
                    "conversations_unreads",
                    {"include_messages": False, "channel_types": "all", "max_channels": 20},
                )

            self.assertFalse(tool_result_is_error(history_result), tool_result_text(history_result))
            self.assertTrue(tool_result_has_payload(history_result))
            self.assertFalse(tool_result_is_error(replies_result), tool_result_text(replies_result))
            self.assertTrue(tool_result_has_payload(replies_result))
            self.assertFalse(tool_result_is_error(search_result), tool_result_text(search_result))
            self.assertTrue(tool_result_has_payload(search_result))
            self.assertFalse(tool_result_is_error(unreads_result), tool_result_text(unreads_result))
            self.assertTrue(tool_result_has_payload(unreads_result))
        finally:
            runtime.stop()

    async def test_native_runtime_exposes_full_validated_surface_by_default(self) -> None:
        runtime = HarnessRuntime(enabled_tools="all").start()
        try:
            doctor = runtime.doctor_snapshot
            self.assertIsNotNone(doctor)
            assert doctor is not None
            self.assertEqual(doctor.fields.get("backend_mode"), "native")
            self.assertEqual(doctor.fields.get("backend_command"), "")
            self.assertEqual(
                set(filter(None, (doctor.fields.get("python_native_tools") or "").split(","))),
                EXPECTED_LIVE_RUNTIME_TOOLS,
            )
            self.assertEqual(doctor.fields.get("python_native_resources"), "channels,users")

            health = runtime.health_payload()
            self.assertEqual(health.get("backendMode"), "native")
            self.assertEqual(set(health.get("pythonNativeTools") or []), EXPECTED_LIVE_RUNTIME_TOOLS)
            self.assertEqual(health.get("pythonNativeResources"), ["channels", "users"])

            async with Client(runtime.mcp_url, timeout=30) as client:
                tool_names = {tool.name for tool in await client.list_tools()}
                self.assertSetEqual(tool_names, EXPECTED_LIVE_RUNTIME_TOOLS)
        finally:
            runtime.stop()

    async def test_conversations_history_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            channel_id = await self._history_channel_id(client)
            result = await client.call_tool(
                "conversations_history",
                {"channel_id": channel_id, "limit": "20"},
            )

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_conversations_replies_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            channel_id, thread_ts = await self._replies_target(client)
            result = await client.call_tool(
                "conversations_replies",
                {"channel_id": channel_id, "thread_ts": thread_ts, "limit": "20"},
            )

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_conversations_search_messages_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            search_query = await self._search_query(client)
            result = await client.call_tool(
                "conversations_search_messages",
                {"search_query": search_query, "limit": 10},
            )

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_conversations_unreads_summary_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            result = await client.call_tool(
                "conversations_unreads",
                {"include_messages": False, "channel_types": "all", "max_channels": 20},
            )

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_usergroups_list_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            result = await client.call_tool(
                "usergroups_list",
                {"include_users": False, "include_count": True, "include_disabled": False},
            )

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_usergroups_me_list_returns_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            result = await client.call_tool("usergroups_me", {"action": "list"})

        self.assertFalse(tool_result_is_error(result), tool_result_text(result))
        self.assertTrue(tool_result_has_payload(result))

    async def test_resources_return_text_csv_payload(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            resources = await client.list_resources()

            for resource in resources:
                contents = await client.read_resource(str(resource.uri))
                self.assertTrue(resource_contents_have_payload(contents))
                self.assertEqual(getattr(resource, "mimeType", None), "text/csv")
                self.assertIn(",", resource_contents_text(contents))
