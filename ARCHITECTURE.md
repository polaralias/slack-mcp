# Architecture

## Summary

The repository now implements one supported runtime:

1. Python FastMCP server
2. native Slack session/auth and API calls in Python
3. direct tool and resource implementations in Python

## Public surface

- [server.py](server.py)
- [slack_native.py](slack_native.py)
- [backend_runtime.py](backend_runtime.py)
- [fastmcp.json](fastmcp.json)
- [scripts/run_server.py](scripts/run_server.py)

Responsibilities:

- HTTP MCP transport
- bearer-token auth
- health routes
- Slack browser-session auth validation
- tool registration and execution
- resource registration and execution
- runtime diagnostics

## Runtime model

Supported runtime mode:

- `native`

Meaning:

- no Go runtime
- no npm package backend
- no delegated backend process

Current evidence:

- [docs/runtime-validation-2026-05-23-native-bootstrap.md](docs/runtime-validation-2026-05-23-native-bootstrap.md)

## Contract target

- preserve the validated 22-tool MCP surface
- preserve the 2 validated Slack resources
- keep the Python MCP boundary as the contract boundary for tests

## Historical note

Older dated documents may still discuss package-backed or Go-backed runtime behaviour. Those references are retained as evidence of how the contract was established, not as active architecture guidance.
