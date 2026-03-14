from __future__ import annotations

import os
import re
import secrets
from pathlib import Path
from typing import Any, Iterable

from fastmcp.client.transports.stdio import StdioTransport
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.server.providers.proxy import FastMCPProxy, StatefulProxyClient
from starlette.responses import JSONResponse

from backend_runtime import (
    DEFAULT_READ_ONLY_TOOLS,
    configured_enabled_tools,
    effective_enabled_tools,
    resolve_backend_command,
)

RUNTIME_PLACEHOLDER_RE = re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$")
REPO_ROOT = Path(__file__).resolve().parent
LOG_DIR = REPO_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


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


def _split_csv(value: str) -> list[str]:
    return [token.strip() for token in value.split(",") if token.strip()]


def _load_api_keys() -> list[str]:
    api_key_mode = _runtime_env("API_KEY_MODE", default="").strip().lower()
    if api_key_mode == "disabled":
        return []

    keys: list[str] = []
    for key in (_runtime_env("SLACK_MCP_API_KEY"), _runtime_env("MCP_API_KEY")):
        if key:
            keys.append(key)

    multi = _runtime_env("MCP_API_KEYS")
    if multi:
        keys.extend(_split_csv(multi))

    return list(dict.fromkeys(keys))


class StaticApiKeyVerifier(TokenVerifier):
    def __init__(self, api_keys: Iterable[str], base_url: str | None = None) -> None:
        super().__init__(base_url=base_url or None)
        self._api_keys = [key for key in api_keys if key]

    async def verify_token(self, token: str) -> AccessToken | None:
        for key in self._api_keys:
            if secrets.compare_digest(token, key):
                return AccessToken(token=token, client_id="slack-mcp", scopes=[])
        return None


backend_command = resolve_backend_command()
backend_transport = StdioTransport(
    command=backend_command.command,
    args=backend_command.args,
    env=backend_command.env,
    cwd=backend_command.cwd,
    keep_alive=True,
    log_file=LOG_DIR / "backend.stderr.log",
)
proxy_client = StatefulProxyClient(backend_transport)

api_keys = _load_api_keys()
auth = StaticApiKeyVerifier(api_keys=api_keys, base_url=_runtime_env("BASE_URL")) if api_keys else None
server = FastMCPProxy(
    name="slack-mcp",
    auth=auth,
    client_factory=proxy_client.new_stateful,
)
mcp = server


def _configured_enabled_tools_payload() -> list[str] | str:
    configured = configured_enabled_tools()
    if configured is None:
        return "default-read-only"
    return configured


def _effective_enabled_tools_payload() -> list[str] | str:
    effective = effective_enabled_tools()
    if effective == "all":
        return "all"
    return list(effective)


def _health_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "server": "slack-mcp",
        "implementation": "fastmcp-python-proxy",
        "backendMode": backend_command.mode,
        "backendCommand": backend_command.summary,
        "defaultEnabledTools": list(DEFAULT_READ_ONLY_TOOLS),
        "configuredEnabledTools": _configured_enabled_tools_payload(),
        "effectiveEnabledTools": _effective_enabled_tools_payload(),
        "apiKeyAuthConfigured": bool(api_keys),
    }


@server.custom_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def root_health(_request):
    return JSONResponse(_health_payload())


@server.custom_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
async def health(_request):
    return JSONResponse(_health_payload())


@server.custom_route("/healthz", methods=["GET", "HEAD"], include_in_schema=False)
async def healthz(_request):
    return JSONResponse(_health_payload())


def main() -> None:
    transport_name = _runtime_env("FASTMCP_TRANSPORT", default="streamable-http").lower()
    if transport_name == "http":
        transport_name = "streamable-http"
    if transport_name == "stdio":
        server.run()
    else:
        host = _runtime_env("HOST", default="127.0.0.1")
        port = int(_runtime_env("PORT", default="3005"))
        path = _runtime_env("MCP_PATH", default="/mcp")
        server.run(
            transport=transport_name,
            host=host,
            port=port,
            path=path,
            show_banner=False,
        )


if __name__ == "__main__":
    main()
