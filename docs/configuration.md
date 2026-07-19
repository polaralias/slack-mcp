# Configuration Reference

## Purpose

This document defines the native Python runtime configuration model.

## Required Slack auth

| Variable | Required | Purpose |
| --- | --- | --- |
| `SLACK_MCP_XOXC_TOKEN` | Yes | Slack browser-session token |
| `SLACK_MCP_XOXD_TOKEN` | Yes | Slack browser-session cookie token |

## Recommended MCP auth

| Variable | Required | Purpose |
| --- | --- | --- |
| `SLACK_MCP_API_KEY` | Recommended | Bearer token accepted by the FastMCP HTTP layer |

Compatible aliases:

- `MCP_API_KEY`
- `MCP_API_KEYS`
- `API_KEY_MODE`

## Endpoint variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `SLACK_MCP_HOST` | `127.0.0.1` | Preferred host bind override |
| `SLACK_MCP_PORT` | `3005` | Preferred port override |
| `SLACK_MCP_PATH` | `/mcp` | Preferred MCP path override |
| `MCP_HOST` / `HOST` | inherited alias | Generic host aliases |
| `MCP_PORT` / `PORT` | inherited alias | Generic port aliases |
| `MCP_PATH` | inherited alias | Generic path alias |
| `MCP_HEALTH_PATH` | `/health` | Health endpoint path |
| `MCP_TRANSPORT` / `FASTMCP_TRANSPORT` | `streamable-http` | Transport mode |

## Tool exposure

| Variable | Default | Purpose |
| --- | --- | --- |
| `SLACK_MCP_ENABLED_TOOLS` | all 22 validated tools | Restricts exposed tools when set to a comma-separated allowlist |

## Slack behaviour and tuning

| Variable | Default | Purpose |
| --- | --- | --- |
| `SLACK_MCP_USER_AGENT` | `slack-mcp-native/1.0` | Custom outbound user-agent |
| `SLACK_MCP_GOVSLACK` | false | GovSlack domain switch |
| `SLACK_MCP_WORKSPACE` | `workspace` | Resource URI workspace segment override |

## Unsupported auth variables

These should remain unset:

- `SLACK_MCP_XOXP_TOKEN`
- `SLACK_MCP_XOXB_TOKEN`

## Harness-only variables

These are not part of the public product contract:

- `SLACK_MCP_HARNESS_UPLOAD_TOOL`
- `SLACK_MCP_HARNESS_SAVED_TOOL`

## Canonical local example

```env
SLACK_MCP_XOXC_TOKEN=<paste-slack-browser-token>
SLACK_MCP_XOXD_TOKEN=<paste-slack-cookie-d-value>
SLACK_MCP_API_KEY=change-me
SLACK_MCP_ENABLED_TOOLS=all
SLACK_MCP_PORT=3005
SLACK_MCP_PATH=/mcp
```
