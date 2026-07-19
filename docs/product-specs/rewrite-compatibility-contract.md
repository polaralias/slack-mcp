# Rewrite Compatibility Contract

## Purpose

This document defines how the repository preserves the intended end-state product contract now that the Python rewrite has replaced the transitional runtime dependencies.

It is not the per-tool normative behaviour spec. That belongs in:

- [tool-surface.md](tool-surface.md)

## Scope

This spec should describe:

- what the rewrite must preserve from the canonical tool surface
- how the harness validates preservation
- how transitional runtime observations relate to the target contract
- how temporary migration gaps are identified and retired
- a clear separation between:
  - current validated runtime behaviour
  - target end-state behaviour
  - accepted temporary migration gaps
- a two-layer harness model:
  - observed-surface coverage for all 22 validated live-runtime tools
  - final-contract assertions for tools admitted by proof
- how legacy mixed output formats are normalised into the final schema-first contract
- a separate but parallel treatment of resources versus tools in coverage and final-contract admission
- proof closure requirements for currently unproven surfaces before those surfaces count as admitted final contract

## Rewrite target

The rewrite target is one native Python FastMCP server that owns the Slack integration directly.

That target means:

- no Go runtime path in supported product code
- no npm package backend in supported product code
- no delegated backend process behind the FastMCP server
- no contract dependency on externally packaged backend artefacts for tool availability

This document treats the historical package-backed runtime only as a transition reference and validation source.

## Canonical preservation rules

The rewrite must preserve these external truths unless an explicit product decision changes them:

- the full 22-tool validated live-runtime scope remains the default compatibility target
- the two validated `slack://<workspace>/channels` and `slack://<workspace>/users` resources remain in scope
- auth remains browser-session based through `xoxc` plus `xoxd`
- MCP behaviour is preserved at the Python server boundary, not by file-for-file backend porting

The rewrite does not need to preserve:

- Go package structure
- npm launcher behaviour
- mixed text-first legacy output formats
- transitional gate quirks that only exist because the current runtime is package-backed

## Dependency rules

The final runtime must not depend on:

- checked-in Go product code
- `npx`
- externally resolved npm package binaries
- sidecar backend processes for core Slack tool execution

Current note:

- the repository may still use Python packages as implementation dependencies
- the forbidden dependency class here is external backend runtime delegation, not ordinary Python packaging

## Migration model

The migration happened by behaviour slice behind the contract harness:

1. auth and session plumbing
2. Slack web-client request helpers
3. read tools
4. write tools
5. saved-item tools
6. attachments
7. usergroup tools
8. resource normalisation

Those slices replaced package-backed behaviour with Python-native behaviour without widening the public contract surface.

## Harness enforcement

The contract harness enforces migration in two layers:

- observed-surface coverage for the full transitional 22-tool runtime
- final-contract assertions for proven end-state behaviour

Any future contract-affecting slice should meet the same bar:

- the Python path satisfies the same MCP boundary assertions
- fixture-sensitive success paths are proven where required
- current-state evidence and canonical docs stay aligned in the same tranche

## Transitional exceptions

Harness-only helper tools may exist during validation when they are needed to create or clean up sandbox fixtures.

Rules for those helpers:

- they are not part of the public contract
- they must be explicitly gated
- they may target deprecated or private Slack endpoints when that is necessary for proof closure
- they should be removed or retained only as internal validation infrastructure, not promoted into product support claims

Current examples:

- `harness_upload_text_file`
- `harness_save_message_for_later`

## Current structural decision

- keep this document separate from the canonical per-tool contract
- use this document for migration, harness, and preservation rules rather than duplicating tool-by-tool behaviour definitions
- do not treat unproven success paths as fully admitted final-contract behaviour
- keep all 22 tools in rewrite scope unless an explicit product decision removes one
- treat plain-text success outputs in transitional runtimes as migration mismatches to retire unless explicitly preserved
- keep fixture catalogue and proof-closure procedures in execution or harness docs rather than product-spec docs
