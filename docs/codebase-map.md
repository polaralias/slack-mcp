# Codebase Map

## Status

This file is now a lightweight current-state map for the native Python repository.

Older deep archaeology about the removed Go and npm runtime paths has been superseded by dated evidence docs and the rewrite/harness records.

## Current repository shape

### Runtime and serving

- [server.py](../server.py)
  Public FastMCP server, health routes, auth wiring, tool/resource registration, and harness-only helper tools.
- [slack_native.py](../slack_native.py)
  Native Slack session client, mapping logic, and CSV/JSON shaping helpers.
- [backend_runtime.py](../backend_runtime.py)
  Native runtime auth validation and tool-selection configuration helpers.
- [scripts/run_server.py](../scripts/run_server.py)
  Operator helper for `serve`, `doctor`, and `url`.
- [fastmcp.json](../fastmcp.json)
  FastMCP launcher metadata.

### Tests and harness

- [tests/test_harness_bootstrap.py](../tests/test_harness_bootstrap.py)
  Runtime bootstrap and MCP surface assertions.
- [tests/test_read_paths.py](../tests/test_read_paths.py)
  Stable read-path and surface restriction assertions.
- [tests/test_fixture_sensitive_paths.py](../tests/test_fixture_sensitive_paths.py)
  Fixture-sensitive write, attachment, saved-item, and usergroup validation.
- [tests/test_runtime_config.py](../tests/test_runtime_config.py)
  Native runtime configuration guardrails.
- [tests/harness](../tests/harness)
  Shared runtime, discovery, normalization, and tool-schema helpers.

### Packaging and operations

- [pyproject.toml](../pyproject.toml)
  Python package metadata.
- [Dockerfile](../Dockerfile)
  Native Python container build.
- [docker-compose.yml](../docker-compose.yml)
  Compose deployment for the supported runtime.
- [.github/workflows/unit-tests.yaml](../.github/workflows/unit-tests.yaml)
  Native Python test workflow.

## Runtime truth

- Supported runtime: Python-native only
- Supported contract surface: 22 tools, 2 resources
- Historical packaged-backend and Go evidence remains in dated docs only

## Read next

- [../ARCHITECTURE.md](../ARCHITECTURE.md)
- [product-specs/runtime-modes.md](product-specs/runtime-modes.md)
- [exec-plans/active/contract-harness.md](exec-plans/active/contract-harness.md)
