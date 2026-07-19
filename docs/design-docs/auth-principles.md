# Auth Principles

## Purpose

This document defines the desired end state for authentication and authorisation in the rewritten Python-only server.

It does not describe every legacy token path that may still exist in inherited code or package artefacts.

## Desired end state

The long-term local Python server should support exactly one clearly documented Slack auth model.

Final supported auth model:

- browser-session derived Slack access using `xoxc` plus `xoxd`

Reasons:

- it matches the currently validated sandbox flow
- it aligns with the repo’s current Python wrapper constraints
- it avoids pretending multiple legacy token modes are equally supported when they are not verified here

## Design constraints

- Slack auth model must be explicit at startup.
- Unsupported token modes must fail fast.
- Auth provenance must be visible in diagnostics.
- Docs must separate:
  - supported
  - legacy
  - unverified

## Security principles

- Tokens must never be written to repo docs or committed config.
- Diagnostic tools should confirm presence and mode, not echo secrets.
- Tool exposure and Slack workspace mutation controls must be configured separately from Slack credential presence.

## Migration note

Legacy docs currently describe `xoxp` and `xoxb` support. Those paths may continue to exist in inherited code or packaged artefacts during migration, but they are not part of the final supported auth contract for the local Python rewrite.

References:

- [../product-specs/auth-model.md](../product-specs/auth-model.md)
- [../SECURITY.md](../SECURITY.md)
- [../../backend_runtime.py](../../backend_runtime.py)
