---
type: "Reference"
title: "2. Installation"
description: "Documents 2. Installation for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - slack-mcp
  - reference
navigation:
  role: reference
  order: 200
---
# 2. Installation

## Purpose

This document defines the supported installation path for the repository.

## Supported setup

For contributors and operators, the supported setup is:

1. local Python environment
2. local FastMCP server from this repository
3. direct native Slack session auth

## Requirements

- Python 3.11+
- `uv`
- Slack browser-session credentials:
  - `SLACK_MCP_XOXC_TOKEN`
  - `SLACK_MCP_XOXD_TOKEN`

Optional:

- Docker, if you want the containerised path

## Install local Python environment

From the repository root:

```bash
uv sync --no-dev
```

## Local startup

```bash
python scripts/run_server.py serve
python scripts/run_server.py doctor
python scripts/run_server.py url
```

## Docker startup

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

## Notes

- Go source, Go binaries, and npm package launchers are no longer part of supported installation paths.
- Historical validation docs may mention package-backed runtime paths; treat those as dated evidence only.

## Next

- [03-configuration-and-usage.md](03-configuration-and-usage.md)

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
