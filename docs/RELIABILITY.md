# Reliability

## Current reliability posture

The service is operationally real and now has a single supported runtime path: the Python-native FastMCP server.

## Current validated positives

- wrapper startup works
- health endpoint works
- real Slack-backed tool execution works
- resource listing works
- full validated tool surface works in sandbox validation

## Current reliability risks

- Slack-side behavioural drift could still affect fixture-sensitive tools
- some success paths depend on mutable sandbox state
- historical docs can still be mistaken for active implementation guidance

## Reliability baseline

- local-only backend
- deterministic startup path
- explicit auth mode
- repeatable integration fixtures
- contract tests for every supported tool and resource
