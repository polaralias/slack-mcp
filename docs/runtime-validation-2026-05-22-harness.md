# Runtime Validation 2026-05-22 Harness

## Scope

This validation exercised the Python black-box contract harness against the live Slack-backed package runtime on 2026-05-22.

Runtime under test:

- Python FastMCP wrapper from this repository
- backend mode: `package`
- backend source: `npx --package slack-mcp-server@latest`

Slack auth used:

- browser-session credentials via `SLACK_MCP_XOXC_TOKEN`
- browser-session credentials via `SLACK_MCP_XOXD_TOKEN`

## Important distinction

This validation proves current observed behavior of the harness target runtime.

It does not by itself admit final-contract behavior for the future Python-only rewrite.

## Harness configuration used

The harness forced these environment variables so validation targeted the full contract surface:

- `SLACK_MCP_ENABLED_TOOLS=all`
- `SLACK_MCP_ADD_MESSAGE_TOOL=1`
- `SLACK_MCP_REACTION_TOOL=1`
- `SLACK_MCP_ATTACHMENT_TOOL=1`

Why this matters:

- without the explicit gate variables, the package runtime exposed only 18 tools in the initial harness pass on 2026-05-22
- with the explicit gate variables, the package runtime exposed the full 22-tool live-runtime surface

That difference is current observed runtime behavior and should not be silently collapsed into the simpler root setup story.

## Harness results

Full-suite command:

- `uv run python -m unittest tests.test_harness_bootstrap tests.test_read_paths tests.test_fixture_sensitive_paths -v`

Full-suite result after the first native `users_search` slice landed:

- 19 tests run
- 19 passed
- 0 skipped
- 0 failures

### Bootstrap suite

Command:

- `uv run python -m unittest tests.test_harness_bootstrap -v`

Result:

- passed

What this proved:

- the Python wrapper starts cleanly against the package runtime
- the health endpoint works
- MCP connectivity works
- the expected 22-tool surface is exposed when the harness enables the write and attachment gates
- the expected 2-resource surface is exposed

### Stable read-path suite

Command:

- `uv run python -m unittest tests.test_read_paths -v`

Result:

- passed

What this proved:

- `channels_list`
- `channels_me`
- `users_search`
- `conversations_history`
- `conversations_replies`
- `conversations_search_messages`
- `conversations_unreads`
- `usergroups_list`
- `usergroups_me` with `action=list`
- both validated resources

The suite auto-discovered stable workspace inputs from the live runtime rather than depending on manual env values for these read-path assertions.

Additional native-slice proof:

- enabling `SLACK_MCP_NATIVE_USERS_SEARCH=1` caused the Python wrapper to report `users_search` as a Python-native override in both doctor and health output
- under that flag, the server still exposed the exact validated 22-tool surface
- under that flag, `users_search` still returned a successful payload through the MCP boundary

### Fixture-sensitive suite

Command:

- `uv run python -m unittest tests.test_fixture_sensitive_paths -v`

Result:

- partial pass with expected skips

What this proved:

- `saved_list` executed successfully in the live harness
- `harness_upload_text_file` successfully uploaded a UTF-8 text file through Slack's external upload flow
- `attachment_get_data` successfully retrieved that uploaded file by returned `file_id`
- `harness_save_message_for_later` successfully created a saved-item fixture through `stars.add`
- `saved_update` successfully moved that fixture through active and completed saved-item states
- `saved_clear_completed` successfully cleared the completed saved-item fixture

Important saved-item finding:

- `stars.add` creates a Later item that initially appears under the `archived` filter
- setting a future `date_due` through `saved_update` moves that fixture into the `saved` filter for the current private `saved.*` runtime
- marking the item completed then exposes it through the `completed` filter, after which `saved_clear_completed` succeeds

## Current verified state after this pass

- the harness bootstrap is implemented and runnable
- the observed-surface inventory assertion is working
- the stable read-path slice is proven against the live package runtime
- the first Python-native replacement slice is proven for `users_search` behind a runtime flag
- attachment success-path proof is now closed through the harness-only upload helper
- saved-item proof closure is now automated through the harness-only save helper plus the public `saved_*` tools

## Current open items

- decide where current observed gate-dependent exposure behavior should be reflected in broader contributor-facing configuration docs

## Relationship to other docs

- [exec-plans/active/contract-harness.md](exec-plans/active/contract-harness.md)
- [exec-plans/active/sandbox-fixture-catalog.md](exec-plans/active/sandbox-fixture-catalog.md)
- [runtime-validation-2026-05-16.md](runtime-validation-2026-05-16.md)
- [product-specs/sandbox-validation.md](product-specs/sandbox-validation.md)
