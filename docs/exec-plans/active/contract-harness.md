---
type: "Product Contract"
title: "Contract Harness"
description: "Documents Contract Harness for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - slack-mcp
  - product-contract
navigation:
  role: foundational
  order: 20
---
# Contract Harness

## Objective

Create the first Python black-box MCP contract harness for development work in this repository.

The harness must support repair and rewrite work without collapsing the distinction between:

- current observed runtime behaviour
- intended final product contract
- remaining proof gaps

## Current verified state

- canonical current runtime is Python-native FastMCP
- the validated live-runtime target is 22 tools plus 2 resources
- canonical product and design docs now exist for auth, tool surface, runtime modes, and sandbox validation
- a canonical sandbox fixture catalogue exists for fixture-sensitive proof closure

## Current gap

The harness exists and is green. The remaining gap is not harness existence, but stronger admission of final-contract assertions versus broad observed-runtime coverage.

## Required harness shape

### Boundary

- test only at the Python MCP boundary
- use the user-facing FastMCP server as the subject under test
- do not make backend-internal assertions part of the primary contract suite

### Layers

- observed-surface coverage for the full 22-tool live-runtime target and validated resources
- final-contract assertions for tools and resources admitted by proof

### Runtime

- default harness target is the native Python runtime
- each run must capture `doctor` output alongside results

### Fixtures

- use the canonical sandbox fixture catalogue before adding fixture-sensitive assertions
- keep fixture setup and cleanup explicit and repeatable

## Initial implementation slices

### Slice 1: harness bootstrap

- stand up a Python test runner and test layout
- add shared helpers to start the local FastMCP server
- capture `python scripts/run_server.py doctor` output per run
- assert health endpoint and MCP connectivity

### Slice 2: observed-surface inventory coverage

- assert tool exposure for the full 22-tool live-runtime target
- assert resource exposure for `slack://<workspace>/channels` and `slack://<workspace>/users`
- record mismatches against canonical docs as failures

### Slice 3: stable read-path assertions

- add black-box assertions for currently verified read-oriented success paths first
- prefer low-fixture or fixture-free coverage before write-heavy slices

### Slice 4: write-path and fixture-sensitive closure

- add write-path assertions for already validated write flows
- close proof gaps for attachments and saved items using canonical fixtures
- keep currently problematic paths visible as explicit gaps or expected current-state findings until product decisions or fixes land

### Slice 5: final-contract admission

- promote tools from observed coverage into final-contract assertions only when proof is strong enough
- keep admission status explicit per tool or resource

## Deliverables

- Python test harness checked into the repository
- shared runtime and client helpers for black-box MCP assertions
- one canonical mapping from tool/resource surfaces to harness coverage status
- reproducible fixture handling for currently unproven surfaces
- dated evidence updates when new real-runtime validation occurs

## Current implementation status

Implemented now:

- Slice 1 bootstrap test helper under `tests/harness/runtime.py`
- shared live-test base class under `tests/harness/base.py`
- shared normalisation helpers under `tests/harness/normalize.py`
- env-driven harness input helpers under `tests/harness/inputs.py`
- canonical observed-surface inventory constants under `tests/harness/contract.py`
- black-box bootstrap suite under `tests/test_harness_bootstrap.py`
- stable read-path suite under `tests/test_read_paths.py`
- fixture-sensitive suite scaffolding under `tests/test_fixture_sensitive_paths.py`
- subprocess startup through `python scripts/run_server.py serve`
- per-run `doctor` capture before server startup
- health endpoint and MCP connectivity assertions
- exact 22-tool observed-surface assertions
- exact 2-resource observed-surface assertions with workspace-agnostic URI checks
- stable read-path assertions for channels, users, conversations, usergroups, and resources
- fixture-gated attachment and saved-item assertions using live tool schemas plus env-provided fixture values
- harness-only wrapper utility tool `harness_upload_text_file` can be enabled for attachment proof closure without widening the canonical public contract
- harness-only wrapper utility tool `harness_save_message_for_later` can be enabled for saved-item proof closure without widening the canonical public contract
- harness diagnostics now report active Python-native tool overrides through doctor and health output
- the native Python FastMCP server now boots as the only supported runtime path
- native `channels_list`, native `channels_me`, and native channels/users resources are implemented and proven in a backend-free bootstrap slice
- native `conversations_history`, `conversations_replies`, `conversations_search_messages`, and `conversations_unreads` are implemented and proven in backend-free mode
- native `saved_list`, `saved_update`, and `saved_clear_completed` are implemented and proven in backend-free mode
- native `conversations_add_message`, `conversations_join`, `conversations_leave`, `conversations_mark`, `reactions_add`, and `reactions_remove` are implemented and proven in backend-free mode
- native `attachment_get_data` is implemented and proven in backend-free mode
- native `usergroups_create`, `usergroups_list`, `usergroups_me`, `usergroups_update`, and `usergroups_users_update` are implemented and proven in backend-free mode
- harness diagnostics now report active Python-native resources through doctor and health output
- the harness no longer depends on Go, npm, or delegated backend selection code

Not implemented yet:

- final-contract admission assertions

## Harness environment inputs

Stable read-path tests use:

- `SLACK_MCP_HARNESS_USERS_SEARCH_QUERY`
- `SLACK_MCP_HARNESS_HISTORY_CHANNEL_ID`
- `SLACK_MCP_HARNESS_REPLIES_CHANNEL_ID`
- `SLACK_MCP_HARNESS_REPLIES_THREAD_TS`
- `SLACK_MCP_HARNESS_SEARCH_QUERY`

Fixture-sensitive tool calls use:

- `SLACK_MCP_HARNESS_TOOL_<TOOL_NAME_UPPER>_<ARG_NAME_UPPER>`

Example:

- `SLACK_MCP_HARNESS_TOOL_ATTACHMENT_GET_DATA_FILE_ID`
- `SLACK_MCP_HARNESS_TOOL_SAVED_UPDATE_ITEM_ID`
- `SLACK_MCP_HARNESS_TOOL_SAVED_UPDATE_TS`

Attachment note:

- `attachment_get_data` success-path proof can now be generated without a manual file fixture by enabling the harness-only `harness_upload_text_file` utility during the test run

Saved-item note:

- saved-item success-path proof can now be generated without manual saved fixtures by enabling the harness-only `harness_save_message_for_later` utility during the test run

Current test entrypoint:

- `uv run python -m unittest tests.test_runtime_config tests.test_harness_bootstrap tests.test_read_paths tests.test_fixture_sensitive_paths`

Current evidence:

- [../../runtime-validation-2026-05-22-harness.md](../../runtime-validation-2026-05-22-harness.md)
- [../../runtime-validation-2026-05-23-native-bootstrap.md](../../runtime-validation-2026-05-23-native-bootstrap.md)

Current full-suite status:

- `uv run python -m unittest tests.test_runtime_config tests.test_harness_bootstrap tests.test_read_paths tests.test_fixture_sensitive_paths -v`
- 29 tests run
- 29 passed
- 0 failures

## Acceptance criteria

- a fresh agent can identify the harness entrypoint and build order from tracked docs alone
- the harness targets the Python MCP boundary, not backend internals
- the harness distinguishes observed-surface coverage from final-contract admission
- runtime mode and doctor diagnostics are captured per run
- fixture-sensitive surfaces use the canonical sandbox fixture catalogue

## Read next

- [../../product-specs/tool-surface.md](../../product-specs/tool-surface.md)
- [../../product-specs/rewrite-compatibility-contract.md](../../product-specs/rewrite-compatibility-contract.md)
- [../../product-specs/runtime-modes.md](../../product-specs/runtime-modes.md)
- [../../product-specs/sandbox-validation.md](../../product-specs/sandbox-validation.md)
- [sandbox-fixture-catalog.md](sandbox-fixture-catalog.md)
- [../../runtime-validation-2026-05-16.md](../../runtime-validation-2026-05-16.md)

## Repository knowledge

- [Documentation map](../../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
