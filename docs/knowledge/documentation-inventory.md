---
type: Repository Documentation Inventory
title: "slack-mcp complete Markdown inventory"
description: "Classifies every in-scope tracked or pending Markdown file in the slack-mcp repository by OKF or approved specialised schema."
timestamp: 2026-07-28T23:00:17Z
authority: derived
verification: verified-working
owner: polaralias
generated_by: repo-knowledge-engineering-census
tags:
  - slack-mcp
  - documentation-inventory
navigation:
  role: supporting
  order: 30
---

# slack-mcp complete Markdown inventory

This is an exhaustive census of every in-scope tracked or pending Markdown file in this repository. Skill package trees (`skills/**`), including `SKILL.md`, references, tests, and bundled sub-documents, are deliberately excluded because they retain the skill-package schema. It proves that each file is either a typed OKF concept, an OKF reserved surface, or an explicitly classified specialised/producer-owned document. It does not duplicate the source content.

## Census result

- In-scope Markdown files: 47
- Excluded skill-package files: 0
- Unclassified files: 0
- Exact duplicate governed knowledge bodies: 0

| Classification | Files |
|---|---:|
| Generated visualization | 1 |
| Generated output | 1 |
| Handoff | 1 |
| OKF execution concept | 1 |
| OKF knowledge concept | 35 |
| Repository instruction | 2 |
| Reserved OKF navigation/history | 6 |

## Completeness

- No Markdown files are unclassified.

## Duplicate check

- No exact duplicate bodies were found among governed OKF knowledge concepts.

## Complete file inventory

| Path | Classification | Format status | Boundary rationale |
|---|---|---|---|
| [`AGENTS.md`](../../AGENTS.md) | Repository instruction | Specialised schema | Instruction authority remains outside factual knowledge |
| [`ARCHITECTURE.md`](../../ARCHITECTURE.md) | OKF knowledge concept | OKF | Architecture Concept |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | Repository instruction | Specialised schema | Instruction authority remains outside factual knowledge |
| [`docs/01-authentication-setup.md`](../01-authentication-setup.md) | OKF knowledge concept | OKF | Security Boundary |
| [`docs/02-installation.md`](../02-installation.md) | OKF knowledge concept | OKF | Reference |
| [`docs/03-configuration-and-usage.md`](../03-configuration-and-usage.md) | OKF knowledge concept | OKF | Reference |
| [`docs/archive/index.md`](../archive/index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`docs/archive/PRODUCT_SENSE.md`](../archive/PRODUCT_SENSE.md) | OKF knowledge concept | OKF | Historical Evidence |
| [`docs/archive/QUALITY_SCORE.md`](../archive/QUALITY_SCORE.md) | OKF knowledge concept | OKF | Historical Evidence |
| [`docs/codebase-map.md`](../codebase-map.md) | OKF knowledge concept | OKF | Architecture Concept |
| [`docs/configuration.md`](../configuration.md) | OKF knowledge concept | OKF | Reference |
| [`docs/decisions/0001-final-contract-principles.md`](../decisions/0001-final-contract-principles.md) | OKF knowledge concept | OKF | Decision |
| [`docs/design-docs/auth-principles.md`](../design-docs/auth-principles.md) | OKF knowledge concept | OKF | Security Boundary |
| [`docs/design-docs/core-beliefs.md`](../design-docs/core-beliefs.md) | OKF knowledge concept | OKF | Design Concept |
| [`docs/design-docs/index.md`](../design-docs/index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`docs/DESIGN.md`](../DESIGN.md) | OKF knowledge concept | OKF | Design Concept |
| [`docs/exec-plans/active/contract-harness.md`](../exec-plans/active/contract-harness.md) | OKF knowledge concept | OKF | Product Contract |
| [`docs/exec-plans/active/sandbox-fixture-catalog.md`](../exec-plans/active/sandbox-fixture-catalog.md) | OKF knowledge concept | OKF | Delivery Plan |
| [`docs/exec-plans/archive/documentation-harness.md`](../exec-plans/archive/documentation-harness.md) | OKF knowledge concept | OKF | Historical Evidence |
| [`docs/exec-plans/tech-debt-tracker.md`](../exec-plans/tech-debt-tracker.md) | OKF knowledge concept | OKF | Delivery Plan |
| [`docs/generated/README.md`](../generated/README.md) | Generated output | Producer-owned output | Must be regenerated through its owning workflow |
| [`docs/handoff/2026-05-22-python-rewrite-harness.md`](../handoff/2026-05-22-python-rewrite-harness.md) | Handoff | Specialised schema | Session-continuity record outside durable knowledge |
| [`docs/knowledge/documentation-inventory.md`](documentation-inventory.md) | OKF knowledge concept | OKF | Repository Documentation Inventory |
| [`docs/knowledge/documentation-map.md`](documentation-map.md) | OKF knowledge concept | OKF | Repository Knowledge Map |
| [`docs/knowledge/index.md`](index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`docs/knowledge/repository-visualization.md`](repository-visualization.md) | OKF knowledge concept | OKF | Visualization |
| [`docs/visualizations/repository-okf.mermaid.md`](../visualizations/repository-okf.mermaid.md) | Generated visualization | Specialised schema | Derived Mermaid report; source records remain authoritative |
| [`docs/PLANS.md`](../PLANS.md) | OKF knowledge concept | OKF | Delivery Plan |
| [`docs/product-specs/auth-model.md`](../product-specs/auth-model.md) | OKF knowledge concept | OKF | Product Contract |
| [`docs/product-specs/index.md`](../product-specs/index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`docs/product-specs/rewrite-compatibility-contract.md`](../product-specs/rewrite-compatibility-contract.md) | OKF knowledge concept | OKF | Product Contract |
| [`docs/product-specs/runtime-modes.md`](../product-specs/runtime-modes.md) | OKF knowledge concept | OKF | Product Contract |
| [`docs/product-specs/sandbox-validation.md`](../product-specs/sandbox-validation.md) | OKF knowledge concept | OKF | Product Contract |
| [`docs/product-specs/tool-surface.md`](../product-specs/tool-surface.md) | OKF knowledge concept | OKF | Product Contract |
| [`docs/refactor-and-repair-plan.md`](../refactor-and-repair-plan.md) | OKF knowledge concept | OKF | Delivery Plan |
| [`docs/references/index.md`](../references/index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`docs/RELIABILITY.md`](../RELIABILITY.md) | OKF knowledge concept | OKF | Reliability Contract |
| [`docs/runtime-validation-2026-05-16.md`](../runtime-validation-2026-05-16.md) | OKF knowledge concept | OKF | Validation Evidence |
| [`docs/runtime-validation-2026-05-22-harness.md`](../runtime-validation-2026-05-22-harness.md) | OKF knowledge concept | OKF | Validation Evidence |
| [`docs/runtime-validation-2026-05-23-native-bootstrap.md`](../runtime-validation-2026-05-23-native-bootstrap.md) | OKF knowledge concept | OKF | Validation Evidence |
| [`docs/SECURITY.md`](../SECURITY.md) | OKF knowledge concept | OKF | Security Boundary |
| [`docs/tool-reference.md`](../tool-reference.md) | OKF knowledge concept | OKF | Reference |
| [`GLOSSARY.md`](../../GLOSSARY.md) | OKF knowledge concept | OKF | Glossary Concept |
| [`README.md`](../../README.md) | OKF knowledge concept | OKF | Repository Guide |
| [`SECURITY.md`](../../SECURITY.md) | OKF knowledge concept | OKF | Security Boundary |
| [`tasks/adopt-rke-okf-knowledge/task.md`](../../tasks/adopt-rke-okf-knowledge/task.md) | OKF execution concept | OKF | Task |
| [`tasks/index.md`](../../tasks/index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |

## Repository knowledge

- [Documentation map](documentation-map.md) — RKE-managed reading order and relationship hub.
