from __future__ import annotations

import unittest
from typing import Any

from tests.harness.inputs import optional_tool_arg


async def tools_by_name(client: Any) -> dict[str, Any]:
    tools = await client.list_tools()
    return {tool.name: tool for tool in tools}


def required_tool_args(tool: Any) -> list[str]:
    schema = getattr(tool, "inputSchema", None) or {}
    required = schema.get("required", [])
    return [str(name) for name in required]


def tool_properties(tool: Any) -> dict[str, Any]:
    schema = getattr(tool, "inputSchema", None) or {}
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        return properties
    return {}


def build_required_args_from_env(tool_name: str, tool: Any) -> dict[str, str]:
    arguments: dict[str, str] = {}
    missing: list[str] = []
    for arg_name in required_tool_args(tool):
        value = optional_tool_arg(tool_name, arg_name)
        if value is None:
            missing.append(arg_name)
        else:
            arguments[arg_name] = value
    if missing:
        missing_envs = ", ".join(
            f"SLACK_MCP_HARNESS_TOOL_{tool_name.upper()}_{arg_name.upper()}" for arg_name in missing
        )
        raise unittest.SkipTest(
            f"Missing required harness tool argument env var(s) for {tool_name}: {missing_envs}"
        )
    return arguments
