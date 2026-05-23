# Security

## Security goals

- minimize secret exposure
- minimize accidental write capability
- make auth mode explicit
- reduce hidden runtime dependencies

## Current security positives

- Python wrapper can require bearer auth
- write-capable tools are intentionally gateable
- browser-session auth can be validated without persisting secrets in repo files

## Current security concerns

- historical runtime evidence can still be mistaken for supported product behavior
- browser-session credentials are powerful and easy to leak in local validation

## Security baseline

- local Python-only implementation
- exactly one supported Slack auth mode: `xoxc` plus `xoxd`
- clear secret handling guidance
- explicit tool exposure model
- docs that separate verified support from inherited or legacy behavior
