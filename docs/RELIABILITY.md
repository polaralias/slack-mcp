---
type: "Reliability Contract"
title: "Reliability"
description: "Documents Reliability for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - slack-mcp
  - reliability-contract
navigation:
  role: supporting
  order: 100
---
# Reliability

## Current reliability posture

The service is operationally real and now has a single supported runtime path: the Python-native FastMCP server.

## Current validated positives

- wrapper startup works
- health endpoint works
- real Slack-backed tool execution works
- resource listing works
- full validated tool surface works in sandbox validation

## Current reliability risks

- Slack-side behavioural drift could still affect fixture-sensitive tools
- some success paths depend on mutable sandbox state
- historical docs can still be mistaken for active implementation guidance

## Reliability baseline

- local-only backend
- deterministic startup path
- explicit auth mode
- repeatable integration fixtures
- contract tests for every supported tool and resource

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
