# 13 - Validation and Reproducibility

## Advanced Studio 0.13 record — November 24, 2026

The advanced kit contains source commit `0007645fdd8cb5f5d73d4270fce51ca7d5b87dbe` with documentation/installer follow-up. The original VSIX hash is recorded in Lab 9 and the kit. It is a development preview, not final 1.0.

| Check | Recorded evidence |
|---|---|
| Node suite | 82 passed |
| Python bridge suites | Model bridge: 2; ComfyUI bridge: 1, passed |
| Cross-platform CI | Windows, Linux and macOS passed; seven native VS Code host runs per platform |
| Live model | One M4 read-only bug-review exercise passed through SSH; no commands or file changes |
| Native screenshots | Real Studio 0.13 in desktop VS Code 1.147.0, isolated demonstration profile, public arithmetic fixture; live model finding and staged diagnostics |
| UI regression | Generated webview checked at 280/380/900 px English and 280/380 px Chinese, light/dark; separate from native screenshot capture |
| Privacy | VSIX textual entries scanned; personal settings, credentials, session files and test profiles excluded |
| Workshop publication | Zero-warning Jupyter Book build; four new lab pages and their local links/images checked in a browser; desktop and 390 px mobile rendering inspected |
| Not complete | Full 20-case real-task acceptance; all provider/plugin combinations; parallel writing agents |

Screenshots are captured from the actual extension's renderer, not the earlier HTML design board. They use only disposable project files and saved demonstration conversations. The capture used expanded child context/total budgets (32,768 / 131,072); defaults remain 16,384 / 64,000. The real-model report suggests a fix; it is not evidence of executed tests. This edition does not repeat every image-generation or OAuth-provider exercise.

The portable fixture was executed on Windows: its baseline failed, the minimal source fix passed without changing tests, and recreating an existing folder was refused. The bundled MCP server completed an actual initialize/discover/read call returning `WORKSHOP-MCP-READ-OK`. These checks are separate from the 82 extension tests. Run the commands in Labs 9–12 and record your own live outcomes. A successful book build is not evidence that a model completed every exercise.

## Beginner reference record — November 18, 2026

Reference: Local Coding Assistant 0.3.0. The following evidence belongs to that frozen reference, not the newer Studio implementation.

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
