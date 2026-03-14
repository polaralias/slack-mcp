# Configuration Reference

This guide explains the supported environment variables and deployment knobs for `slack-mcp`.

## Required settings

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SLACK_MCP_XOXC_TOKEN` | Yes | none | Browser-session cookie token used by the preserved Slack runtime. |
| `SLACK_MCP_XOXD_TOKEN` | Yes | none | Browser-session workspace token paired with `SLACK_MCP_XOXC_TOKEN`. |
| `SLACK_MCP_API_KEY` | Recommended | none | Service-specific bearer token accepted by the FastMCP HTTP endpoint. |

## Supported auth mode

- The FastMCP Python layer intentionally supports the existing individual browser-session auth flow only.
- `SLACK_MCP_XOXP_TOKEN` and `SLACK_MCP_XOXB_TOKEN` are treated as unsupported for this repo and should be left unset.
- `SLACK_MCP_SSE_API_KEY` is retained only as a deprecated backend compatibility alias; prefer `SLACK_MCP_API_KEY` or `MCP_API_KEY`.

## MCP client auth

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `MCP_API_KEY` | No | none | Generic single-key alias if you prefer a shared naming pattern across services. |
| `MCP_API_KEYS` | No | none | Comma-separated additional bearer tokens accepted by the HTTP MCP endpoint. |
| `API_KEY_MODE` | No | static auth enabled | Set to `disabled` to turn off bearer-token checks entirely. |

## Tool exposure and write gates

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SLACK_MCP_ENABLED_TOOLS` | No | read-focused default subset | Comma-separated tool list to expose. Use `all` or a deliberately blank value for the full 16-tool surface. |
| `SLACK_MCP_ADD_MESSAGE_TOOL` | No | disabled unless explicitly enabled | Enables `conversations_add_message`. Supports `true`, `1`, allowlists such as `C123,D456`, or exclusions such as `!C123`. |
| `SLACK_MCP_REACTION_TOOL` | No | disabled unless explicitly enabled | Enables `reactions_add` and `reactions_remove`, with the same channel-restriction syntax as message posting. |
| `SLACK_MCP_ATTACHMENT_TOOL` | No | disabled unless explicitly enabled | Enables `attachment_get_data`. Expected values are truthy flags such as `true`, `1`, or `yes`. |
| `SLACK_MCP_MARK_TOOL` | No | disabled unless explicitly enabled | Enables `conversations_mark`. Expected values are truthy flags such as `true` or `1`. |
| `SLACK_MCP_ADD_MESSAGE_MARK` | No | disabled | When message posting is enabled, automatically marks posted messages as read. |
| `SLACK_MCP_ADD_MESSAGE_UNFURLING` | No | disabled | Enables link unfurling for posted messages, optionally restricted to a comma-separated domain allowlist. |

## Backend selection

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SLACK_MCP_BACKEND_MODE` | No | `auto` | Backend selection strategy for the preserved Slack runtime. Allowed values are `auto`, `binary`, `go`, and `package`. |
| `SLACK_MCP_BACKEND_BINARY` | No | auto-discovered | Absolute path to a compiled backend binary if you want to skip Go or npm resolution. |
| `SLACK_MCP_PACKAGE_SPEC` | No | `slack-mcp-server@latest` | npm package spec used when backend mode falls back to the published package. |

Backend resolution order in `auto` mode:
1. compiled backend binary
2. local Go source with `go run`
3. published npm package

## Runtime, network, and cache settings

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SLACK_MCP_USER_AGENT` | No | none | Custom user-agent string for outbound Slack requests. |
| `SLACK_MCP_PROXY` | No | none | Proxy URL used for outbound requests. |
| `SLACK_MCP_CACHE_TTL` | No | runtime default | Cache TTL used by the Python wrapper when describing backend status and cache behavior. |
| `SLACK_MCP_MIN_REFRESH_INTERVAL` | No | `30s` | Minimum interval between expensive Slack cache refreshes in the preserved runtime. |
| `SLACK_MCP_USERS_CACHE` | No | runtime cache file | Path to the users cache file. |
| `SLACK_MCP_CHANNELS_CACHE` | No | runtime cache file | Path to the channels cache file. |
| `SLACK_MCP_GOVSLACK` | No | `false` | Switches the backend to GovSlack domains. |

## TLS and advanced backend settings

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SLACK_MCP_CUSTOM_TLS` | No | none | Preserved compatibility flag for custom TLS handling in older packaging flows. |
| `SLACK_MCP_SERVER_CA` | No | none | Path to a custom CA certificate file trusted by the backend. |
| `SLACK_MCP_SERVER_CA_TOOLKIT` | No | none | Injects the HTTP Toolkit CA certificate into the trust store for local debugging. |
| `SLACK_MCP_SERVER_CA_INSECURE` | No | disabled | Trust all insecure TLS requests. Do not combine with `SLACK_MCP_SERVER_CA`. |
| `SLACK_MCP_OPENAI_API` | No | none | Integration-test-only setting retained by the copied backend test harness. |
| `SLACK_MCP_DXT` | No | none | Packaging flag used by the bundled npm launcher for DXT-style environments. |

## Logging and endpoint settings

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SLACK_MCP_LOG_LEVEL` | No | `info` | Backend log level. |
| `SLACK_MCP_LOG_FORMAT` | No | runtime default | Backend log format override. |
| `SLACK_MCP_LOG_COLOR` | No | runtime default | Enables or disables colored backend logs where supported. |
| `SLACK_MCP_HOST_PORT` | No | `3005` | Host-side published port in the bundled `docker-compose.yml`. |
| `SLACK_MCP_PORT` | No | `3005` | Internal service port used by the FastMCP HTTP layer. |
| `SLACK_MCP_PATH` | No | `/mcp` | HTTP path where the MCP endpoint is exposed. |
| `MCP_HOST` / `HOST` / `SLACK_MCP_HOST` | No | `127.0.0.1` locally, `0.0.0.0` in compose | Host bind address used by `scripts/run_server.py` and the FastMCP wrapper. |
| `MCP_PORT` / `PORT` | No | `3005` | Generic runtime port override. |
| `MCP_PATH` | No | `/mcp` | Generic runtime path override. |
| `MCP_HEALTH_PATH` | No | `/health` | Health endpoint path exposed by the FastMCP wrapper. |
| `MCP_TRANSPORT` / `FASTMCP_TRANSPORT` | No | `streamable-http` | Transport mode for the FastMCP wrapper. |

## Files and deployment notes

- The FastMCP Python layer handles HTTP transport, API-key auth, and compose-friendly deployment.
- The copied Slack runtime remains the backend implementation and is executed over stdio for feature parity.
- The bundled compose file assumes the external Docker network `reverse_proxy` already exists.
- Persist `./state/slack-cache` if you want cache files to survive container recreation.
