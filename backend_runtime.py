from __future__ import annotations

import os
import re

RUNTIME_PLACEHOLDER_RE = re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$")

DEFAULT_ENABLED_TOOLS = [
    "attachment_get_data",
    "channels_list",
    "channels_me",
    "conversations_add_message",
    "conversations_history",
    "conversations_join",
    "conversations_leave",
    "conversations_mark",
    "conversations_replies",
    "conversations_search_messages",
    "conversations_unreads",
    "reactions_add",
    "reactions_remove",
    "saved_clear_completed",
    "saved_list",
    "saved_update",
    "usergroups_create",
    "usergroups_list",
    "usergroups_me",
    "usergroups_update",
    "usergroups_users_update",
    "users_search",
]

REQUIRED_AUTH_VARS = ("SLACK_MCP_XOXC_TOKEN", "SLACK_MCP_XOXD_TOKEN")
FORBIDDEN_AUTH_VARS = ("SLACK_MCP_XOXP_TOKEN", "SLACK_MCP_XOXB_TOKEN")


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


def _raw_runtime_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    cleaned = value.strip()
    if RUNTIME_PLACEHOLDER_RE.fullmatch(cleaned):
        return None
    return value


def _split_csv(value: str) -> list[str]:
    return [token.strip() for token in value.split(",") if token.strip()]


def configured_enabled_tools() -> list[str] | str | None:
    raw = _raw_runtime_env("SLACK_MCP_ENABLED_TOOLS")
    if raw is None:
        return None
    trimmed = raw.strip()
    if not trimmed or trimmed.lower() in {"all", "*"}:
        return "all"
    return _split_csv(trimmed)


def effective_enabled_tools() -> list[str] | str:
    configured = configured_enabled_tools()
    if configured == "all":
        return "all"
    if isinstance(configured, list):
        return configured
    return list(DEFAULT_ENABLED_TOOLS)


def validate_auth_environment() -> None:
    missing = [name for name in REQUIRED_AUTH_VARS if not _runtime_env(name)]
    if missing:
        raise SystemExit(
            "Missing required Slack browser auth env vars: "
            + ", ".join(missing)
            + ". This runtime supports xoxc/xoxd only."
        )

    forbidden = [name for name in FORBIDDEN_AUTH_VARS if _runtime_env(name)]
    if forbidden:
        raise SystemExit(
            "Unsupported auth env var(s) detected: "
            + ", ".join(forbidden)
            + ". Clear them so the Slack runtime cannot prefer xoxp/xoxb over xoxc/xoxd."
        )
