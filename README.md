# slack-mcp

Standalone FastMCP Python server for Slack that proxies the preserved Slack runtime over stdio for feature parity.

## Highlights

- Default MCP endpoint: `http://localhost:3005/mcp`
- Default health endpoint: `http://localhost:3005/health`
- Supports `SLACK_MCP_API_KEY`, `MCP_API_KEY`, or `MCP_API_KEYS`
- Preserves the current Slack tool surface and resources by proxying the copied Slack runtime
- Supports the current browser-session auth parameters only:
  - `SLACK_MCP_XOXC_TOKEN`
  - `SLACK_MCP_XOXD_TOKEN`
- Persists Slack cache data under `./state/slack-cache`
- Supports full tool parity when `SLACK_MCP_ENABLED_TOOLS` is set to `all` or an explicitly blank value

## Architecture

This repo packages the FastMCP Python Slack server and the preserved Slack backend runtime together.

- The top-level server is Python/FastMCP.
- The Python server handles HTTP MCP transport, API-key auth, compose-friendly deployment, and health routes.
- The copied Slack runtime remains the backend implementation and is executed over stdio to preserve existing tool behavior, resources, and Slack-specific edge handling.

That makes the client-facing server fully FastMCP Python while avoiding a risky full behavior rewrite of the Slack backend.

## Reference Docs

- [Tool reference](docs/tool-reference.md) contains the full public tool inventory, parameter details, and exposed resources (16 tools).
- [Configuration reference](docs/configuration.md) explains auth, tool exposure gates, backend selection, ports, caching, and deployment notes.

## Configuration

1. Copy `.env.example` to `.env`
2. Fill in the required values:
   - `SLACK_MCP_XOXC_TOKEN`
   - `SLACK_MCP_XOXD_TOKEN`
   - `SLACK_MCP_API_KEY`

Common optional settings:

- `SLACK_MCP_ENABLED_TOOLS`
- `SLACK_MCP_HOST_PORT`
- `SLACK_MCP_PORT`
- `SLACK_MCP_PATH`
- `API_KEY_MODE`
- `SLACK_MCP_BACKEND_MODE`
- `SLACK_MCP_BACKEND_BINARY`
- `SLACK_MCP_PACKAGE_SPEC`
- `SLACK_MCP_USER_AGENT`
- `SLACK_MCP_PROXY`
- `SLACK_MCP_CACHE_TTL`

Tool selection note:

- If `SLACK_MCP_ENABLED_TOOLS` is not set, this workspace defaults to the same read-focused tool subset used in the compose refactor.
- If you want the full Slack tool surface, set `SLACK_MCP_ENABLED_TOOLS=all` or an explicitly blank value.

Docker Compose note:

- If a secret contains a literal `$`, escape it as `$$` in `.env`

Authentication note:

- This refactor intentionally supports the current individual browser-session auth flow only.
- Leave `SLACK_MCP_XOXP_TOKEN` and `SLACK_MCP_XOXB_TOKEN` unset.

## Run Locally

```bash
python scripts/run_server.py serve
python scripts/run_server.py doctor
python scripts/run_server.py url
```

The Python server will choose a backend in this order unless you override it:

1. compiled backend binary
2. local Go source with `go run`
3. published npm package

## Run With Docker Compose

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

The included `docker-compose.yml` publishes the server on port `3005`, joins the external `reverse_proxy` network, and persists Slack cache data under `./state/slack-cache`.

## Add To A Shared MCP Compose Project

Use this service in a larger compose stack when you want one project containing multiple MCP servers:

```yaml
services:
  slack-mcp:
    build:
      context: /path/to/slack-mcp
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file:
      - /path/to/slack-mcp/.env
    environment:
      MCP_HOST: 0.0.0.0
      MCP_PORT: "3005"
      MCP_PATH: /mcp
    volumes:
      - /path/to/slack-mcp/state/slack-cache:/root/.cache/slack-mcp-server
    ports:
      - "3005:3005"
    networks:
      - reverse_proxy

networks:
  reverse_proxy:
    external: true
```

If you do not need host port publishing because you are fronting the service with another internal proxy, you can omit the `ports` section.

## MCP Client Connection

- URL: `http://<host>:<port>/mcp`
- Header: `Authorization: Bearer <your-api-key>`

## Repository Notes

- The FastMCP Python layer proxies tools and resources from the copied Slack runtime
- Health responses identify the server as `slack-mcp`
- Write tools are still available when enabled, but only read-focused validation is expected for this port
