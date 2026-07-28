---
type: "Reference"
title: "Tool Reference"
description: "Documents Tool Reference for the slack-mcp repository."
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
# Tool Reference

## Purpose

This document defines the tool-surface reference in a way that is useful for:

- native runtime maintenance
- harness development
- historical provenance review

It is not just a dump of one implementation file.

## Important warning

There was a historical mismatch between:

- the legacy checked-in Go subtree tool surface
- the validated live packaged backend tool surface
- the current Python-native runtime surface

Because of that history, this document separates:

1. current Python-native compatibility target
2. legacy Go-subtree intent
3. validated live runtime surface

References:

- [runtime-validation-2026-05-16.md](runtime-validation-2026-05-16.md)
- [refactor-and-repair-plan.md](refactor-and-repair-plan.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

## Surface categories

### Current Python-native categories

- conversations
- channels and users
- reactions and attachments
- saved items
- usergroups

### Legacy Go-subtree categories

- conversations
- channels and users
- reactions and attachments
- usergroups

### Historical validation categories

- conversations
- channels and users
- reactions and attachments
- saved items
- usergroups

## Current Python-native compatibility tool set

This is the current repository runtime intent after the Python-native transition work.

### Conversations

- `conversations_add_message`
- `conversations_history`
- `conversations_join`
- `conversations_leave`
- `conversations_mark`
- `conversations_replies`
- `conversations_search_messages`
- `conversations_unreads`

### Channels and users

- `channels_list`
- `channels_me`
- `users_search`

### Reactions and attachments

- `attachment_get_data`
- `reactions_add`
- `reactions_remove`

### Saved items

- `saved_clear_completed`
- `saved_list`
- `saved_update`

### Usergroups

- `usergroups_create`
- `usergroups_list`
- `usergroups_me`
- `usergroups_update`
- `usergroups_users_update`

Current Python-native count:

- 22 tools

## Legacy Go-subtree intent tool set

This is the older local Go-subtree intent described by the inherited checked-in Go code and prior docs.

### Conversations

- `conversations_history`
- `conversations_replies`
- `conversations_add_message`
- `conversations_search_messages`
- `conversations_unreads`
- `conversations_mark`

### Reactions and attachments

- `reactions_add`
- `reactions_remove`
- `attachment_get_data`

### Channels and users

- `channels_list`
- `users_search`

### Usergroups

- `usergroups_list`
- `usergroups_me`
- `usergroups_create`
- `usergroups_update`
- `usergroups_users_update`

Canonical repo-intent count:

- 16 tools

## Historical validation tool set

This is the tool surface observed from the packaged backend path on 2026-05-16, which is still useful as provenance for how the 22-tool contract was established.

### Conversations

- `conversations_add_message`
- `conversations_history`
- `conversations_join`
- `conversations_leave`
- `conversations_mark`
- `conversations_replies`
- `conversations_search_messages`
- `conversations_unreads`

### Channels and users

- `channels_list`
- `channels_me`
- `users_search`

### Reactions and attachments

- `attachment_get_data`
- `reactions_add`
- `reactions_remove`

### Saved items

- `saved_list`
- `saved_update`
- `saved_clear_completed`

### Usergroups

- `usergroups_create`
- `usergroups_list`
- `usergroups_me`
- `usergroups_update`
- `usergroups_users_update`

Validated live-runtime count:

- 22 tools

## Mismatch summary

Tools present in the validated live runtime and current Python-native runtime but not in the legacy Go-subtree docs:

- `channels_me`
- `conversations_join`
- `conversations_leave`
- `saved_list`
- `saved_update`
- `saved_clear_completed`

This mismatch is resolved in shipped product code but remains useful as historical provenance for why the contract expanded.

## Validation status by tool

### Verified success

- `channels_list`
- `channels_me`
- `users_search`
- `conversations_history`
- `conversations_add_message`
- `conversations_replies`
- `conversations_search_messages`
- `conversations_unreads`
- `conversations_mark`
- `reactions_add`
- `reactions_remove`
- `conversations_join`
- `conversations_leave`
- `usergroups_create`
- `usergroups_list`
- `usergroups_me` with `action=list`
- `usergroups_me` with `action=join`
- `usergroups_update`
- `usergroups_users_update`

### Now success-proven in native harness

- `attachment_get_data`
- `saved_list`
- `saved_update`
- `saved_clear_completed`
- `usergroups_me` with `action=leave`
  Proven with a two-member fixture because Slack rejects attempts to update a group to an empty member list.

## Harness contract recommendation

Future black-box harness work should treat the tool surface as a contract with four fields per tool:

- `exposed`
- `schema`
- `success_path_status`
- `known_failure_modes`

The end-state canonical contract should also capture:

- fixture expectations where a success path depends on pre-created Slack state

That is more useful than treating tool presence alone as verification.

Important distinction:

- runtime validation records the observed behaviour of dated runtimes
- the Python contract harness should assert the intended final product behaviour
- known current defects should be documented as current-state findings, not preserved as the default end-state contract

Current harness decision:

- the first Python contract harness should cover the full 22-tool validated live-runtime surface
- the harness should target the intended fixed end state for that 22-tool surface, not freeze known transitional defects by default

Current contract-definition decision:

- each tool needs a canonical end-state contract covering exposure, arguments/schema, success-path behaviour and output shape, intentional failure modes, and fixture expectations where needed

## Current compatibility target

Current decision:

- the repository's current target surface is the 22-tool validated live-runtime surface

This is both:

- the current harness target
- the default compatibility target for the supported Python-only implementation

Implication:

- repair work and harness engineering should target the 22-tool validated live-runtime surface first
- later product changes should preserve that surface unless an explicit product decision approves a contract change

## Resources

Validated live runtime resources:

- `slack://<workspace>/channels`
- `slack://<workspace>/users`

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
