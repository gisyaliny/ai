(macstudio-lab-02)=
# 02 - Your First VS Code Extension

**Format:** hands-on lab · **Suggested time:** 35 minutes · **Original course lessons:** 3–4.

```{admonition} Learning objectives
:class: tip
Create a manifest, register a command, and launch an isolated Extension Development Host.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 3. Build your first extension

### 3.1 Create a clean source folder

**Run on Windows:**

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\macstudio-assistant-course"
Set-Location "$env:USERPROFILE\Documents\macstudio-assistant-course"
New-Item -ItemType Directory -Path src,media,test,.vscode
code .
```

If that folder already exists, choose a different empty name. This is the extension source folder, not the project the agent will later edit.

**Create `package.json`:**

```json
{
  "name": "macstudio-assistant",
  "displayName": "Mac Studio Assistant",
  "version": "0.2.0",
  "publisher": "workshop-example",
  "engines": { "vscode": "^1.96.0" },
  "main": "./src/extension.js",
  "activationEvents": ["onCommand:macstudio.open"],
  "contributes": {
    "commands": [{"command": "macstudio.open", "title": "Mac Studio: Open chat"}]
  }
}
```

**Create `src/extension.js`:**

```javascript
const vscode = require('vscode');

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('macstudio.open', () => {
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
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Mac Studio extension",
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

Press **F5** in the source window. A second window, the **Extension Development Host**, opens. In that second window, press `Ctrl+Shift+P`, run **Mac Studio: Open chat**, and look for the notification. The launch configuration disables other installed extensions for this development session to avoid conflicts with the installed edition.

This is the standard extension debugging workflow; see Microsoft's [first extension guide](https://code.visualstudio.com/api/get-started/your-first-extension).

**Checkpoint:** You can change the message, stop and restart debugging, and see the new message. You now know which window contains source code and which window runs the extension.

## 4. Define the finished extension contract

The manifest is the contract between your extension and VS Code. It declares commands, settings, the activity-bar container, and the view ID. The identifiers must agree with the JavaScript you will write later.

**Replace `package.json` with the complete manifest below.** The example publisher is for local development; it is not permission to publish to a marketplace account.

```json
{
  "name": "macstudio-assistant",
  "displayName": "Mac Studio Assistant",
  "description": "A coding assistant powered by a remote Mac, with reviewed client-side edits.",
  "version": "0.2.0",
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
    "onView:macstudio.chat"
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
          "id": "macstudio",
          "title": "Mac Studio",
          "icon": "media/icon.svg"
        }
      ]
    },
    "views": {
      "macstudio": [
        {
          "id": "macstudio.chat",
          "name": "Assistant",
          "type": "webview"
        }
      ]
    },
    "commands": [
      {
        "command": "macstudio.open",
        "title": "Mac Studio: Open chat"
      },
      {
        "command": "macstudio.connect",
        "title": "Mac Studio: Check connection"
      },
      {
        "command": "macstudio.settings",
        "title": "Mac Studio: Connection settings"
      },
      {
        "command": "macstudio.attach",
        "title": "Mac Studio: Attach selection or file"
      },
      {
        "command": "macstudio.newChat",
        "title": "Mac Studio: New chat"
      },
      {
        "command": "macstudio.setApiKey",
        "title": "Mac Studio: Set API key"
      }
    ],
    "menus": {
      "editor/context": [
        {
          "command": "macstudio.attach",
          "group": "navigation@90"
        }
      ]
    },
    "configuration": {
      "title": "Mac Studio Assistant",
      "properties": {
        "macstudio.sshHost": {
          "type": "string",
          "default": "macstudio",
          "scope": "machine",
          "description": "SSH config alias or user@host. Host fingerprint must already be trusted."
        },
        "macstudio.sshIdentityFile": {
          "type": "string",
          "default": "~/.ssh/macstudio_course",
          "scope": "machine",
          "description": "Local private key path. Leave empty to use SSH config or agent."
        },
        "macstudio.sshExecutable": {
          "type": "string",
          "default": "ssh",
          "scope": "machine",
          "description": "Local OpenSSH executable."
        },
        "macstudio.remotePython": {
          "type": "string",
          "default": "/usr/bin/python3",
          "scope": "machine",
          "description": "Python 3 executable on the Mac."
        },
        "macstudio.remoteConfig": {
          "type": "string",
          "default": "~/.openclaw/openclaw.json",
          "scope": "machine",
          "description": "Remote OpenClaw JSON configuration; only used by legacy modes."
        },
        "macstudio.mode": {
          "type": "string",
          "enum": [
            "direct",
            "openclaw",
            "qwen"
          ],
          "default": "direct",
          "description": "Direct uses the configured API. Other modes use the remote OpenClaw configuration."
        },
        "macstudio.maxOutputTokens": {
          "type": "integer",
          "default": 4096,
          "minimum": 256,
          "maximum": 16384
        },
        "macstudio.timeoutSeconds": {
          "type": "integer",
          "default": 600,
          "minimum": 30,
          "maximum": 3600
        },
        "macstudio.maxToolRounds": {
          "type": "integer",
          "default": 12,
          "minimum": 1,
          "maximum": 30
        },
        "macstudio.baseUrl": {
          "type": "string",
          "default": "http://127.0.0.1:11436/v1",
          "scope": "machine",
          "description": "Model API loopback URL on the Mac, reached through SSH."
        },
        "macstudio.modelId": {
          "type": "string",
          "default": "YOUR_MODEL_ID",
          "scope": "machine",
          "description": "Explicit model ID for direct mode."
        }
      }
    }
  },
  "scripts": {
    "test": "node --test test/core.test.js",
    "test:live": "node test/live.js",
    "test:host": "node test/run-host.js",
    "package": "vsce package --allow-missing-repository",
    "test:bridge": "python test/bridge_test.py"
  },
  "devDependencies": {
    "@vscode/vsce": "3.9.2",
    "@vscode/test-electron": "2.5.2"
  }
}
```

The `main` entry points to executable JavaScript. `extensionKind: ["workspace"]` means the extension belongs with the workspace; in this course the workspace is local Windows. If you instead open a Remote-SSH workspace, the execution location can change. This course's “Windows commands” assumptions no longer apply unchanged.

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

**Run on Windows, in the source folder:**

```powershell
npm.cmd install
```

Keep the resulting `package-lock.json`. If using the included completed reference, run `npm.cmd ci` instead: it already has a lockfile. Runtime code uses built-in Node/Python APIs and VS Code APIs; the npm dependencies are for packaging and integration tests.

**Checkpoint:** Installation succeeds and the manifest parses. The final sidebar is not ready yet. Continue through Lesson 10 before testing the complete UI. Your old hello-world controller will be replaced in Lesson 9.

```{admonition} Lab acceptance evidence
:class: important
Show the hello-world notification from your own F5 session and identify the source window versus the test window.
```

> **Image Suggestion (Nanobanana Prompt)**: Create a clean educational illustration for “Your First VS Code Extension”, using a neutral VS Code-inspired desktop palette, legible monospace labels, a Windows workstation and a Mac Studio where relevant, and clearly marked “Illustration” text. Emphasize the lab's actual control or execution boundary. Include no real credentials, personal paths, or fabricated test results. Use even lighting and a flat technical-documentation style rather than decorative effects.

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
