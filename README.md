# slack-mcp

Standalone Slack MCP server with direct HTTP transport, static API-key auth, and a compose-friendly cache volume.

## Highlights

- Default MCP endpoint: `http://localhost:3005/mcp`
- Default health endpoint: `http://localhost:3005/health`
- Supports `SLACK_MCP_API_KEY`, `MCP_API_KEY`, or `MCP_API_KEYS`
- Preserves the default read-only tool surface through `SLACK_MCP_ENABLED_TOOLS`
- Persists Slack cache data under `./state/slack-cache`

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
- `SLACK_MCP_RUN_MODE`
- `SLACK_MCP_USER_AGENT`
- `SLACK_MCP_PROXY`
- `SLACK_MCP_CACHE_TTL`

Docker Compose note:

- If a secret contains a literal `$`, escape it as `$$` in `.env`

Authentication note:

- The recommended configuration is browser-session auth with `SLACK_MCP_XOXC_TOKEN` and `SLACK_MCP_XOXD_TOKEN`
- Leave `SLACK_MCP_XOXP_TOKEN` and `SLACK_MCP_XOXB_TOKEN` unset for this deployment flow

## Run Locally

```bash
python scripts/run_server.py serve
python scripts/run_server.py doctor
python scripts/run_server.py url
```

The local helper prefers the vendored Go source and can fall back to the published npm package when needed.

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
      target: production
    restart: unless-stopped
    env_file:
      - /path/to/slack-mcp/.env
    environment:
      SLACK_MCP_HOST: 0.0.0.0
      SLACK_MCP_PORT: "3005"
      SLACK_MCP_PATH: /mcp
    command: ["--transport", "http"]
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

- Health responses identify the server as `slack-mcp`
- The repo includes the vendored Go implementation used by the production image
- The default tool allowlist remains read-focused until you change `SLACK_MCP_ENABLED_TOOLS`
