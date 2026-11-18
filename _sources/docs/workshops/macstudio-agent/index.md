(macstudio-workshop)=
# 00 - Build a Mac Studio Coding Agent for VS Code

Build an inspectable coding assistant from a blank extension folder. Your Windows computer runs VS Code and project tools; a Mac Studio runs the model. You will connect them over SSH, implement streaming and tool calling, review code changes, and package a working extension.

**Audience:** beginners with basic JavaScript or Python experience. **Language:** English, with Chinese annotations for key terminology. **Workshop edition:** November 17, 2026. **Reference implementation:** Mac Studio Assistant 0.2.0.

## Workshop outcomes

By the end you can trace an **agent loop（智能体循环）**, implement **built-in tools（内置工具）**, build a **Webview（网页视图）**, and distinguish a proposed edit from an applied and tested change. You will also know what model switching, **MCP（模型上下文协议）**, and **skills（技能指令包）** do—and what this reference does not implement.

```{mermaid}
flowchart LR
    U["Windows: VS Code sidebar"] <--> E["Windows: extension and reviewed tools"]
    E <-->|"SSH"| B["Mac: temporary Python bridge"]
    B <-->|"loopback HTTP"| M["Mac: model API"]
    E <--> F["Windows project files"]
```

## Download the workshop materials

- {download}`Complete tutorial and reference source <assets/MacStudio-Beginner-Course.zip>` — includes the English reference project, lockfile, intentionally broken exercise, and original validation record. Extract it locally; do not run it inside a browser notebook.
- [Validation and reproducibility notes](validation.md) — what was tested, when, and what remains a learner check.

```{note}
The downloadable reference was tested on November 11, 2026. Publication on November 17 does not imply every model service or MCP integration was retested. Hostnames, model IDs, ports, and key paths are examples; use your own deployment. No private keys or real API credentials are included.
```

## Prerequisites and preflight

Bring a Windows computer with desktop VS Code, Node.js/npm, OpenSSH, and Python 3. You need access to a Mac with SSH, Python 3, and an already-running OpenAI-compatible model API. The workshop teaches the agent client, not model training or weight installation.

Complete the SSH and API checks in Lab 1 before a group session. If you cannot access a model, you can still complete the hello-world extension, offline file-tool tests, and UI reading. Mark live checkpoints as **not run**; do not substitute fabricated outputs.

This book page is the instruction surface. PowerShell commands run in a Windows terminal; Mac commands run on the Mac; extension code runs in the VS Code Development Host. Copyable code blocks are deliberately not executed during Jupyter Book builds.

## Agenda and pacing

The eight labs total approximately **6 hours 15 minutes**, excluding installation delays and breaks. Use two half-day sessions or four shorter meetings. For a 90-minute demonstration, preconfigure SSH/API access, show Labs 1–3, and demonstrate the completed reference with the Lab 6 toy project; that shorter path is not the full reconstruction.

| Lab | Topic | Suggested time |
|---|---|---|
| 1 | [Architecture and Connection](01-architecture-and-connection.md) | 45 min |
| 2 | [Your First VS Code Extension](02-first-extension.md) | 35 min |
| 3 | [SSH Bridge and Streaming Responses](03-ssh-and-streaming.md) | 50 min |
| 4 | [Project Tools and the Agent Loop](04-project-tools.md) | 45 min |
| 5 | [Controller and Sidebar Interface](05-controller-and-interface.md) | 60 min |
| 6 | [Capstone: Fix, Review, and Verify](06-capstone-and-tests.md) | 60 min |
| 7 | [Packaging and Model Selection](07-package-and-models.md) | 35 min |
| 8 | [MCP, Skills, and Next Steps](08-mcp-skills-and-next-steps.md) | 45 min |

## How to work through each lab

1. Read the learning objectives and execution location.
2. Create or replace only the named file. A complete file block should not be appended to an old implementation.
3. Run the checkpoint and record actual output without credentials.
4. Compare with the downloaded `reference/` folder when stuck.
5. Complete the acceptance evidence and answer the knowledge quiz before continuing.

Some modules are assembled before the complete UI can run. Labs 2–4 explicitly identify those intermediate states. Keep the extension source folder separate from the disposable project that the assistant edits.

## Capstone and assessment

Your capstone is a broken addition function with a failing test. The assistant must read it, propose a minimal change, leave the file untouched until review, and run the test only after command approval.

| Evidence | Acceptance condition |
|---|---|
| Connection record | Noninteractive SSH and authenticated API discovery succeed |
| Agent trace | A model tool call receives the matching result and continues |
| Reviewed diff | Change is proposed before it is applied |
| Verification | Actual test output changes from failure to success |
| Failure drills | Stale edit is rejected; cancelled command is not executed |
| Capability statement | Clearly separates implemented tools from optional MCP/skill designs |

## Instructor notes

Prepare a known-working reference on a separate demo folder. Test the serving model's tool template before class, reserve time for SSH-agent issues, and avoid having a whole class saturate one model server simultaneously. Pair participants for diff review and ask each to explain which computer executes a command.

Do not distribute a private SSH key or shared production credentials. Use individual authorized access and disposable exercise files. Remote server tools have their own policy; the Windows command confirmation does not automatically govern them.

## Scope and follow-up

Implemented: streaming text, local list/read/search tools, edit proposals, native diffs, explicit apply, and approved commands. Optional design exercises: automatic primary-model discovery, a general MCP client, and automatic skill loading. Image input, persistent conversations, and a hardened process sandbox are not delivered features.

> **Image Suggestion (Nanobanana Prompt)**: Create a welcoming workshop cover with a Windows laptop showing a restrained editor sidebar and a Mac Studio on a neutral desk. Label the devices “Project tools” and “Model inference”; add the title “Build a Mac Studio Coding Agent”. Use clean typography, soft daylight, a navy and teal palette, and a small “Concept illustration” caption. Do not show passwords or imply a real screenshot.

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Does this workshop run the model on Windows?**

<details>
<summary>Answer</summary>

No. Windows runs the extension and client project tools; the example model runs on the Mac.

</details>

**2. What is the capstone evidence?**

<details>
<summary>Answer</summary>

A reviewed and applied minimal fix plus actual passing test output and failure-drill results.

</details>

**3. Does downloading the reference grant MCP access?**

<details>
<summary>Answer</summary>

No. Capabilities must be configured and verified in the host that executes them.

</details>
