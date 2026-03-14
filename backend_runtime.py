from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
GO_MOD_PATH = REPO_ROOT / "go.mod"
GO_MAIN_PATH = REPO_ROOT / "cmd" / "slack-mcp-server" / "main.go"
RUNTIME_PLACEHOLDER_RE = re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$")

DEFAULT_PACKAGE_SPEC = "slack-mcp-server@latest"
DEFAULT_BACKEND_MODE = "auto"
DEFAULT_READ_ONLY_TOOLS = [
    "conversations_history",
    "conversations_replies",
    "attachment_get_data",
    "conversations_search_messages",
    "conversations_unreads",
    "channels_list",
    "usergroups_list",
    "users_search",
]
REQUIRED_AUTH_VARS = ("SLACK_MCP_XOXC_TOKEN", "SLACK_MCP_XOXD_TOKEN")
FORBIDDEN_AUTH_VARS = ("SLACK_MCP_XOXP_TOKEN", "SLACK_MCP_XOXB_TOKEN")
BACKEND_MODE_CHOICES = {"auto", "binary", "go", "package"}
HTTP_ONLY_ENV_VARS = {
    "API_KEY_MODE",
    "BASE_URL",
    "FASTMCP_TRANSPORT",
    "HOST",
    "MCP_API_KEY",
    "MCP_API_KEYS",
    "MCP_HEALTH_PATH",
    "MCP_HOST",
    "MCP_PATH",
    "MCP_PORT",
    "MCP_TRANSPORT",
    "PORT",
    "SLACK_MCP_API_KEY",
    "SLACK_MCP_HOST",
    "SLACK_MCP_PATH",
    "SLACK_MCP_PORT",
}


@dataclass(frozen=True)
class BackendCommand:
    mode: str
    command: str
    args: list[str]
    cwd: str | None
    env: dict[str, str]
    summary: dict[str, Any]


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
    return list(DEFAULT_READ_ONLY_TOOLS)


def enabled_tools_argument() -> str:
    effective = effective_enabled_tools()
    if effective == "all":
        return ""
    return ",".join(effective)


def _resolve_shell_command(candidates: list[str]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def npx_command() -> str | None:
    return _resolve_shell_command(["npx.cmd", "npx"] if os.name == "nt" else ["npx"])


def npm_command() -> str | None:
    return _resolve_shell_command(["npm.cmd", "npm"] if os.name == "nt" else ["npm"])


def go_command() -> str | None:
    return _resolve_shell_command(["go.exe", "go"] if os.name == "nt" else ["go"])


def local_source_available() -> bool:
    return GO_MOD_PATH.exists() and GO_MAIN_PATH.exists()


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


def build_backend_env() -> dict[str, str]:
    env = os.environ.copy()
    enabled_tools = enabled_tools_argument()
    if enabled_tools:
        env["SLACK_MCP_ENABLED_TOOLS"] = enabled_tools
    else:
        env.pop("SLACK_MCP_ENABLED_TOOLS", None)
    env.setdefault("SLACK_MCP_LOG_LEVEL", "info")
    for key in HTTP_ONLY_ENV_VARS:
        env.pop(key, None)
    return {key: str(value) for key, value in env.items()}


def _command_summary(mode: str, command: str, args: list[str], cwd: str | None) -> dict[str, Any]:
    return {
        "mode": mode,
        "command": command,
        "args": list(args),
        "cwd": cwd,
    }


def _transport_args() -> list[str]:
    args = ["--transport", "stdio"]
    enabled_tools = enabled_tools_argument()
    if enabled_tools:
        args.extend(["--enabled-tools", enabled_tools])
    return args


def _package_process(package_spec: str, tool_args: list[str]) -> tuple[str, list[str]]:
    npx = npx_command()
    if npx:
        return npx, ["--yes", "--package", package_spec, "--", "slack-mcp-server", *tool_args]

    npm = npm_command()
    if npm:
        return npm, ["exec", "--yes", "--package", package_spec, "--", "slack-mcp-server", *tool_args]

    raise SystemExit("Node/npm tooling is required. Neither npx nor npm was found on PATH.")


def _backend_binary_candidates() -> list[str]:
    configured = _runtime_env("SLACK_MCP_BACKEND_BINARY")
    candidates: list[str] = []
    if configured:
        candidates.append(configured)
    candidates.extend(
        [
            str(REPO_ROOT / "build" / "slack-mcp-runtime.exe"),
            str(REPO_ROOT / "build" / "slack-mcp-runtime"),
            str(REPO_ROOT / "build" / "slack-mcp-server.exe"),
            str(REPO_ROOT / "build" / "slack-mcp-server"),
            str(REPO_ROOT / "slack-mcp-runtime.exe"),
            str(REPO_ROOT / "slack-mcp-runtime"),
            str(REPO_ROOT / "slack-mcp-server.exe"),
            str(REPO_ROOT / "slack-mcp-server"),
            "/usr/local/bin/slack-mcp-runtime",
            "/usr/local/bin/slack-mcp-server",
            "/usr/bin/slack-mcp-runtime",
            "/usr/bin/slack-mcp-server",
            "slack-mcp-runtime",
            "slack-mcp-server",
            "mcp-server",
        ]
    )
    return candidates


def _resolve_binary_candidate(candidate: str) -> str | None:
    path = Path(candidate).expanduser()
    if path.exists() and path.is_file():
        return str(path.resolve())
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    return None


def _resolve_backend_binary(required: bool) -> str | None:
    for candidate in _backend_binary_candidates():
        resolved = _resolve_binary_candidate(candidate)
        if resolved:
            return resolved
    if required:
        raise SystemExit(
            "SLACK_MCP_BACKEND_MODE=binary was requested, but no backend binary was found. "
            "Set SLACK_MCP_BACKEND_BINARY or build the bundled runtime first."
        )
    return None


def _resolve_backend_mode() -> str:
    mode = _runtime_env("SLACK_MCP_BACKEND_MODE", default=DEFAULT_BACKEND_MODE).lower()
    if mode not in BACKEND_MODE_CHOICES:
        raise SystemExit("SLACK_MCP_BACKEND_MODE must be one of: auto, binary, go, package.")
    return mode


def resolve_backend_command() -> BackendCommand:
    validate_auth_environment()

    mode = _resolve_backend_mode()
    tool_args = _transport_args()
    env = build_backend_env()
    cwd = str(REPO_ROOT)

    if mode == "binary":
        command = _resolve_backend_binary(required=True)
        if command is None:
            raise SystemExit("Slack backend binary was not found.")
        return BackendCommand(
            mode="binary",
            command=command,
            args=tool_args,
            cwd=cwd,
            env=env,
            summary=_command_summary("binary", command, tool_args, cwd),
        )

    if mode == "go":
        if not local_source_available():
            raise SystemExit(
                "SLACK_MCP_BACKEND_MODE=go requires the copied Slack Go source tree in this repo."
            )
        command = go_command()
        if not command:
            raise SystemExit("SLACK_MCP_BACKEND_MODE=go requires Go on PATH.")
        args = ["run", "./cmd/slack-mcp-server", *tool_args]
        return BackendCommand(
            mode="go",
            command=command,
            args=args,
            cwd=cwd,
            env=env,
            summary=_command_summary("go", command, args, cwd),
        )

    if mode == "package":
        package_spec = _runtime_env("SLACK_MCP_PACKAGE_SPEC", default=DEFAULT_PACKAGE_SPEC)
        command, args = _package_process(package_spec, tool_args)
        return BackendCommand(
            mode="package",
            command=command,
            args=args,
            cwd=cwd,
            env=env,
            summary=_command_summary("package", command, args, cwd),
        )

    binary_command = _resolve_backend_binary(required=False)
    if binary_command:
        return BackendCommand(
            mode="binary",
            command=binary_command,
            args=tool_args,
            cwd=cwd,
            env=env,
            summary=_command_summary("binary", binary_command, tool_args, cwd),
        )

    go = go_command()
    if local_source_available() and go:
        args = ["run", "./cmd/slack-mcp-server", *tool_args]
        return BackendCommand(
            mode="go",
            command=go,
            args=args,
            cwd=cwd,
            env=env,
            summary=_command_summary("go", go, args, cwd),
        )

    package_spec = _runtime_env("SLACK_MCP_PACKAGE_SPEC", default=DEFAULT_PACKAGE_SPEC)
    command, args = _package_process(package_spec, tool_args)
    return BackendCommand(
        mode="package",
        command=command,
        args=args,
        cwd=cwd,
        env=env,
        summary=_command_summary("package", command, args, cwd),
    )
