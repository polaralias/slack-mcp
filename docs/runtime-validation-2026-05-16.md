# Runtime Validation 2026-05-16

## Scope

This validation used real Slack browser-session credentials against a private sandbox workspace.

The verification target was the runtime actually served by this repository on this machine:

- Python FastMCP wrapper from this repo
- backend mode: `package`
- backend source: `npx --package slack-mcp-server@latest`

Important consequence:

- these results validate the Python wrapper and the live packaged backend path
- these results do **not** prove that the checked-in local Go source in this repository matches the runtime that was exercised
- these results document current observed behavior, not the approved final end-state contract for the Python rewrite

## Environment

- Python available: yes
- `uv` available: yes
- Node/npm/npx available: yes
- Go available on PATH: no
- Docker available on PATH: no

## High-signal finding

The live backend surface does not match the local repository’s documented and checked-in tool surface.

Observed live tool count: 22

Observed live tools:

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

This is materially different from the 16-tool surface described in [docs/tool-reference.md](tool-reference.md) and the historical local registration in `pkg/server/server.go`.

## Verified resources

- `slack://<sandbox-workspace>/channels`
  Returned valid CSV data
- `slack://<sandbox-workspace>/users`
  Returned valid CSV data

## Tool results

### Verified success paths

- `channels_list`
  Returned 5 channels/DMs from the sandbox workspace.
- `channels_me`
  Returned 3 joined public channels.
- `users_search`
  Returned the current test user.
- `conversations_history`
  Returned recent messages from the primary sandbox validation channel.
- `conversations_add_message`
  Successfully posted a top-level message to the primary sandbox validation channel.
- `conversations_replies`
  Successfully returned a thread containing both a parent message and a reply created during the run.
- `conversations_search_messages`
  Successfully found both the earlier diagnostic message and the newly created validation messages.
- `conversations_unreads`
  Returned unread summary data.
- `conversations_mark`
  Successfully marked the test channel as read up to the created message timestamp.
- `reactions_add`
  Successfully added `:rocket:` to the test message.
- `reactions_remove`
  Successfully removed `:rocket:` from the test message.
- `conversations_leave`
  Successfully left `#new-channel`.
- `conversations_join`
  Successfully re-joined `#new-channel`.
- `usergroups_create`
  Successfully created a disposable test user group.
- `usergroups_update`
  Successfully updated that group’s handle and description.
- `usergroups_me` with `action=list`
  Returned valid CSV output before and after mutations.
- `usergroups_me` with `action=join`
  Successfully joined the created group.
- `usergroups_users_update`
  Successfully replaced the group membership with the current user.

### Verified error paths or failures

- `attachment_get_data`
  No valid recent file fixture was found in scanned message history, so success-path validation could not be completed.
  The error path was exercised with an invalid file ID and returned `file_not_found`.
- `saved_list`
  Tool executed successfully, but the sandbox workspace had no saved items.
- `saved_update`
  No valid saved-item fixture existed for success-path validation.
  The error path was exercised and returned `saved_not_found`.
- `saved_clear_completed`
  Tool executed but returned `failed to clear completed saved items: fatal_error` in the empty-fixture state.
  This should be treated as a candidate bug or unsupported edge case.
- `usergroups_me` with `action=leave`
  Repeatedly returned `invalid_arguments`, even when tested on a freshly created group that the current user had just joined.
  This should be treated as a candidate bug or an undocumented Slack-side constraint.

## Test artifacts created in Slack

Messages created in the primary sandbox validation channel:

- diagnostic message: `diagnostic write probe`
- validation parent message with a run-specific token
- validation thread reply with the same run-specific token

User groups created:

- one disposable validation group for update and membership tests
- one disposable validation group for leave-behavior checks

These were intentionally created as disposable verification artifacts.

## Behavioral notes

- `conversations_add_message` in the live packaged backend returns plain success text with timestamps, not the CSV message row behavior present in the local checked-in handler code.
- Search appears to have at least mild freshness/indexing delay. The first broad search immediately after posting did not return results, while a subsequent retry did.
- `channels_me` reported `MemberCount` as `0` for joined public channels in the sandbox output, which may be a formatting or mapping issue rather than a true count.

## Conclusions

### What is proven

- The Python FastMCP wrapper in this repo works end-to-end with real Slack credentials.
- The npm package backend fallback is operational on this machine.
- Most read surfaces and most write surfaces exposed by the live backend are functional in the sandbox workspace.

### What is not proven

- The local Go source in this repository matches the behavior of the live packaged backend.
- The local Go runtime path works at all on this machine.
- The Docker deployment path works on this machine.
- Success-path attachment retrieval and saved-item mutation are valid in the current sandbox workspace.

### What should be treated as active findings

- Local repo surface and live packaged surface are out of sync.
- `usergroups_me leave` appears broken or constrained.
- `saved_clear_completed` appears broken or under-specified in the empty-fixture case.
