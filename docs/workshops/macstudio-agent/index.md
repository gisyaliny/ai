(localagent-workshop)=
# 00 - Build Your Own Coding Agent: Windows, Linux and macOS

Build an inspectable coding assistant from a blank VS Code extension folder. Use **Windows, Linux, or macOS** for your project and a local or remote OpenAI-compatible model. You will implement streaming, tool calling, reviewed edits, command approval, and a sidebar interface.

**Audience:** beginners with basic JavaScript or Python experience. **Language:** English, with Chinese annotations for key terminology. **Edition:** November 18, 2026. **Reference:** Local Coding Assistant 0.3.0.

The URL retains the original `macstudio-agent` slug so existing shared links keep working; the course and code are now platform-neutral. Mac Studio is an optional model host, not a prerequisite. This edition uses a new extension ID and `localagent.*` settings; re-enter settings and the API key if coming from the older extension.

## Workshop outcomes

By the end you can trace an **agent loop（智能体循环）**, implement **built-in tools（内置工具）**, build a **Webview（网页视图）**, and distinguish a proposed edit from an applied and tested change. You will also know what model switching, **MCP（模型上下文协议）**, and **skills（技能指令包）** do—and what this reference does not implement.

```{mermaid}
flowchart LR
    U["VS Code on Windows / Linux / macOS"] <--> E["Extension and reviewed project tools"]
    E <--> B["Python bridge: local or optional remote"]
    B <--> M["Same-machine API or remote API through SSH"]
    E <--> F["Selected project files"]
```

## Download the workshop materials

- {download}`Complete tutorial and reference source <assets/Coding-Agent-Workshop.zip>` — includes the English reference project, lockfile, intentionally broken exercise, and current validation record. Extract it locally; do not run it inside a browser notebook.
- [Validation and reproducibility notes](validation.md) — what was tested, when, and what remains a learner check.

```{note}
The current validation record separates Windows fixture tests from live-model and other-OS checks. Cross-platform code and commands do not imply that every OS/model combination has been tested. Never submit real keys, account names, or private host addresses as workshop evidence.
```

## Prerequisites and preflight

Bring desktop VS Code, Node.js/npm, and Python 3. [Lab 1](01-architecture-and-connection.md) supplies separate Windows PowerShell, Linux Bash and macOS Terminal commands, plus a portable probe. Choose **A: same computer**, **B: SSH tunnel to any supported server OS**, or **C: optional Linux/macOS remote bridge**. If you lack a model, complete the offline tests and UI construction and mark live exercises as not run.

The book contains copyable examples; it does not execute shell commands during a build. Run commands only in the labelled terminal. Downloaded scripts include `scripts/check.ps1`, `scripts/check.cmd` and `scripts/check.sh`. The shared Python and JavaScript source is identical across platforms.

## Agenda and pacing

The eight labs total approximately **6 hours 15 minutes**, excluding installation delays and breaks. Use two half-day sessions or four shorter meetings. For a 90-minute demonstration, preconfigure SSH/API access, show Labs 1–3, and demonstrate the completed reference with the Lab 6 toy project; that shorter path is not the full reconstruction.

| Lab | Topic | Suggested time |
|---|---|---|
| 1 | [Architecture and Connection](01-architecture-and-connection.md) | 45 min |
| 2 | [Your First VS Code Extension](02-first-extension.md) | 35 min |
| 3 | [Local/SSH Transport and Streaming](03-ssh-and-streaming.md) | 50 min |
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
| Connection record | The selected route reaches the API and discovers the configured model |
| Agent trace | A model tool call receives the matching result and continues |
| Reviewed diff | Change is proposed before it is applied |
| Verification | Actual test output changes from failure to success |
| Failure drills | Stale edit is rejected; cancelled command is not executed |
| Capability statement | Clearly separates implemented tools from optional MCP/skill designs |

## Instructor notes

Prepare a known-working reference on a separate demo folder. Test the serving model's tool template before class, reserve time for SSH-agent issues, and avoid having a whole class saturate one model server simultaneously. Pair participants for diff review and ask each to explain which computer executes a command.

Do not distribute a private SSH key or shared production credentials. Use individual authorized access and disposable exercise files. Remote server tools have their own policy; the client command confirmation does not automatically govern them.

## Scope and follow-up

Implemented: streaming text, local list/read/search tools, edit proposals, native diffs, explicit apply, and approved commands. Optional design exercises: automatic primary-model discovery, a general MCP client, and automatic skill loading. Image input, persistent conversations, and a hardened process sandbox are not delivered features.


## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Must the model run on a Mac?**

<details>
<summary>Answer</summary>

No. The model can run on Windows, Linux or macOS, on the client or a separate server.

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
