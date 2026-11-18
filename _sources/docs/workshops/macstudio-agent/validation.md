# 09 - Validation and Reproducibility

Date: November 11, 2026 (America/New_York).

This record applies to the English reference accompanying the original downloadable `COURSE.md`, derived from the existing Mac Studio Assistant 0.2.0 implementation. The installed extension was not replaced while preparing the course.

| Check | Result | Evidence / scope |
|---|---|---|
| JavaScript, Python, and JSON snippets | Passed | JavaScript syntax checks, Python AST parsing, JSON parsing |
| PowerShell snippets | Passed syntax parsing | Commands that change SSH setup or install software were not executed as a beginner would |
| Core unit tests | 4 passed | Fragmented SSE, workspace traversal/link restrictions, edit anchors, invalid/cancelled SSH requests |
| Python bridge regression | 1 passed | Fixture loopback server; direct mode without OpenClaw config; tested nonlocal URLs rejected |
| Live smoke request | Passed | Real SSH bridge, model discovery, streamed reply |
| Live tool protocol | Passed | Model tool call plus tool-result continuation returning the fixture marker |
| VS Code extension-host integration | Passed | Activation, Webview ready, diff opening, file application, stale-edit rejection, file creation, traversal rejection, live model-driven read/propose/apply |
| Packaging | Passed | VSCE produced an installable VSIX from the reference |
| Beginner toy project | Intentionally broken | The course's initial subtraction implementation is expected to fail its addition test |

## Environment and practical qualifications

- Windows x64, Node 22.16.0, OpenSSH, and Python were used. The Mac was reached using the existing `macstudio` alias and authorized `id_ed25519` key.
- Live requests selected `YOUR_MODEL_ID`. Model discovery also listed another ID at validation time; the reference continued to request its explicitly configured ID. This does not establish what weights the server may route behind a model alias.
- The regular VS Code installation was updating and could not launch the initial test. The host test was rerun successfully with an existing separate VS Code 1.139.1 test build.
- That archived test build logged an unrelated missing TextMate worker resource. The extension-host assertions, Webview readiness, and model edit flow still passed. This is not a claim of flawless editor installation or visual pixel-level review.
- Packaging and host tests reused the existing development dependencies. A fresh-machine npm installation was not performed; the reference includes the resolved package lockfile for reproduction.
- Tests needing subprocess/network or temporary directory-link access were run with permissions to perform those operations. Restricted execution environments may reject those operations before the application logic is reached.
- The live host test automatically invokes the reviewed-edit application method on a disposable fixture. Manual command approval, keyboard accessibility, and visual review remain learner checkpoints, not fully automated coverage.
- The command timeout, child-process cleanup limitations, UTF-8 assumptions, coarse context guard, and filesystem race limits are documented in the course.
- Generic MCP client integration, automatic server-default model selection, image input, and automatic skill discovery are design exercises, not tested or installed capabilities.

## Reproduce

In the reference directory, install dependencies with `npm ci`. Run `npm test` and `npm run test:bridge`. For live checks, supply your own `MACSTUDIO_API_KEY` in the terminal environment and run `node test/smoke.js`, `npm run test:live`, and `npm run test:host` as described in the course. Change the explicit host/key/model values in test options if your deployment differs.

Never infer success from a model's answer alone. Preserve actual test outputs, examine changed files, and distinguish a proposed change from an applied and verified change.


The Jupyter Book adaptation preserves the tested code and separates the 16 source lessons into eight workshop labs. Build-time rendering is a documentation check, not a repeat of the live Mac integration tests.

[Return to the workshop](index.md).

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Were optional MCP-client designs tested as installed features?**

<details>
<summary>Answer</summary>

No. They remain design exercises.

</details>

**2. Does a successful book build prove the API is currently available?**

<details>
<summary>Answer</summary>

No. A documentation build and a live service test are different checks.

</details>
