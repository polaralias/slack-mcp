---
type: "Validation Evidence"
title: "Runtime Validation 2026-05-23 Native Runtime"
description: "Documents Runtime Validation 2026-05-23 Native Runtime for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: evidence
verification: verified-limited
owner: polaralias
tags:
  - slack-mcp
  - validation-evidence
navigation:
  role: reference
  order: 200
---
# Runtime Validation 2026-05-23 Native Runtime

## Scope

This validation exercised the Python-native runtime on 2026-05-23 after the remaining write, attachment, join/leave, and usergroup tools were migrated.

Runtime under test:

- Python FastMCP server from this repository
- backend mode: `native`
- delegated backend process: none

Slack auth used:

- browser-session credentials via `SLACK_MCP_XOXC_TOKEN`
- browser-session credentials via `SLACK_MCP_XOXD_TOKEN`

## Current proof level

This pass proves that the full validated 22-tool contract can now run without the npm package backend.

It does not change the historical fact that the packaged runtime was the original live contract source.

## Native runtime configuration used

Primary full-surface proof used:

- `SLACK_MCP_ENABLED_TOOLS=all`

No delegated backend command was used.

## Targeted native proofs

Commands:

- `uv run python -m unittest tests.test_read_paths.StableReadPathTests.test_native_runtime_exposes_full_validated_surface_by_default -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths.FixtureSensitivePathTests.test_native_runtime_supports_write_and_attachment_tools -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths.FixtureSensitivePathTests.test_native_runtime_supports_usergroups_tools -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths.FixtureSensitivePathTests.test_native_runtime_supports_saved_tools -v`

Result:

- passed

What this proved:

- `python scripts/run_server.py doctor` reports `backend_mode=native`
- doctor reports no delegated backend command
- health output reports `backendMode=native`
- the backend-free native runtime exposes the full validated 22-tool surface:
  - `attachment_get_data`
  - `channels_list`
  - `channels_me`
  - `conversations_add_message`
  - `conversations_history`
  - `conversations_join`
  - `conversations_leave`
  - `conversations_mark`
  - `conversations_replies`
  - `conversations_search_messages`
  - `conversations_unreads`
  - `reactions_add`
  - `reactions_remove`
  - `saved_clear_completed`
  - `saved_list`
  - `saved_update`
  - `usergroups_create`
  - `usergroups_list`
  - `usergroups_me`
  - `usergroups_update`
  - `usergroups_users_update`
  - `users_search`
- the backend-free native runtime exposes the validated resource surface:
  - `slack://<workspace-or-placeholder>/channels`
  - `slack://<workspace-or-placeholder>/users`
- native success paths are now proven for:
  - channels and users
  - conversation reads
  - conversation writes
  - reactions
  - attachments
  - saved items
  - usergroups

## Full-suite check

Commands:

- `uv run python -m compileall tests server.py slack_native.py scripts/run_server.py backend_runtime.py`
- `uv run python -m unittest tests.test_runtime_config tests.test_harness_bootstrap tests.test_read_paths tests.test_fixture_sensitive_paths -v`

Result:

- 29 tests run
- 29 passed
- 0 failures

What this proved:

- the Python-native full-surface runtime is green under the repository's primary black-box harness
- the repository no longer needs the npm package path for contract-complete runtime validation

## Current verified state after this pass

- the repository can now run the full 22-tool contract in true backend-free `native` mode
- the Python FastMCP server has direct Slack session implementations for all validated tools and resources
- the npm package backend is no longer required for full-surface harness validation
- supported runtime guidance is now native-only

## Residual notes

- harness-only helper tools still exist for fixture creation and are intentionally outside the public contract
- `usergroups_me leave` can still fail against Slack if asked to remove the sole remaining member of a group; the native success proof avoided that single-member edge case by using a two-member fixture when available
- resource URIs still use a workspace-placeholder segment when no explicit workspace slug is configured

## Relationship to other docs

- [product-specs/runtime-modes.md](product-specs/runtime-modes.md)
- [exec-plans/active/contract-harness.md](exec-plans/active/contract-harness.md)
- [runtime-validation-2026-05-22-harness.md](runtime-validation-2026-05-22-harness.md)

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
