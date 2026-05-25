# Slack MCP

Slack MCP is a FastMCP Python server for Slack, built around direct native Slack session support.

## What It Does

The server exposes a validated Slack MCP surface for reading and acting against Slack workspaces through a native Python runtime. It is designed for personal or controlled workspace use where the current browser-session auth flow is acceptable.

## Core Capabilities

- validated Slack MCP tool surface
- direct Slack session auth with current supported token types
- configurable tool exposure allowlist
- MCP bearer-key protection for the server itself
- local and container runtime paths

## Endpoints

- MCP: `http://localhost:3005/mcp`
- Health: `http://localhost:3005/health`

## Required Authentication

- `SLACK_MCP_XOXC_TOKEN`
- `SLACK_MCP_XOXD_TOKEN`

Optional but recommended:

- `SLACK_MCP_API_KEY`

## Quick Start

```bash
uv sync --no-dev
python scripts/run_server.py serve
python scripts/run_server.py doctor
python scripts/run_server.py url
```

## Docker

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

## MCP Client Connection

- URL: `http://<host>:<port>/mcp`
- Header: `Authorization: Bearer <your-api-key>`

## Documentation

Start with:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/product-specs/tool-surface.md](docs/product-specs/tool-surface.md)
- [docs/SECURITY.md](docs/SECURITY.md)

For repository workflow and agent-focused context, read [AGENTS.md](AGENTS.md).
