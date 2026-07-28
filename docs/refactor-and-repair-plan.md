---
type: "Delivery Plan"
title: "Refactor And Repair Plan"
description: "Documents Refactor And Repair Plan for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - slack-mcp
  - delivery-plan
navigation:
  role: supporting
  order: 100
---
# Refactor And Repair Plan

## Current status

The original repair and rewrite objective has been completed at the runtime level:

- the repository now ships one supported Python-native FastMCP runtime
- the validated 22-tool contract has been preserved
- the Go backend and npm launcher path have been removed from supported product code
- the primary black-box harness is green against the native runtime

Latest verified evidence:

- [runtime-validation-2026-05-23-native-bootstrap.md](runtime-validation-2026-05-23-native-bootstrap.md)
- [exec-plans/active/contract-harness.md](exec-plans/active/contract-harness.md)

## What the repair phase achieved

- established the validated 22-tool and 2-resource contract surface
- built a Python black-box MCP harness around that surface
- migrated all validated tool behaviour into direct Python Slack session code
- removed delegated backend selection and preserved only the native runtime path
- updated packaging, compose, and CI towards the Python-native runtime

## Current focus

The repository is now in a post-migration hardening and simplification phase.

Priority work:

1. keep the native runtime and harness aligned as the single source of truth
2. reduce migration-era complexity that is no longer needed
3. tighten final-contract docs and assertions
4. improve packaging and operational clarity for the Python-native runtime

## Remaining work categories

### Contract hardening

- promote more behaviour from observed-runtime assertions into explicit final-contract assertions
- decide where text outputs should remain text and where structured output should be strengthened
- keep fixture-sensitive success paths proven and maintained

### Runtime simplification

- review now-redundant environment controls and helper pathways
- keep only product-significant configuration in canonical docs
- prevent reintroduction of delegated backend patterns

### Documentation maintenance

- keep canonical docs current with shipped code
- preserve dated evidence docs as history, not active runtime guidance
- retire or clearly label archaeology docs that still describe removed architecture

### Operational polish

- ensure Docker and CI reflect only the supported native runtime
- improve local operator guidance around auth, health, and tool exposure

## Explicit non-goals

- no restoration of Go runtime support
- no restoration of npm package launcher support
- no restoration of delegated backend process architecture

## Success criteria for the current phase

- canonical docs describe only the supported Python-native runtime as current truth
- dated evidence docs remain available for history without confusing active guidance
- the black-box harness stays green and remains the default proof mechanism
- repository packaging and CI paths align with native-only runtime support

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
