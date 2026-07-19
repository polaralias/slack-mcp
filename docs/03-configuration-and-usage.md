# 3. Configuration And Usage

## Runtime shape

The repository now runs as:

1. Python FastMCP server
2. native Slack session implementation in Python
3. no delegated backend process

## Startup

```bash
python scripts/run_server.py serve
python scripts/run_server.py doctor
python scripts/run_server.py url
```

## Key environment variables

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
- `SLACK_MCP_GOVSLACK`
- `SLACK_MCP_USER_AGENT`
- `SLACK_MCP_WORKSPACE`

## Tool exposure model

- `SLACK_MCP_ENABLED_TOOLS` controls which tools are exposed.
- Slack mutation behaviour is governed directly by the native implementation rather than by a delegated backend selection path.

## Health and connectivity

Default local endpoints:

- MCP: `http://127.0.0.1:3005/mcp`
- health: `http://127.0.0.1:3005/health`

Example client auth:

```text
Authorization: Bearer <SLACK_MCP_API_KEY>
```

## Example local workflow

1. Configure auth:

```env
SLACK_MCP_XOXC_TOKEN=<paste-slack-browser-token>
SLACK_MCP_XOXD_TOKEN=<paste-slack-cookie-d-value>
SLACK_MCP_API_KEY=change-me
SLACK_MCP_ENABLED_TOOLS=all
```

2. Inspect startup:

```bash
python scripts/run_server.py doctor
```

3. Start the service:

```bash
python scripts/run_server.py serve
```

4. Verify health:

```bash
curl http://127.0.0.1:3005/health
```

## Canonical companion docs

- setup: [01-authentication-setup.md](01-authentication-setup.md)
- install: [02-installation.md](02-installation.md)
- detailed config: [configuration.md](configuration.md)
- runtime findings: [runtime-validation-2026-05-23-native-bootstrap.md](runtime-validation-2026-05-23-native-bootstrap.md)
