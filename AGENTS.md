# AGENTS

## Purpose

This repository is in a native-runtime hardening phase.

Agent work should optimize for:

- repository truth
- reproducible verification
- contract preservation
- maintainability of the Python-only FastMCP implementation

## Current reality

- The user-facing server is Python/FastMCP.
- The runtime implementation is now Python-native end to end.
- Historical Go and npm-backed runtime evidence may still appear in dated documents, but they are not supported product paths.

Canonical entry docs:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/DESIGN.md](docs/DESIGN.md)
- [docs/PLANS.md](docs/PLANS.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/RELIABILITY.md](docs/RELIABILITY.md)

High-signal current-state references:

- [docs/refactor-and-repair-plan.md](docs/refactor-and-repair-plan.md)
- [docs/runtime-validation-2026-05-16.md](docs/runtime-validation-2026-05-16.md)
- [docs/product-specs/auth-model.md](docs/product-specs/auth-model.md)
- [docs/design-docs/auth-principles.md](docs/design-docs/auth-principles.md)

## Working principles

- Treat docs as claims until verified.
- Treat code as intended behavior until tested.
- Prefer black-box MCP boundary validation over implementation assumptions.
- Do not silently collapse distinctions between:
  - current supported Python-native behavior
  - historical runtime evidence
  - desired future contract refinements

## Documentation rules

- New decisions should land in canonical docs under `docs/`.
- Legacy docs should not be deleted until their replacements are complete.
- When a legacy doc is contradicted by validation, note that explicitly in canonical docs.
- Configuration and tool-surface claims must identify whether they describe:
  - canonical intended support
  - validated live runtime support
  - legacy or inherited behavior

## Change rules

- New behavior should be specified in product- or design-level docs before implementation when the behavior is user-visible.
- New tests should prefer Python black-box MCP boundary assertions over backend-internal assumptions.
- Do not reintroduce delegated backend patterns or secondary runtime paths without an explicit product decision and matching contract updates.
