(localagent-lab-07)=
# 07 - Packaging and Model Selection

**Format:** hands-on lab · **Suggested time:** 35 minutes · **Original course lessons:** 13–14.

```{admonition} Learning objectives
:class: tip
Build a VSIX, inspect its contents, and distinguish pinned models from delegated server selection.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 13. Package and install your extension

**Create `.vscodeignore`:**

```text
node_modules/**
test/**
.vscode-test/**
package-lock.json
*.vsix
test-results/**
**/*.log

.vscode/**
__pycache__/**
**/__pycache__/**
scripts/**
```

This keeps dependencies, fixtures, test profiles, logs, and previous packages out of the VSIX. Copy `LICENSE` from the reference if retaining this implementation's MIT license; if starting your own distribution, decide your license and publisher identity deliberately.

**Create `README.md` in the extension source folder:**

```markdown
# Local Coding Assistant 0.3.0

A beginner VS Code extension workshop for Windows, Linux and macOS.
Use a local OpenAI-compatible model endpoint, or forward a server endpoint
through SSH. The optional remote Python bridge requires a Linux/macOS server
with a POSIX login shell. Windows servers use SSH port forwarding instead.

Read the workshop at https://gisyaliny.github.io/ai/docs/workshops/macstudio-agent/index.html
and start at Lab 1 before running live tests (offline: ../COURSE.md).
Windows: npm.cmd ci; npm.cmd test; npm.cmd run test:bridge.
Linux/macOS: npm ci; npm test; npm run test:bridge.
Python: python on Windows, python3 elsewhere; override with AGENT_PYTHON.
Convenience checks: powershell -File scripts/check.ps1 or sh scripts/check.sh.

Press F5, open a disposable project, then Local Agent: Open chat.
Set localagent.transport=local and localagent.modelId to an installed model.
Use Local Agent: Set API key; a nonsecret placeholder is sufficient only
when your local server intentionally ignores authentication.
Run npm run package (npm.cmd on Windows) to create a VSIX.

Edits require review and explicit application. Commands require approval.
Tools run on the VS Code workspace extension host, with your permissions.
This is not an OS sandbox. MCP and automatic skill loading are design labs.
This new extension ID does not migrate older settings or SecretStorage.
```

**Run from the extension source folder:**

**Windows PowerShell:**

```powershell
npm.cmd run package
code --install-extension .\localagent-assistant-0.3.0.vsix --force
```

**Linux Bash / macOS zsh:**

```bash
npm run package
code --install-extension ./localagent-assistant-0.3.0.vsix --force
```

Alternatively use **Extensions → … → Install from VSIX…**. Reload VS Code, open a project folder, and run **Local Agent: Open chat**. Installation under the same extension ID updates/replaces that same extension ID. This platform-neutral edition has a new ID (`workshop-example.localagent-assistant`); it does not replace or import settings from the earlier Mac-specific extension.

The packaging utility is `vsce`; a VSIX can be installed locally without publishing to a marketplace. See Microsoft's [packaging and publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension).

A package should contain source/assets and the manifest, not private keys, API tokens, `node_modules`, or test profiles. Inspect the file listing printed during packaging. Keep the npm lockfile in your source repository even though it is excluded from the VSIX.

The installed extension uses SecretStorage configured through its password prompt. It does not read the terminal test environment variable. If a live test passed but the installed extension reports 401, use **Local Agent: Set API key** and check the active mode.

**Checkpoint:** Close the development host and verify the installed extension independently. A successful F5 session is not proof that your VSIX included every required asset.

## 14. Change the model without confusing the user

### 14.1 What the completed reference does today

| Mode | Model selection | What happens after a server-side change |
|---|---|---|
| `direct` | Explicit `localagent.modelId` and `localagent.baseUrl` | No discovery-based automatic switch; independent of the client OS |
| `qwen` | Reads `agents.defaults.model.primary` and its provider from remote JSON on each request | Can follow that configuration if the replacement is a compatible loopback model API |
| `openclaw` | Calls `openclaw/main` | Server owns agent model routing; loaded config and sessions matter |

If a service keeps a stable model alias while replacing the weights behind it, direct mode can use the changed backend without a settings change. That is server alias behavior, not model discovery in our extension. An ID in `/models` is not a universal declaration of the “primary” model.

Legacy `qwen` / `openclaw` modes read configuration on the **bridge host**: the client with local transport, or the Linux/macOS server with SSH transport. A tunnel alone does not make a remote configuration file local. Prefer SSH transport for remote server-owned configuration.

The `qwen` mode includes Qwen-oriented inference options and requires literal string credentials in the remote JSON. It is not a universal provider adapter. Its name should become clearer before exposing it to a broad audience.

### 14.2 Exercise: switch a pinned model

1. Start the replacement model on your chosen model host using its serving workflow.
2. Run model discovery and note the exact model ID. Do not guess it from a filename.
3. In VS Code settings, change `localagent.modelId`; change Base URL only if necessary.
4. Finish or stop the current task, then start a new chat.
5. Click Connect and repeat the live tool-continuation test against the replacement.

The live scripts have explicit endpoint/model values in their options. Update those values too when testing a replacement; changing UI settings does not change standalone Node scripts.

### 14.3 Optional design exercise: follow the server default

This is a future feature, **not integrated into the reference**. Design the policy before adding a dropdown. Two modes are enough: **Pinned model（固定模型）** and **Follow server default（跟随服务端默认模型）**.

In follow mode, use an explicit trusted source of truth, such as a gateway's supported default-model API or a managed server configuration. Do not choose the first `/models` item. Resolve the endpoint/model at task start, display it, and keep the selection stable for all tool rounds in that task.

Add tests for an absent default, multiple advertised models, a missing configured ID, a change between tasks, and a change during a task. On uncertainty, explain the problem and ask for a deliberate selection. Never silently send a continuation to an unrelated model.

**UI improvement:** Display `Model: …`, `Selection: Pinned / Server default`, and `Tools run on: the actual extension-host OS`. Report an actual resolved value rather than a label inferred from the requested configuration.

```{admonition} Lab acceptance evidence
:class: important
Produce a VSIX and document which settings and tests must change when you replace the model.
```


**Continue:** [Previous](06-capstone-and-tests.md) · [Next](08-mcp-skills-and-next-steps.md) · [Workshop guide](index.md)

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Does direct mode automatically follow the server default?**

<details>
<summary>Answer</summary>

No. It requests the configured ID. A server may independently change weights behind a stable alias.

</details>

**2. Why not choose the first models-list entry?**

<details>
<summary>Answer</summary>

List order does not establish a primary model or the user's intended selection.

</details>

**3. Should dependencies and test profiles ship in the VSIX?**

<details>
<summary>Answer</summary>

No. Exclude installed development dependencies, generated test profiles, logs, and credentials.

</details>
