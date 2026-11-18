# 09 - Validation and Reproducibility

Edition: November 18, 2026. Reference: Local Coding Assistant 0.3.0.

This edition adds local Python transport, Windows/Linux/macOS instructions, SSH tunnel routing, neutral settings/UI, portable test configuration and scripts. Earlier live Windows-to-Mac evidence belongs to version 0.2.0; it is not a live pass for this changed release.

| Check | Result / scope |
|---|---|
| Core and transport fixture tests | 6 passed on Windows: file restrictions, edit anchors, fragmented SSE, invalid/cancelled requests, actual local Python subprocess with UTF-8 tool continuation, SSH command construction |
| Python bridge regression | 1 passed on Windows using a local HTTP fixture, including rejected non-loopback URLs |
| Source and copyable blocks | JavaScript/Python/JSON checked during publication; shell examples reviewed and PowerShell parsed |
| Packaging | VSIX packaging checked during publication; no Marketplace publication |
| Linux/macOS runtime | Portable source and shell commands supplied; no fresh native end-to-end execution recorded for this edition |
| Live model, SSH tunnel and optional SSH bridge | Learner/instructor checkpoints; fixture tests are not live inference evidence |
| Current VS Code UI end-to-end | Learner checkpoint; the earlier release's UI results are historical |
| Generic MCP / automatic skills / vision | Not implemented; Lab 8 marks extension exercises explicitly |

## Development dependency audit

The lockfile was refreshed with nonbreaking audit fixes. The remaining npm audit findings concern packaging/development dependencies (8 reported: 2 moderate, 6 high), including glob/pattern parsing. They are not shipped in the VSIX; this is not a claim that the development toolchain has no known advisories. Review current upstream fixes before using packaging tools on untrusted repositories. No forced major-version upgrade was applied in this teaching release.

## Reproduce

Extract the ZIP. In `reference/`, use `npm.cmd ci` on Windows or `npm ci` on Linux/macOS. Run `scripts/check.cmd` in Windows CMD, `powershell -File scripts/check.ps1` in PowerShell when local policy permits, or `sh scripts/check.sh` on Linux/macOS. The individual npm commands in Lab 6 are equivalent and do not require running a PowerShell script file.

Set `AGENT_PYTHON` if your local executable has a custom path. Complete Lab 1 for route A, B or C; configure endpoint/model overrides in Lab 3; use the password launcher for smoke, live tool continuation and the separate VS Code host test. Record OS, route, versions, exact test outcomes and limitations without personal identifiers or credentials.

The bundled toy project intentionally fails until the learner reviews and applies the addition fix. A book build is only a documentation check. A fixture service checks protocol plumbing, not whether a real model chooses useful tools. Do not report skipped checks as passed.

[Return to the workshop](index.md).
