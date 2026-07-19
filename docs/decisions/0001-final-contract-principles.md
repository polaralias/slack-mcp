# Decision 0001: Final Contract Principles

## Status

Accepted

## Context

The repository entered repair work with three conflicting truths:

- local checked-in Go code
- npm packaged runtime behaviour
- inherited and partially drifted documentation

The rewrite needed clear end-state principles before implementation and harness work could be considered trustworthy.

## Decision

The repository's final end-state principles are:

- final production runtime is local Python/FastMCP only
- Go runtime support and retained Go product code are removed from supported product code
- the npm package backend has been retired from supported product code
- the intended final supported tool surface remains the full 22-tool validated live-runtime scope unless an explicit product decision removes a tool
- tools are admitted into the final contract only once success-path proof is established
- the harness must distinguish observed-surface coverage from admitted final-contract assertions
- final outputs should normalise towards schema-first structured responses rather than preserve mixed legacy formats by default
- final Slack-side auth support is `xoxc` plus `xoxd` only
- validated resources remain in final scope as convenience discovery surfaces, not the product centre
- proof closure for currently unproven surfaces is a required pre-rewrite gate

## Consequences

- runtime-validation docs record transitional current-state truth, but they do not define the final contract by themselves
- canonical product behaviour belongs in product-spec docs
- rewrite compatibility and fixture machinery belong in separate compatibility and execution docs
- fixture-sensitive surfaces such as attachments and saved items need explicit sandbox catalogue coverage before final-contract admission

## Canonical references

- [../product-specs/tool-surface.md](../product-specs/tool-surface.md)
- [../product-specs/rewrite-compatibility-contract.md](../product-specs/rewrite-compatibility-contract.md)
- [../refactor-and-repair-plan.md](../refactor-and-repair-plan.md)
