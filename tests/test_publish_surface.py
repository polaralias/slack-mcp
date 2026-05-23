from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / ".env.example",
    REPO_ROOT / "docs" / "configuration.md",
    REPO_ROOT / "docs" / "03-configuration-and-usage.md",
]

UNSUPPORTED_PUBLIC_ENV_VARS = {
    "SLACK_MCP_ADD_MESSAGE_MARK",
    "SLACK_MCP_ADD_MESSAGE_TOOL",
    "SLACK_MCP_ATTACHMENT_TOOL",
    "SLACK_MCP_CACHE_TTL",
    "SLACK_MCP_LOG_COLOR",
    "SLACK_MCP_LOG_FORMAT",
    "SLACK_MCP_LOG_LEVEL",
    "SLACK_MCP_NATIVE_USERS_SEARCH",
    "SLACK_MCP_PROXY",
    "SLACK_MCP_REACTION_TOOL",
}


class PublishSurfaceTests(unittest.TestCase):
    def test_fastmcp_manifest_does_not_expose_unsupported_public_env_vars(self) -> None:
        manifest = json.loads((REPO_ROOT / "fastmcp.json").read_text(encoding="utf-8"))
        env = manifest["deployment"]["env"]
        self.assertTrue(isinstance(env, dict))
        self.assertFalse(UNSUPPORTED_PUBLIC_ENV_VARS.intersection(env))

    def test_public_docs_do_not_advertise_unsupported_public_env_vars(self) -> None:
        for path in PUBLIC_DOCS:
            content = path.read_text(encoding="utf-8")
            for variable_name in UNSUPPORTED_PUBLIC_ENV_VARS:
                with self.subTest(path=path.name, variable_name=variable_name):
                    self.assertNotIn(variable_name, content)

    def test_ci_uses_safe_pull_request_trigger(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "unit-tests.yaml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("pull_request_target:", workflow)

    def test_ci_always_runs_offline_verification(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "unit-tests.yaml").read_text(encoding="utf-8")
        self.assertIn("tests.test_runtime_config", workflow)
        self.assertIn("tests.test_publish_surface", workflow)

