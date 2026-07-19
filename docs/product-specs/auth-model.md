# Auth Model

## Product question

How should a user authenticate the local Slack MCP server to Slack, and how should an MCP client authenticate to the server?

## Slack-side auth target

Only supported Slack auth for the final local Python product:

- `SLACK_MCP_XOXC_TOKEN`
- `SLACK_MCP_XOXD_TOKEN`

This is the intended final product contract, not a statement that every inherited runtime path already conforms to it yet.

## Client-to-server auth target

Primary supported MCP client auth:

- bearer token via `SLACK_MCP_API_KEY`
- generic aliases may remain for compatibility, but should not be the centre of docs

## Desired operational behaviour

- startup fails clearly if required Slack auth values are missing
- startup fails clearly if conflicting legacy token modes are supplied
- health and doctor outputs report auth mode without exposing secrets
- docs describe the only supported setup first and push legacy material out of the main path

## Current known gaps

- historical evidence docs still mention broader token behaviour because they record dated runtime observations
- browser-session credentials remain a high-trust local secret and require careful operator handling

## Final auth decision

- final supported Slack-side auth is `xoxc` plus `xoxd` only
- `xoxp`, `xoxb`, and other inherited token paths are legacy or transitional only

## Validation references

- [../runtime-validation-2026-05-23-native-bootstrap.md](../runtime-validation-2026-05-23-native-bootstrap.md)
- [../runtime-validation-2026-05-16.md](../runtime-validation-2026-05-16.md)
- [../refactor-and-repair-plan.md](../refactor-and-repair-plan.md)
