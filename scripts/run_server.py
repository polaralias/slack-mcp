from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
GO_MOD_PATH = REPO_ROOT / "go.mod"
GO_MAIN_PATH = REPO_ROOT / "cmd" / "slack-mcp-server" / "main.go"
DEFAULT_PACKAGE_SPEC = "slack-mcp-server@latest"
DEFAULT_RUN_MODE = "auto"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3005
DEFAULT_PATH = "/mcp"
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
SLACK_BINARY_NAME = "slack-mcp-server"


@dataclass(frozen=True)
class RuntimeConfig:
    host: str
    port: int
    path: str
    run_mode: str
    package_spec: str

    @property
    def mcp_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"

    @property
    def health_url(self) -> str:
        return f"http://{self.host}:{self.port}/health"


def _normalize_path(value: str) -> str:
    cleaned = (value or "/").strip()
    if not cleaned:
        return "/"
    return "/" + cleaned.strip("/")


def _runtime_env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        cleaned = value.strip()
        if cleaned:
            return cleaned
    return default


def _env_file_candidates() -> list[Path]:
    candidates: list[Path] = []
    configured = os.getenv("MCP_ENV_FILE", "").strip()
    if configured:
        candidates.append(Path(configured))
    candidates.append(REPO_ROOT / ".env")
    return candidates


def load_env_files() -> None:
    seen: set[Path] = set()
    for candidate in _env_file_candidates():
        path = candidate.expanduser().resolve()
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            if len(value) >= 2 and value[:1] == value[-1:] and value[:1] in {"'", '"'}:
                value = value[1:-1]
            os.environ.setdefault(key, value)


def _resolve_shell_command(candidates: list[str]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def npx_command() -> list[str] | None:
    candidates = ["npx.cmd", "npx"] if os.name == "nt" else ["npx"]
    resolved = _resolve_shell_command(candidates)
    return [resolved] if resolved else None


def npm_command() -> list[str] | None:
    candidates = ["npm.cmd", "npm"] if os.name == "nt" else ["npm"]
    resolved = _resolve_shell_command(candidates)
    return [resolved] if resolved else None


def go_command() -> list[str] | None:
    candidates = ["go.exe", "go"] if os.name == "nt" else ["go"]
    resolved = _resolve_shell_command(candidates)
    return [resolved] if resolved else None


def local_source_available() -> bool:
    return GO_MOD_PATH.exists() and GO_MAIN_PATH.exists()


def package_command(package_spec: str, binary_name: str, args: list[str]) -> list[str]:
    npx = npx_command()
    if npx:
        return npx + ["--yes", "--package", package_spec, "--", binary_name, *args]

    npm = npm_command()
    if npm:
        return npm + ["exec", "--yes", "--package", package_spec, "--", binary_name, *args]

    raise SystemExit("Node/npm tooling is required. Neither npx nor npm was found on PATH.")


def enabled_tools_value() -> str:
    return _runtime_env("SLACK_MCP_ENABLED_TOOLS", default=",".join(DEFAULT_READ_ONLY_TOOLS))


def load_config() -> RuntimeConfig:
    run_mode = _runtime_env("SLACK_MCP_RUN_MODE", default=DEFAULT_RUN_MODE).lower()
    if run_mode not in {"auto", "go", "package"}:
        raise SystemExit("SLACK_MCP_RUN_MODE must be one of: auto, go, package.")

    return RuntimeConfig(
        host=_runtime_env("SLACK_MCP_HOST", "MCP_HOST", default=DEFAULT_HOST),
        port=int(_runtime_env("SLACK_MCP_PORT", "MCP_PORT", default=str(DEFAULT_PORT))),
        path=_normalize_path(_runtime_env("SLACK_MCP_PATH", "MCP_PATH", default=DEFAULT_PATH)),
        run_mode=run_mode,
        package_spec=_runtime_env("SLACK_MCP_PACKAGE_SPEC", default=DEFAULT_PACKAGE_SPEC),
    )


def validate_auth_environment() -> None:
    missing = [name for name in REQUIRED_AUTH_VARS if not os.getenv(name, "").strip()]
    if missing:
        raise SystemExit(
            "Missing required Slack browser auth env vars: "
            + ", ".join(missing)
            + ". This runtime supports xoxc/xoxd only."
        )

    forbidden = [name for name in FORBIDDEN_AUTH_VARS if os.getenv(name, "").strip()]
    if forbidden:
        raise SystemExit(
            "Unsupported auth env var(s) detected: "
            + ", ".join(forbidden)
            + ". Clear them so the Slack runtime cannot prefer xoxp/xoxb over xoxc/xoxd."
        )


def build_env(config: RuntimeConfig) -> dict[str, str]:
    env = os.environ.copy()
    env["SLACK_MCP_HOST"] = config.host
    env["SLACK_MCP_PORT"] = str(config.port)
    env["SLACK_MCP_PATH"] = config.path
    env["SLACK_MCP_ENABLED_TOOLS"] = enabled_tools_value()
    env.setdefault("SLACK_MCP_LOG_LEVEL", "info")
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


def _resolve_runner_mode(config: RuntimeConfig) -> str:
    go = go_command()
    if config.run_mode == "go":
        if not local_source_available():
            raise SystemExit("SLACK_MCP_RUN_MODE=go requires the vendored Slack MCP source tree in this repo.")
        if not go:
            raise SystemExit("SLACK_MCP_RUN_MODE=go requires Go on PATH.")
        return "go"
    if config.run_mode == "package":
        return "package"
    if local_source_available() and go:
        return "go"
    return "package"


def serve_command(config: RuntimeConfig, extra_args: list[str] | None = None) -> tuple[str, list[str]]:
    args = [
        "--transport",
        "http",
        "--enabled-tools",
        enabled_tools_value(),
        *list(extra_args or []),
    ]
    runner_mode = _resolve_runner_mode(config)
    if runner_mode == "go":
        go = go_command()
        if not go:
            raise SystemExit("Go was selected but is not available on PATH.")
        return runner_mode, go + ["run", "./cmd/slack-mcp-server", *args]
    return runner_mode, package_command(config.package_spec, SLACK_BINARY_NAME, args)


def is_server_healthy(config: RuntimeConfig, timeout_seconds: float = 2.0) -> bool:
    try:
        with socket.create_connection((config.host, config.port), timeout=timeout_seconds):
            pass
    except OSError:
        return False

    request = Request(config.health_url, method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return 200 <= getattr(response, "status", 0) < 300
    except HTTPError as exc:
        return exc.code < 500
    except URLError:
        return False


def _remainder(values: list[str]) -> list[str]:
    if values and values[0] == "--":
        return values[1:]
    return values


def cmd_serve(config: RuntimeConfig, args: argparse.Namespace) -> int:
    validate_auth_environment()
    _runner_mode, command = serve_command(config, extra_args=_remainder(args.server_args))
    return subprocess.run(command, cwd=REPO_ROOT, env=build_env(config), check=False).returncode


def cmd_doctor(config: RuntimeConfig, _args: argparse.Namespace) -> int:
    npx = npx_command()
    npm = npm_command()
    go = go_command()
    runner_mode = _resolve_runner_mode(config)
    print(f"repo={REPO_ROOT}")
    print(f"mcp_url={config.mcp_url}")
    print(f"health_url={config.health_url}")
    print(f"runner_mode={runner_mode}")
    print(f"package_spec={config.package_spec}")
    print(f"go_tooling={'present' if go else 'missing'}")
    print(f"node_tooling={'present' if (npx or npm) else 'missing'}")
    print(f"enabled_tools={enabled_tools_value()}")
    print(f"health={'online' if is_server_healthy(config) else 'offline'}")
    return 0


def cmd_url(config: RuntimeConfig, _args: argparse.Namespace) -> int:
    print(config.mcp_url)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="slack-mcp runtime helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Show runtime diagnostics")
    subparsers.add_parser("url", help="Print the MCP URL")

    serve_parser = subparsers.add_parser("serve", help="Run the MCP server")
    serve_parser.add_argument(
        "server_args",
        nargs=argparse.REMAINDER,
        help="Additional slack-mcp-server arguments",
    )
    return parser


def main() -> int:
    load_env_files()
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()

    if args.command == "doctor":
        return cmd_doctor(config, args)
    if args.command == "url":
        return cmd_url(config, args)
    if args.command == "serve":
        return cmd_serve(config, args)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
