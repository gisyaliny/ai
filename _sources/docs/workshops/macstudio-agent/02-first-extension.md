(localagent-lab-02)=
# 02 - Your First VS Code Extension

**Format:** hands-on lab · **Suggested time:** 35 minutes · **Original course lessons:** 3–4.

```{admonition} Learning objectives
:class: tip
Create a manifest, register a command, and launch an isolated Extension Development Host.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 3. Build your first extension

### 3.1 Create a clean source folder

**Run on your client:**

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\localagent-assistant-course"
Set-Location "$env:USERPROFILE\Documents\localagent-assistant-course"
New-Item -ItemType Directory -Path src,media,test,.vscode
code .
```

**Linux Bash / macOS zsh:**

```bash
mkdir -p "$HOME/Documents"
mkdir "$HOME/Documents/localagent-assistant-course"
cd "$HOME/Documents/localagent-assistant-course"
mkdir src media test .vscode
code .
```

If that folder already exists, choose a different empty name. On Windows CMD you can use `mkdir`, `cd /d`, and `npm.cmd`; PowerShell variables such as `$env:USERPROFILE` do not work in CMD. This is the extension source folder, not the project the agent will later edit.

**Create `package.json`:**

```json
{
  "name": "localagent-assistant",
  "displayName": "Local Coding Assistant",
  "version": "0.3.0",
  "publisher": "workshop-example",
  "engines": { "vscode": "^1.96.0" },
  "main": "./src/extension.js",
  "activationEvents": ["onCommand:localagent.open"],
  "contributes": {
    "commands": [{"command": "localagent.open", "title": "Local Agent: Open chat"}]
  }
}
```

**Create `src/extension.js`:**

```javascript
const vscode = require('vscode');

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('localagent.open', () => {
      vscode.window.showInformationMessage('Your extension is running.');
    })
  );
}

module.exports = { activate };
```

`require('vscode')` works inside the extension host because VS Code supplies the module. Running `node src/extension.js` in an ordinary terminal is not a valid activation test. No npm installation is necessary for this first checkpoint.

**Create `.vscode/launch.json`:**

```json
{
  "version": "0.3.0",
  "configurations": [
    {
      "name": "Run Local Agent extension",
      "type": "extensionHost",
      "request": "launch",
      "args": [
        "--disable-extensions",
        "--extensionDevelopmentPath=${workspaceFolder}"
      ]
    }
  ]
}
```

Press **F5** in the source window. A second window, the **Extension Development Host**, opens. In that second window, press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS), run **Local Agent: Open chat**, and look for the notification. The launch configuration disables other installed extensions for this development session to avoid conflicts with the installed edition.

This is the standard extension debugging workflow; see Microsoft's [first extension guide](https://code.visualstudio.com/api/get-started/your-first-extension).

**Checkpoint:** You can change the message, stop and restart debugging, and see the new message. You now know which window contains source code and which window runs the extension.

## 4. Define the finished extension contract

The manifest is the contract between your extension and VS Code. It declares commands, settings, the activity-bar container, and the view ID. The identifiers must agree with the JavaScript you will write later.

**Replace `package.json` with the complete manifest below.** The example publisher is for local development; it is not permission to publish to a marketplace account.

```json
{
  "name": "localagent-assistant",
  "displayName": "Local Coding Assistant",
  "description": "A coding assistant for Windows, Linux and macOS, with reviewed project edits.",
  "version": "0.3.0",
  "publisher": "workshop-example",
  "license": "MIT",
  "engines": {
    "vscode": "^1.96.0"
  },
  "categories": [
    "AI",
    "Other"
  ],
  "main": "./src/extension.js",
  "extensionKind": [
    "workspace"
  ],
  "activationEvents": [
    "onView:localagent.chat"
  ],
  "capabilities": {
    "untrustedWorkspaces": {
      "supported": false
    },
    "virtualWorkspaces": false
  },
  "contributes": {
    "viewsContainers": {
      "activitybar": [
        {
          "id": "localagent",
          "title": "Local Agent",
          "icon": "media/icon.svg"
        }
      ]
    },
    "views": {
      "localagent": [
        {
          "id": "localagent.chat",
          "name": "Assistant",
          "type": "webview"
        }
      ]
    },
    "commands": [
      {
        "command": "localagent.open",
        "title": "Local Agent: Open chat"
      },
      {
        "command": "localagent.connect",
        "title": "Local Agent: Check connection"
      },
      {
        "command": "localagent.settings",
        "title": "Local Agent: Connection settings"
      },
      {
        "command": "localagent.attach",
        "title": "Local Agent: Attach selection or file"
      },
      {
        "command": "localagent.newChat",
        "title": "Local Agent: New chat"
      },
      {
        "command": "localagent.setApiKey",
        "title": "Local Agent: Set API key"
      }
    ],
    "menus": {
      "editor/context": [
        {
          "command": "localagent.attach",
          "group": "navigation@90"
        }
      ]
    },
    "configuration": {
      "title": "Local Coding Assistant",
      "properties": {
        "localagent.sshHost": {
          "type": "string",
          "default": "model-server",
          "scope": "machine",
          "description": "SSH config alias or user@host. Host fingerprint must already be trusted."
        },
        "localagent.sshIdentityFile": {
          "type": "string",
          "default": "",
          "scope": "machine",
          "description": "Local private key path. Leave empty to use SSH config or agent."
        },
        "localagent.sshExecutable": {
          "type": "string",
          "default": "ssh",
          "scope": "machine",
          "description": "Local OpenSSH executable."
        },
        "localagent.remotePython": {
          "type": "string",
          "default": "python3",
          "scope": "machine",
          "description": "Python 3 executable on a Linux/macOS SSH bridge host. Windows servers use a tunnel with local transport."
        },
        "localagent.remoteConfig": {
          "type": "string",
          "default": "~/.openclaw/openclaw.json",
          "scope": "machine",
          "description": "Remote OpenClaw JSON configuration; only used by legacy modes."
        },
        "localagent.mode": {
          "type": "string",
          "enum": [
            "direct",
            "openclaw",
            "qwen"
          ],
          "default": "direct",
          "description": "Direct uses the configured API. Other modes use the remote OpenClaw configuration."
        },
        "localagent.maxOutputTokens": {
          "type": "integer",
          "default": 4096,
          "minimum": 256,
          "maximum": 16384
        },
        "localagent.timeoutSeconds": {
          "type": "integer",
          "default": 600,
          "minimum": 30,
          "maximum": 3600
        },
        "localagent.maxToolRounds": {
          "type": "integer",
          "default": 12,
          "minimum": 1,
          "maximum": 30
        },
        "localagent.baseUrl": {
          "type": "string",
          "default": "http://127.0.0.1:11434/v1",
          "scope": "machine",
          "description": "Loopback model URL as seen by the Python bridge: local machine/tunnel in local transport, server in SSH transport."
        },
        "localagent.modelId": {
          "type": "string",
          "default": "YOUR_MODEL_ID",
          "scope": "machine",
          "description": "Explicit model ID for direct mode."
        },
        "localagent.transport": {
          "type": "string",
          "enum": [
            "local",
            "ssh"
          ],
          "default": "local",
          "scope": "machine",
          "description": "Local Python for a same-machine API or SSH tunnel; SSH bridge for a Linux/macOS server with a POSIX login shell."
        },
        "localagent.localPython": {
          "type": "string",
          "default": "",
          "scope": "machine",
          "description": "Python 3 executable on the extension host; empty selects python on Windows or python3 elsewhere. Use a path, not a command with arguments."
        }
      }
    }
  },
  "scripts": {
    "test": "node --test test/core.test.js test/transport.test.js",
    "test:live": "node test/live.js",
    "test:host": "node test/run-host.js",
    "package": "vsce package --allow-missing-repository",
    "test:bridge": "node test/run-bridge.js"
  },
  "devDependencies": {
    "@vscode/vsce": "3.9.2",
    "@vscode/test-electron": "2.5.2"
  }
}
```

The `main` entry points to executable JavaScript. `extensionKind: ["workspace"]` means the extension belongs with the workspace; in this course the workspace is local to your desktop OS. Remote-SSH or WSL changes the extension host location; use the commands, Python path and loopback address appropriate to that host.

`untrustedWorkspaces.supported: false` disables this extension in Restricted Mode. File and command methods also check trust at runtime. See [Workspace Trust for extension authors](https://code.visualstudio.com/api/extension-guides/workspace-trust).

Connection settings use `scope: "machine"` so they are machine-specific rather than taken from a project's settings. The API key is absent from the manifest because it belongs in SecretStorage.

**Create `media/icon.svg`:**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="13" rx="3"/><path d="M8 21h8M12 16v5M7 8l3 2-3 2m6 0h4"/></svg>
```

**Create `.gitignore`:**

```text
node_modules/
.vscode-test/
test-results/
*.vsix
__pycache__/
```

**Run in the extension source folder:**

**Windows PowerShell:**

```powershell
npm.cmd install
```

**Linux Bash / macOS zsh:**

```bash
npm install
```

Keep the resulting `package-lock.json`. If using the included completed reference, run `npm.cmd ci` (Windows) or `npm ci` (Linux/macOS) instead: it already has a lockfile. Runtime code uses built-in Node/Python APIs and VS Code APIs; the npm dependencies are for packaging and integration tests.

The `test` script refers to the transport regression added in Lab 6; until then run `node --test test/core.test.js` at the Lab 4 checkpoint.

**Checkpoint:** Installation succeeds and the manifest parses. The final sidebar is not ready yet. Continue through Lesson 10 before testing the complete UI. Your old hello-world controller will be replaced in Lesson 9.

```{admonition} Lab acceptance evidence
:class: important
Show the hello-world notification from your own F5 session and identify the source window versus the test window.
```


**Continue:** [Previous](01-architecture-and-connection.md) · [Next](03-ssh-and-streaming.md) · [Workshop guide](index.md)

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Why not run extension.js with ordinary Node?**

<details>
<summary>Answer</summary>

VS Code supplies the vscode module inside its extension host.

</details>

**2. What is package.json responsible for?**

<details>
<summary>Answer</summary>

It declares entry points, commands, settings, views, compatibility, and packaging metadata.

</details>

**3. Why disable other extensions in the development session?**

<details>
<summary>Answer</summary>

To avoid ID conflicts with the installed reference and reduce interference during testing.

</details>
