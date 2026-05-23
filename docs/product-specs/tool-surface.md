# Tool Surface

## Purpose

This document is the canonical end-state product contract for the Slack MCP tool surface.

It should define the intended final behavior of the local Python-only implementation, not merely describe transitional runtime observations.

## Scope

This spec is the authoritative source for the full 22-tool supported surface.

Resource policy:

- the two validated resources, `slack://<workspace>/channels` and `slack://<workspace>/users`, should remain in the final product as first-class supported surface
- resources are convenience discovery surfaces, not the primary contract center of the product
- resources should also normalize toward schema-first structured output rather than preserving CSV as the main end-state contract

Admission policy:

- all 22 validated live-runtime tools remain in intended end-state scope
- the goal is to admit all 22 tools into the final contract rather than quietly leaving hard-to-validate tools outside scope

Current status:

- all 22 validated tools are now implemented in the supported Python-native runtime
- the remaining contract work is about tightening normative behavior definitions, not about tool-surface migration

Per-tool contract definition must cover:

- exposure
- arguments and schema
- success-path behavior
- output shape
- intentional failure modes
- fixture expectations where a success path depends on pre-created Slack state

Output-shape policy:

- the final product should standardize tool outputs into one explicit response style wherever practical
- schema-first structured outputs are the default contract target
- human-readable text should be secondary to structured output
- mixed legacy response formats are migration debt unless explicitly preserved by product decision

Each tool should use the same fixed contract template.

A tool should not be admitted into the final end-state contract until its intended success path has been proven or otherwise resolved to the repository's standard.

## Relationship to other docs

- [tool-reference.md](../tool-reference.md)
  tracks current-state comparison, validation status, and mismatch analysis
- [rewrite-compatibility-contract.md](rewrite-compatibility-contract.md)
  should describe how the harness and migration enforce this product contract
- [auth-model.md](auth-model.md)
  defines auth assumptions that apply across the tool surface

## Current structural decision

- keep this as one repo-wide canonical contract file for all 22 tools
- do not split by domain unless the surface becomes too large to manage cleanly
- use one fixed per-tool template across the whole file
