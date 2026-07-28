---
type: "Delivery Plan"
title: "Plans"
description: "Documents Plans for the slack-mcp repository."
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
# Plans

## Canonical plan docs

- [refactor-and-repair-plan.md](refactor-and-repair-plan.md)
- [exec-plans/active/contract-harness.md](exec-plans/active/contract-harness.md)
- [exec-plans/tech-debt-tracker.md](exec-plans/tech-debt-tracker.md)

Completed and archived:

- [exec-plans/archive/documentation-harness.md](exec-plans/archive/documentation-harness.md)
- [archive/index.md](archive/index.md)

## Current plan hierarchy

1. Keep the Python-native 22-tool contract green under black-box MCP tests.
2. Consolidate or retire transitional migration-era flags and helper pathways where they no longer add value.
3. Promote more end-state contract assertions from “observed runtime” to explicit final behaviour.
4. Reduce documentation drift by keeping canonical docs aligned with shipped native code after each tranche.
5. Improve ergonomics and packaging around the supported Python-native runtime only.

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
