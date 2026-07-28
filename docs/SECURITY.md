---
type: "Security Boundary"
title: "Security"
description: "Documents Security for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - slack-mcp
  - security-boundary
navigation:
  role: foundational
  order: 20
---
# Security

## Security goals

- minimise secret exposure
- minimise accidental write capability
- make auth mode explicit
- reduce hidden runtime dependencies

## Current security positives

- Python wrapper can require bearer auth
- write-capable tools are intentionally gateable
- browser-session auth can be validated without persisting secrets in repo files

## Current security concerns

- historical runtime evidence can still be mistaken for supported product behaviour
- browser-session credentials are powerful and easy to leak in local validation

## Security baseline

- local Python-only implementation
- exactly one supported Slack auth mode: `xoxc` plus `xoxd`
- clear secret handling guidance
- explicit tool exposure model
- docs that separate verified support from inherited or legacy behaviour

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
