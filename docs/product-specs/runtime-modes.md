# Runtime Modes

## Purpose

This document defines the supported runtime story for the repository after the Python-native transition.

## Canonical runtime

The supported runtime is:

- Python FastMCP server from this repository
- direct Slack browser-session calls from Python
- no delegated backend process

Current evidence:

- [../runtime-validation-2026-05-23-native-bootstrap.md](../runtime-validation-2026-05-23-native-bootstrap.md)

## Supported mode in code

The launcher now supports one runtime mode:

- `native`

`python scripts/run_server.py doctor` still emits `backend_mode=native` so the harness keeps a stable diagnostic field, but there is no alternate backend resolution path behind it.

## Development rules

- Treat the Python-native runtime as the only supported product runtime.
- Do not reintroduce delegated backend selection through Go binaries, local Go source, or npm packages.
- Historical package-backed validation docs remain evidence only.

## Required diagnostics for runtime-sensitive work

Any harness or validation run should capture:

- `backend_mode`
- enabled-tools mode
- transport
- MCP URL and health URL
- native tool and resource inventory

Current source for that snapshot:

- `python scripts/run_server.py doctor`

## Relationship to other docs

- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [rewrite-compatibility-contract.md](rewrite-compatibility-contract.md)
- [../configuration.md](../configuration.md)
