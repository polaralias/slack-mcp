---
type: "Glossary Concept"
title: "Glossary"
description: "Documents Glossary for the slack-mcp repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - slack-mcp
  - glossary-concept
navigation:
  role: foundational
  order: 20
---
# Glossary

This glossary defines the product-language for the supported Python-native Slack MCP server.

It is review-derived from the current repository contract docs, harness docs, and retained evidence so future agents can rely on one domain-language surface even where earlier glossary work was not clearly tracked.

## Language

**Python-Native Runtime**:
The supported end-to-end FastMCP Python server implementation.
_Avoid_: Hybrid runtime, delegated backend path

**Tool Surface**:
The canonical supported set of 22 Slack tools exposed by the repository.
_Avoid_: Transitional wrapper set, inherited runtime leftovers

**Resource Surface**:
The two validated Slack discovery resources, `slack://<workspace>/channels` and `slack://<workspace>/users`.
_Avoid_: Main product contract centre

**Observed Surface**:
The currently exposed runtime surface that the harness checks at the MCP boundary.
_Avoid_: Final contract by assumption

**Final Contract**:
The intended end-state public behaviour the repository is willing to preserve as the supported product.
_Avoid_: Whatever the transitional runtime happens to emit today

**Schema-First Output**:
The preferred contract style where structured output is primary and human-readable text is secondary.
_Avoid_: Mixed ad hoc text responses

**Browser-Session Auth**:
The only supported Slack-side auth story for the product, using `SLACK_MCP_XOXC_TOKEN` and `SLACK_MCP_XOXD_TOKEN`.
_Avoid_: Bot token auth, user-token fallback, legacy mixed auth

**MCP Bearer Auth**:
The supported client-to-server auth story for protecting the MCP endpoint.
_Avoid_: Open endpoint by accident, Slack auth reuse

**Validated Contract Surface**:
The user-visible runtime surface that the repository is willing to claim publicly because it is documented and validated.
_Avoid_: Historical observation, latent code path

**Historical Runtime Evidence**:
Dated validation notes that remain useful as evidence but do not define the active contract by themselves.
_Avoid_: Canonical current guidance

**Harness-Only Helper Tool**:
An internal validation tool used to create or clean up fixtures for proof closure without becoming part of the public product contract.
_Avoid_: Public supported tool

**Fixture-Sensitive Proof**:
Validation that depends on prepared Slack state and therefore needs explicit fixture creation, cleanup, or catalogue rules.
_Avoid_: Assumed success path

## Relationships

- The **Python-Native Runtime** implements the **Tool Surface** and **Resource Surface**
- The **Observed Surface** is what the harness sees at the MCP boundary today
- The **Final Contract** is narrower than raw observation when transitional behaviour has not been admitted yet
- The **Validated Contract Surface** includes the **Tool Surface** and the validated **Resource Surface**
- **Schema-First Output** is the preferred contract direction for the **Tool Surface**
- **Browser-Session Auth** is the only supported Slack-side auth for the **Python-Native Runtime**
- **MCP Bearer Auth** protects the server boundary independently from **Browser-Session Auth**
- A **Harness-Only Helper Tool** may support **Fixture-Sensitive Proof** without joining the **Validated Contract Surface**
- **Historical Runtime Evidence** may explain how the repository got here, but it does not override the **Validated Contract Surface**

## Example dialogue

> **Dev:** "A legacy doc mentions `xoxb`. Is that still a supported auth path?"
> **Domain expert:** "No. That is **Historical Runtime Evidence**. The supported Slack-side auth is **Browser-Session Auth** only."

## Flagged ambiguities

- "runtime" could refer to either the old mixed implementation or the supported one — resolved: **Python-Native Runtime** is the active product path
- validated resources could be mistaken for secondary leftovers — resolved: the **Resource Surface** is supported, but it is not the main contract centre
- the currently observed runtime could be mistaken for the whole intended contract — resolved: distinguish **Observed Surface** from **Final Contract**
- human-readable output could drift into the primary contract shape — resolved: **Schema-First Output** is the intended norm
- Slack auth and MCP auth could be conflated — resolved: **Browser-Session Auth** and **MCP Bearer Auth** are separate layers
- internal fixture helpers could be mistaken for supported tools — resolved: **Harness-Only Helper Tool** is validation infrastructure only
- fixture-dependent runtime success could be treated as self-proving — resolved: **Fixture-Sensitive Proof** requires explicit proof closure
- historical validation notes could be treated as active setup guidance — resolved: they remain **Historical Runtime Evidence**, not canonical contract

## Repository knowledge

- [Documentation map](docs/knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
