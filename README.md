# slack-mcp

Standalone FastMCP Python server for Slack with direct native Slack session support.

## Current status

- Default MCP endpoint: `http://localhost:3005/mcp`
- Default health endpoint: `http://localhost:3005/health`
- Native Python runtime is the only supported runtime
- Validated contract surface: 22 tools plus 2 resources
- Supported Slack auth parameters:
  - `SLACK_MCP_XOXC_TOKEN`
  - `SLACK_MCP_XOXD_TOKEN`
- Supports `SLACK_MCP_API_KEY`, `MCP_API_KEY`, or `MCP_API_KEYS`

## Read this first

1. [AGENTS.md](AGENTS.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [docs/DESIGN.md](docs/DESIGN.md)
4. [docs/PLANS.md](docs/PLANS.md)
5. [docs/SECURITY.md](docs/SECURITY.md)
6. [docs/RELIABILITY.md](docs/RELIABILITY.md)

High-signal references:

- [docs/product-specs/rewrite-compatibility-contract.md](docs/product-specs/rewrite-compatibility-contract.md)
- [docs/product-specs/tool-surface.md](docs/product-specs/tool-surface.md)
- [docs/exec-plans/active/contract-harness.md](docs/exec-plans/active/contract-harness.md)
- [docs/runtime-validation-2026-05-23-native-bootstrap.md](docs/runtime-validation-2026-05-23-native-bootstrap.md)

## Configuration

Required:

- `SLACK_MCP_XOXC_TOKEN`
- `SLACK_MCP_XOXD_TOKEN`

Recommended:

- `SLACK_MCP_API_KEY`

Common optional settings:

- `SLACK_MCP_ENABLED_TOOLS`
- `SLACK_MCP_HOST`
- `SLACK_MCP_PORT`
- `SLACK_MCP_PATH`
- `MCP_HEALTH_PATH`
- `API_KEY_MODE`
- `SLACK_MCP_GOVSLACK`
- `SLACK_MCP_USER_AGENT`
- `SLACK_MCP_WORKSPACE`

Tool selection note:

- If `SLACK_MCP_ENABLED_TOOLS` is not set, the full validated 22-tool surface is exposed.
- You can still restrict exposure with a comma-separated allowlist.

Authentication note:

- This runtime intentionally supports the current browser-session auth flow only.
- Leave `SLACK_MCP_XOXP_TOKEN` and `SLACK_MCP_XOXB_TOKEN` unset.

## Run locally

```bash
uv sync --no-dev
python scripts/run_server.py serve
python scripts/run_server.py doctor
python scripts/run_server.py url
```

## Run with Docker Compose

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

## MCP client connection

- URL: `http://<host>:<port>/mcp`
- Header: `Authorization: Bearer <your-api-key>`

## Repository notes

- The FastMCP Python layer is the user-facing server and the Slack implementation.
- The Go backend and npm package launcher are no longer part of supported product code.
- Historical runtime-validation docs remain in the repo as evidence, not as active implementation guidance.
