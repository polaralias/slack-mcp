---
type: "Delivery Plan"
title: "Sandbox Fixture Catalogue"
description: "Documents Sandbox Fixture Catalogue for the slack-mcp repository."
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
# Sandbox Fixture Catalogue

## Purpose

This document defines the canonical sandbox fixtures and proof-closure workflow used by the contract harness.

It is execution guidance, not product contract.

## Initial scope

This catalogue should start with the currently unproven or fixture-sensitive surfaces first:

- `attachment_get_data`
- `saved_list`
- `saved_update`
- `saved_clear_completed`
- any resource normalisation checks that require seeded data

It should be structured so it can expand to the full tool and resource surface later.

## Required fixture fields

Each fixture entry should define:

- surface under test
- prerequisite Slack state
- creation steps
- cleanup steps
- proof target
- known risks or nondeterminism

## Initial proof-closure targets

### Attachments

- create or identify a message with a retrievable attachment fixture
- verify success-path retrieval, not just invalid-file error handling

### Saved items

- create or identify at least one valid saved item fixture
- verify list behaviour in non-empty state
- verify update behaviour against a valid saved item
- verify clear-completed behaviour against an intentional completed-state fixture

### Resources

- verify final normalised resource output once the end-state resource schema is defined

## Relationship to other docs

- [../archive/documentation-harness.md](../archive/documentation-harness.md)
- [../tech-debt-tracker.md](../tech-debt-tracker.md)
- [../../product-specs/rewrite-compatibility-contract.md](../../product-specs/rewrite-compatibility-contract.md)
- [../../runtime-validation-2026-05-16.md](../../runtime-validation-2026-05-16.md)

## Repository knowledge

- [Documentation map](../../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
