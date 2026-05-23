# 1. Authentication Setup

## Purpose

This document describes the current canonical authentication model for this repository.

It replaces the earlier mixed-token setup guidance as the main entrypoint for contributors working in this repo.

References:

- [product-specs/auth-model.md](product-specs/auth-model.md)
- [design-docs/auth-principles.md](design-docs/auth-principles.md)
- [SECURITY.md](SECURITY.md)

## Current canonical model

For this repository, the primary supported Slack auth model is:

- `SLACK_MCP_XOXC_TOKEN`
- `SLACK_MCP_XOXD_TOKEN`

This matches:

- the current Python wrapper constraints
- the validated sandbox runtime work in this repo
- the current supported product runtime

## What this means

If you are developing or verifying this repository locally, assume:

- browser-session style Slack access is the supported setup path
- bearer auth between MCP client and server is configured separately
- legacy token modes may still appear in inherited docs or code, but they are not the preferred setup path here

## Required environment variables

Slack access:

- `SLACK_MCP_XOXC_TOKEN`
- `SLACK_MCP_XOXD_TOKEN`

Recommended MCP client auth:

- `SLACK_MCP_API_KEY`

## How to obtain the Slack values

### `SLACK_MCP_XOXC_TOKEN`

1. Open Slack in your browser and log in.
2. Open browser developer tools.
3. Open the console.
4. Run:

```js
JSON.parse(localStorage.localConfig_v2).teams[document.location.pathname.match(/^\/client\/([A-Z0-9]+)/)[1]].token
```

5. Copy the browser token value.

### `SLACK_MCP_XOXD_TOKEN`

1. In developer tools, open browser storage/cookies.
2. Find the Slack cookie named `d`.
3. Copy its value.
4. Store it as `SLACK_MCP_XOXD_TOKEN`.

## MCP client auth

The server can require a bearer token from MCP clients.

Recommended:

- set `SLACK_MCP_API_KEY`
- connect clients with `Authorization: Bearer <your-api-key>`

## Example local `.env`

```env
SLACK_MCP_XOXC_TOKEN=<paste-slack-browser-token>
SLACK_MCP_XOXD_TOKEN=<paste-slack-cookie-d-value>
SLACK_MCP_API_KEY=change-me
```

## What is not the main path here

Older inherited materials describe:

- `SLACK_MCP_XOXP_TOKEN`
- `SLACK_MCP_XOXB_TOKEN`

Those paths may still appear in inherited historical docs, but they are not the canonical auth story for this repository and should not be the main contributor path.

## Validation status

This auth model was used successfully during authenticated runtime verification in the sandbox workspace.

Reference:

- [runtime-validation-2026-05-16.md](runtime-validation-2026-05-16.md)

## Next

- [02-installation.md](02-installation.md)
