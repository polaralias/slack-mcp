# Handoff: python-rewrite-harness

## Session Goal

Complete the Python-native replacement of the validated 22-tool runtime while preserving the black-box contract harness.

## Current State

The repository now has an explicit rewrite contract: one native Python FastMCP server, no Go runtime, no npm backend, and no delegated external backend process in the final product shape.

Saved-item proof closure is now automated in the harness:

- `harness_save_message_for_later` in [server.py](../../server.py) creates a Save for Later fixture through `stars.add`
- the live `saved_update` tool moves that fixture into active and completed states
- the live `saved_clear_completed` tool clears the completed fixture

The fixture-sensitive suite is now fully automated and no longer depends on the deleted manual `attachment_get_data` file-id fixture test.

The Python-native runtime now covers the full validated surface, and the repository has removed the old delegated backend path from supported product code.

The server now starts as a native-only runtime:

- all 22 validated tools and the 2 validated resources are proven under the native Python implementation
- full-surface canonical validation no longer depends on the npm package backend

This session depends on local uncommitted state.

## Verification State

Verified live on 2026-05-23 with local Slack browser-session credentials present in the shell environment:

- `uv run python -m compileall tests server.py slack_native.py scripts/run_server.py backend_runtime.py`
- `uv run python -m unittest tests.test_read_paths.StableReadPathTests.test_native_runtime_exposes_full_validated_surface_without_backend -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths.FixtureSensitivePathTests.test_native_runtime_supports_write_and_attachment_tools_without_backend -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths.FixtureSensitivePathTests.test_native_runtime_supports_usergroups_tools_without_backend -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths.FixtureSensitivePathTests.test_native_runtime_supports_saved_tools_without_backend -v`
- `uv run python -m unittest tests.test_harness_bootstrap tests.test_read_paths -v`
- `uv run python -m unittest tests.test_fixture_sensitive_paths -v`
- `uv run python -m unittest tests.test_runtime_config tests.test_harness_bootstrap tests.test_read_paths tests.test_fixture_sensitive_paths -v`

Latest full-suite result:

- 29 tests run
- 29 passed
- 0 skips
- 0 failures

Important operational note:

- Slack session credentials were used locally for validation and were shared in thread history; they should be rotated, but no secret values are recorded in this handoff.

## Canonical References

- [AGENTS.md](../../AGENTS.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [docs/PLANS.md](../PLANS.md)
- [docs/refactor-and-repair-plan.md](../refactor-and-repair-plan.md)
- [docs/product-specs/rewrite-compatibility-contract.md](../product-specs/rewrite-compatibility-contract.md)
- [docs/exec-plans/active/contract-harness.md](../exec-plans/active/contract-harness.md)
- [docs/runtime-validation-2026-05-22-harness.md](../runtime-validation-2026-05-22-harness.md)
- [docs/runtime-validation-2026-05-23-native-bootstrap.md](../runtime-validation-2026-05-23-native-bootstrap.md)

## Changes Made

- tightened rewrite target docs to explicitly forbid Go, npm backend, and delegated backend-process end states
- added harness-only `harness_save_message_for_later` helper and runtime flag support
- replaced saved-item manual fixture assumptions with live end-to-end saved-item proof in [tests/test_fixture_sensitive_paths.py](../../tests/test_fixture_sensitive_paths.py)
- removed the redundant manual `attachment_get_data` fixture test
- updated runtime evidence and harness plan docs to reflect automated saved-item proof closure
- added shared native Slack session plumbing in [slack_native.py](../../slack_native.py)
- added a flag-gated native Python `users_search` implementation in [server.py](../../server.py)
- added a harness test proving the native override preserves the exact 22-tool MCP surface in [tests/test_read_paths.py](../../tests/test_read_paths.py)
- added `native` backend mode to the runtime launcher and doctor path
- refactored the server so proxy delegation is optional rather than mandatory
- added native Python implementations for `channels_list`, `channels_me`, and the two validated resources
- added a harness test proving backend-free native bootstrap for the channels/users/resources slice
- added native Python implementations for `conversations_history`, `conversations_replies`, `conversations_search_messages`, and `conversations_unreads`
- expanded the native-only harness proof to cover the conversation read family
- used the upstream zip's saved-item source as a direct implementation reference for the native saved-item tranche
- added native Python implementations for `saved_list`, `saved_update`, and `saved_clear_completed`
- added a fixture-sensitive native-only proof for the saved-item tranche
- added native Python implementations for `conversations_add_message`, `conversations_join`, `conversations_leave`, `conversations_mark`, `reactions_add`, `reactions_remove`, and `attachment_get_data`
- added native Python implementations for `usergroups_create`, `usergroups_list`, `usergroups_me`, `usergroups_update`, and `usergroups_users_update`
- added a full-surface native runtime proof and fixture-sensitive native write, attachment, and usergroup proofs
- removed supported Go runtime code, npm launcher artifacts, and delegated backend selection from the repository
- updated canonical packaging, CI, and documentation to describe the native-only runtime
- added runtime-config tests that guard the no-backend, xoxc/xoxd-only configuration model

## Open Issues Or Risks

- Harness-only helper tools exist for fixture creation and are intentionally not part of the public contract.
- `usergroups_me leave` still depends on Slack accepting a non-empty replacement member list; removing the sole remaining member still triggers Slack `invalid_arguments`, so the native success proof uses a two-member fixture when available.
- The repo has substantial uncommitted documentation and harness changes on `main`; the next session should assume a dirty worktree.

## Suggested Next Step

Move from cleanup to hardening: promote final-contract assertions, trim obsolete historical docs further where useful, and improve packaging/operator ergonomics around the native-only runtime.

## Suggested Skills

- `pickup`
- `repository-knowledge-engineering`
- `tdd`
- `query-to-knowledge`
