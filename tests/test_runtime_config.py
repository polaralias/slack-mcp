from __future__ import annotations

import importlib
import os
import sys
import unittest
from unittest.mock import patch

from backend_runtime import (
    DEFAULT_ENABLED_TOOLS,
    configured_enabled_tools,
    effective_enabled_tools,
    validate_auth_environment,
)


class RuntimeConfigTests(unittest.TestCase):
    def test_default_enabled_tools_matches_validated_surface(self) -> None:
        self.assertEqual(len(DEFAULT_ENABLED_TOOLS), 22)
        self.assertEqual(len(set(DEFAULT_ENABLED_TOOLS)), 22)

    def test_effective_enabled_tools_defaults_to_full_surface(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SLACK_MCP_ENABLED_TOOLS", None)
            self.assertEqual(configured_enabled_tools(), None)
            self.assertEqual(effective_enabled_tools(), DEFAULT_ENABLED_TOOLS)

    def test_configured_enabled_tools_parses_csv_allowlist(self) -> None:
        with patch.dict(os.environ, {"SLACK_MCP_ENABLED_TOOLS": "channels_list, users_search"}, clear=False):
            self.assertEqual(configured_enabled_tools(), ["channels_list", "users_search"])
            self.assertEqual(effective_enabled_tools(), ["channels_list", "users_search"])

    def test_validate_auth_environment_requires_browser_session_pair(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as exc:
                validate_auth_environment()
        self.assertIn("SLACK_MCP_XOXC_TOKEN", str(exc.exception))
        self.assertIn("SLACK_MCP_XOXD_TOKEN", str(exc.exception))

    def test_validate_auth_environment_rejects_legacy_auth_vars(self) -> None:
        with patch.dict(
            os.environ,
            {
                "SLACK_MCP_XOXC_TOKEN": "browser-session-test",
                "SLACK_MCP_XOXD_TOKEN": "cookie-test",
                "SLACK_MCP_XOXP_TOKEN": "legacy-token-test",
            },
            clear=True,
        ):
            with self.assertRaises(SystemExit) as exc:
                validate_auth_environment()
        self.assertIn("SLACK_MCP_XOXP_TOKEN", str(exc.exception))

    def test_server_import_requires_explicit_api_key_or_disabled_mode(self) -> None:
        sys.modules.pop("server", None)
        with patch.dict(
            os.environ,
            {
                "SLACK_MCP_XOXC_TOKEN": "browser-session-test",
                "SLACK_MCP_XOXD_TOKEN": "cookie-test",
            },
            clear=True,
        ):
            with self.assertRaises(RuntimeError) as exc:
                importlib.import_module("server")

        self.assertIn("SLACK_MCP_API_KEY", str(exc.exception))
        self.assertIn("API_KEY_MODE=disabled", str(exc.exception))
        sys.modules.pop("server", None)

    def test_server_import_allows_explicit_no_auth_mode(self) -> None:
        sys.modules.pop("server", None)
        with patch.dict(
            os.environ,
            {
                "SLACK_MCP_XOXC_TOKEN": "browser-session-test",
                "SLACK_MCP_XOXD_TOKEN": "cookie-test",
                "API_KEY_MODE": "disabled",
            },
            clear=True,
        ):
            module = importlib.import_module("server")
            payload = module._health_payload()

        self.assertEqual(payload["mcpAuthMode"], "disabled")
        self.assertFalse(payload["apiKeyAuthConfigured"])
        sys.modules.pop("server", None)
