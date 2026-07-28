---
type: "Delivery Plan"
title: "Tech Debt Tracker"
description: "Documents Tech Debt Tracker for the slack-mcp repository."
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
# Tech Debt Tracker

## P0

- Final-contract assertions remain less complete than broad observed-runtime coverage.

## P1

- `usergroups_me leave` still depends on Slack accepting a non-empty replacement member list.
- Harness-only fixture helpers should be reviewed periodically so they stay internal infrastructure rather than accidental product surface.
- A few historical evidence docs still need periodic review so they remain clearly archival rather than active guidance.

## P2

- Packaging and deployment ergonomics can be tightened further for the native-only runtime.
- Some output formats are still text-first where future structured output may be preferable.

## Usage

This file is a tracker, not the full plan.

Primary plan reference:

- [../refactor-and-repair-plan.md](../refactor-and-repair-plan.md)

## Repository knowledge

- [Documentation map](../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
