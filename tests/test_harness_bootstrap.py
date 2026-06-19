from __future__ import annotations

import unittest

from fastmcp import Client

from tests.harness.base import LiveHarnessTestCase
from tests.harness.contract import EXPECTED_LIVE_RUNTIME_TOOLS, EXPECTED_RESOURCE_URI_SUFFIXES


class HarnessBootstrapTests(LiveHarnessTestCase):
    def test_doctor_snapshot_captures_native_runtime_selection(self) -> None:
        snapshot = self.runtime.doctor_snapshot
        self.assertIsNotNone(snapshot)
        assert snapshot is not None
        self.assertEqual(snapshot.fields["backend_mode"], "native")
        self.assertEqual(snapshot.fields["backend_command"], "")
        self.assertEqual(snapshot.fields["configured_enabled_tools"], "all")
        self.assertEqual(snapshot.fields["transport"], "streamable-http")
        self.assertEqual(snapshot.fields["api_key_auth_configured"], "no")

    def test_health_endpoint_reports_expected_native_bootstrap_state(self) -> None:
        payload = self.runtime.health_payload()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["server"], "slack-mcp")
        self.assertEqual(payload["implementation"], "fastmcp-python-native")
        self.assertEqual(payload["backendMode"], "native")
        self.assertIsNone(payload["backendCommand"])
        self.assertEqual(payload["mcpAuthMode"], "disabled")
        self.assertEqual(payload["configuredEnabledTools"], "all")
        self.assertEqual(payload["effectiveEnabledTools"], "all")
        self.assertFalse(payload["apiKeyAuthConfigured"])
        self.assertSetEqual(set(payload["pythonNativeTools"]), EXPECTED_LIVE_RUNTIME_TOOLS)
        self.assertEqual(payload["pythonNativeResources"], ["channels", "users"])

    async def test_client_can_ping_and_discover_mcp_surface(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            self.assertTrue(await client.ping())

            tools = await client.list_tools()
            resources = await client.list_resources()

        self.assertGreater(len(tools), 0)
        self.assertGreater(len(resources), 0)

    async def test_live_runtime_exposes_exact_22_tool_surface(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            tools = await client.list_tools()

        observed_tool_names = {tool.name for tool in tools}
        self.assertSetEqual(observed_tool_names, EXPECTED_LIVE_RUNTIME_TOOLS)
        self.assertEqual(len(observed_tool_names), 22)

    async def test_live_runtime_exposes_expected_resource_surface(self) -> None:
        async with Client(self.runtime.mcp_url, timeout=30) as client:
            resources = await client.list_resources()

        observed_uris = {str(resource.uri) for resource in resources}
        observed_suffixes = {
            uri[len("slack://") + uri[len("slack://") :].find("/") :]
            for uri in observed_uris
            if uri.startswith("slack://") and "/" in uri[len("slack://") :]
        }

        self.assertSetEqual(observed_suffixes, EXPECTED_RESOURCE_URI_SUFFIXES)
        self.assertEqual(len(observed_uris), 2)
        for uri in observed_uris:
            self.assertTrue(uri.startswith("slack://"))
