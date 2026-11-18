(macstudio-lab-01)=
# 01 - Architecture and Connection

**Format:** hands-on lab · **Suggested time:** 45 minutes · **Original course lessons:** 1–2.

```{admonition} Learning objectives
:class: tip
Locate every execution boundary; verify noninteractive SSH and the authenticated model endpoint.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 1. Understand the architecture before writing code

An **extension host（扩展宿主）** is the process in which VS Code runs extension code. In this course it runs on Windows. A **Webview（网页视图）** renders our sidebar. It sends small messages to the extension host; it does not run SSH or touch project files directly.

The **inference server（推理服务）** lives on the Mac. It generates text and structured tool-call requests. It does not gain access to your Windows filesystem merely because a model produced a filename.

```{mermaid}
flowchart LR
    U[You] --> W[Windows sidebar Webview]
    W <-->|postMessage| E[Windows extension host]
    E <-->|encrypted SSH stdin/stdout| P[Temporary Python process on Mac]
    P <-->|loopback HTTP| M[Mac model API]
    E <-->|read / reviewed edit| F[Windows project files]
    E -->|approved command| T[Windows PowerShell]
```

The arrows show request and response boundaries. File operations and approved commands belong to the Windows extension host.

Our design uses SSH as a request/response bridge. It does **not** run `ssh -L`, create a Windows HTTP listener, or upload the whole project. Each model request starts a temporary Python process on the Mac, sends JSON through standard input, and returns the response through standard output.

There are two meanings of `127.0.0.1`: in a Windows browser it means Windows; inside the remote Python process it means the Mac. Our Base URL is evaluated by the latter.

A **tool call（工具调用）** is a request for the application to invoke a named function with JSON arguments. The application must decide whether to execute it. A minimal **agent loop（智能体循环）** is:

1. Send conversation messages and available tool descriptions to the model.
2. Receive text, tool calls, or both.
3. Validate and execute permitted tool calls.
4. Add each tool result to the conversation using the matching call ID.
5. Ask the model to continue. Stop when it returns a final answer or a limit is reached.

**Checkpoint:** If the model requests `local_read_file("src/main.py")`, the Windows extension reads the selected Windows project. The Mac does not interpret that as a path on its own disk.

## 2. Prepare the two computers

### 2.1 Prerequisites and environment checks

| Windows client | Mac Studio |
|---|---|
| Desktop VS Code | Running OpenAI-compatible Chat Completions API |
| Node.js and npm | Python 3 usable over SSH |
| OpenSSH client | SSH access for your account |
| Python 3 for local bridge tests | Model service accessible through Mac loopback |
| Network route to the Mac, such as your Tailscale connection | Same reachable network or tailnet |

The original implementation was exercised with Node 22.16.0; use a supported Node version compatible with the packaging tools. `engines.vscode` in the manifest declares an API floor, not proof that every older VS Code release has been tested. You do not need a Windows GPU or model weights on Windows.

**Run on Windows, in PowerShell:**

```powershell
node --version
npm.cmd --version
python --version
ssh -V
code --version
```

Use `npm.cmd` on Windows if execution policy prevents `npm.ps1` from running. If `code` is not on PATH, open VS Code normally and use its menus. Do not change a global execution policy just to follow this course.

### 2.2 Make SSH reliable before building a GUI

If you already have working key authentication, reuse it. Never overwrite an existing private key. If you need a new key, create a distinct one on Windows:

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\macstudio_course"
Get-Content "$env:USERPROFILE\.ssh\macstudio_course.pub"
```

Only the `.pub` file is copied to the Mac. Keep the private key on Windows. On the Mac, append the public-key line to the account's `~/.ssh/authorized_keys`; do not replace existing keys. For example, after logging in interactively on the Mac:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
nano ~/.ssh/authorized_keys
```

Paste the single public-key line on its own line and save. An encrypted private key needs to be unlocked in an SSH agent usable by the process that launches VS Code. Our extension will not show SSH password or passphrase prompts.

Edit the Windows SSH config at `$env:USERPROFILE\.ssh\config`. Replace the example hostname with the reachable name or address of your Mac. Merge this block into your existing file rather than replacing the file:

```text
Host macstudio
    HostName YOUR_MAC_HOSTNAME_OR_IP
    User your-ssh-user
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

For a newly created course key, use `~/.ssh/macstudio_course` instead, both here and in the extension setting. Our working machine used `id_ed25519`; its other `macstudio` key was not accepted. Matching the actual authorized key matters more than its filename.

Connect interactively once, verify the host fingerprint against your Mac through a trusted channel, and accept it only if it matches. Then test the exact noninteractive behavior used by the extension:

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" your-ssh-user@macstudio
# After checking the host and logging in, type exit to return to Windows.
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -i "$env:USERPROFILE\.ssh\id_ed25519" macstudio "whoami; /usr/bin/python3 --version"
```

**Checkpoint:** The second command prints the account and Python version without asking for a password. A successful interactive password login alone is insufficient. If Python has a different path, record that path for `macstudio.remotePython`.

### 2.3 Check the API on the Mac

The running service in our example advertises:

```text
Base URL: http://127.0.0.1:11436/v1
Model ID: qwen3.8-flash-next-q6
```

These are deployment-specific values. The model name does not independently prove its context size, vision support, or tool reliability. We will test the protocol behaviors we use. This course does not require a cloud API key.

Create `probe_api.py` on the Mac with the following complete diagnostic script. It prompts for your configured service key without storing it in source code:

```python
import getpass
import json
import urllib.request

base = "http://127.0.0.1:11436/v1"
model = "qwen3.8-flash-next-q6"
key = getpass.getpass("Local API key: ")

def request(route, body=None):
    req = urllib.request.Request(
        base + route,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)

print(json.dumps(request("/models"), indent=2))
reply = request("/chat/completions", {
    "model": model,
    "messages": [{"role": "user", "content": "Reply only OK."}],
    "max_tokens": 128,
    "stream": False,
})
print(reply["choices"][0]["message"]["content"])
```

**Run on Mac:** `python3 probe_api.py`. Use the key configured for your service; the tutorial deliberately does not embed your real key. Expect your model in `/models` and a short reply. An HTTP 401 is an authentication problem; a refused connection usually means the address, port, or service state is wrong.

**Checkpoint:** Do not proceed until SSH and the API work independently. A sidebar cannot repair an unavailable service.

```{admonition} Lab acceptance evidence
:class: important
Record a successful SSH account/Python check and an API probe. Do not paste credentials into your notes.
```

> **Image Suggestion (Nanobanana Prompt)**: Create a clean educational illustration for “Architecture and Connection”, using a neutral VS Code-inspired desktop palette, legible monospace labels, a Windows workstation and a Mac Studio where relevant, and clearly marked “Illustration” text. Emphasize the lab's actual control or execution boundary. Include no real credentials, personal paths, or fabricated test results. Use even lighting and a flat technical-documentation style rather than decorative effects.

**Continue:** [Previous](index.md) · [Next](02-first-extension.md) · [Workshop guide](index.md)

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Where does local_read_file execute?**

<details>
<summary>Answer</summary>

In the Windows extension host, against the selected client workspace.

</details>

**2. Why is a successful password-based SSH login insufficient?**

<details>
<summary>Answer</summary>

The extension uses BatchMode and cannot answer interactive password prompts.

</details>

**3. Which computer does the Base URL loopback address refer to?**

<details>
<summary>Answer</summary>

The Mac, because the remote Python process sends the HTTP request.

</details>
