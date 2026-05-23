# Sandbox Validation

## Purpose

This document defines what sandbox validation proves in this repository and how that evidence relates to the final product contract.

It is not the contract itself.

## Canonical current-state position

Sandbox validation is the repository's current evidence mechanism for real Slack-backed behavior.

It proves:

- observed runtime exposure
- observed schema and argument acceptance
- observed success or failure behavior
- fixture gaps that prevent full proof closure

It does not by itself approve final end-state behavior for the Python rewrite.

## Evidence classes

### Dated runtime evidence

Example:

- [../runtime-validation-2026-05-16.md](../runtime-validation-2026-05-16.md)
- [../runtime-validation-2026-05-23-native-bootstrap.md](../runtime-validation-2026-05-23-native-bootstrap.md)

Use:

- records what a specific runtime did on a specific date
- preserves defects, quirks, and incomplete proof honestly

### Canonical product contract

Examples:

- [tool-surface.md](tool-surface.md)
- [auth-model.md](auth-model.md)

Use:

- defines intended end-state behavior
- should not be rewritten to match transitional defects by default

### Harness execution guidance

Examples:

- [../exec-plans/active/contract-harness.md](../exec-plans/active/contract-harness.md)
- [../exec-plans/active/sandbox-fixture-catalog.md](../exec-plans/active/sandbox-fixture-catalog.md)

Use:

- tells contributors how to turn product and runtime knowledge into repeatable black-box assertions

## Proof model

The repository uses a two-layer proof model:

### Observed-surface coverage

- covers all 22 validated live-runtime tools plus validated resources
- proves what the current canonical runtime exposes and how it behaves today
- may include known defects, mixed output formats, and fixture-specific caveats

### Final-contract admission

- applies only to tools and resources whose intended success path has been proven to repository standard
- asserts the end-state Python contract rather than freezing transitional quirks
- remains separate from broad surface coverage

## Validation status language

Use only these status terms in canonical docs:

- verified working
- verified limited
- known broken
- untested

Use those terms to describe evidence strength, not optimism.

## Required output from a validation slice

Each meaningful validation or harness slice should leave behind:

- updated canonical docs if support truth changed
- updated execution docs if fixture or harness procedures changed
- a dated evidence note if new real-runtime validation happened
- narrowed remaining gaps, not just a generic statement that work continues

## Fixture-sensitive surfaces

The following surfaces require explicit sandbox fixture handling before final-contract admission:

- `attachment_get_data`
- `saved_list`
- `saved_update`
- `saved_clear_completed`
- resource normalization checks that depend on seeded data

Canonical fixture guidance lives in:

- [../exec-plans/active/sandbox-fixture-catalog.md](../exec-plans/active/sandbox-fixture-catalog.md)

## Development rules

- Do not treat a single successful manual run as sufficient harness proof.
- Do not widen support claims from local source inspection alone.
- Do not delete old evidence notes when the contract improves.
- Promote proven behavior into canonical contract docs in the same tranche that makes the proof trustworthy.

## Relationship to other docs

- [rewrite-compatibility-contract.md](rewrite-compatibility-contract.md)
- [tool-surface.md](tool-surface.md)
- [../tool-reference.md](../tool-reference.md)
- [../runtime-validation-2026-05-16.md](../runtime-validation-2026-05-16.md)
