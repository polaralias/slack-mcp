from __future__ import annotations

import os
import unittest


ENV_PREFIX = "SLACK_MCP_HARNESS_"


def env_name(name: str) -> str:
    return f"{ENV_PREFIX}{name}"


def optional_env(name: str) -> str | None:
    value = os.getenv(env_name(name), "").strip()
    return value or None


def require_env(name: str) -> str:
    value = optional_env(name)
    if value is None:
        raise unittest.SkipTest(f"Missing required harness env var: {env_name(name)}")
    return value


def tool_arg_env_name(tool_name: str, arg_name: str) -> str:
    tool_segment = tool_name.upper()
    arg_segment = arg_name.upper()
    return env_name(f"TOOL_{tool_segment}_{arg_segment}")


def optional_tool_arg(tool_name: str, arg_name: str) -> str | None:
    value = os.getenv(tool_arg_env_name(tool_name, arg_name), "").strip()
    return value or None
