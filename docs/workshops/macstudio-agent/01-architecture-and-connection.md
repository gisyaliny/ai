(localagent-lab-01)=
# 01 - Choose Your Platform and Connect a Model

**Format:** hands-on lab · **Suggested time:** 45–60 minutes, excluding model download.

Build the same agent on **Windows, Linux, or macOS**. No Mac Studio is required. The **client（客户端）** runs VS Code and project tools. The **model server（模型服务器）** may be the same computer or another computer on your network. A Mac Studio is one possible server, alongside a Linux GPU machine or a Windows workstation.

## 1. Choose one connection route

| Route | Client OS | Model server OS | Python bridge runs on | Extension setting |
|---|---|---|---|---|
| A — Same computer (begin here) | Windows / Linux / macOS | Same computer | Client | `localagent.transport: local` |
| B — SSH tunnel（SSH 隧道） | Windows / Linux / macOS | Windows / Linux / macOS with SSH server | Client | `local`, forwarded Base URL |
| C — Remote Python bridge (optional) | Windows / Linux / macOS | Linux / macOS with POSIX login shell | Server | `ssh` |

Routes A and B use identical extension code. Route B forwards only HTTP traffic; it does not execute Python through the server's shell. This avoids Windows/POSIX remote-shell quoting differences. Route C preserves the earlier SSH bridge as an advanced exercise; do not select C for a Windows SSH server.

```{mermaid}
flowchart LR
    U["VS Code sidebar"] <--> E["Extension host: Windows / Linux / macOS"]
    E <--> F["Project files and approved commands"]
    E <--> P["Local Python bridge"]
    P <-->|"A: loopback HTTP"| L["Same-machine model"]
    P <-->|"B: SSH tunnel"| R["Remote model: Windows / Linux / macOS"]
```

Tool calls are requests, not permissions. The extension reads files, proposes changes, and asks you to approve commands on the **workspace extension host（工作区扩展宿主）**. The model receives only the context the client sends. In a Remote-SSH or WSL VS Code window, the extension host may itself be remote: its paths, Python, loopback address and command shell follow that location. For your first run, use a normal desktop VS Code window and a local project folder.

## 2. Install and verify prerequisites

Install [desktop VS Code](https://code.visualstudio.com/download), a supported [Node.js LTS](https://nodejs.org/en/download) compatible with the bundled packaging tool, and [Python 3](https://www.python.org/downloads/). The initial reference used Node 22; record your actual version. Browser-only VS Code cannot run this extension's subprocesses.

- **Windows:** use the official installers. Make Python available as `python` in a newly opened terminal. If `python` opens the Microsoft Store, fix the app execution alias or set `localagent.localPython` to your real Python executable. Use PowerShell blocks below; `npm.cmd` avoids the `npm.ps1` execution-policy issue.
- **Linux:** install VS Code and Node from their official distribution instructions for your architecture. On Debian/Ubuntu, Python and the SSH client can be installed with `sudo apt update` followed by `sudo apt install python3 openssh-client`. Other distributions use their own package managers.
- **macOS:** install VS Code, Node and Python for your CPU architecture. In VS Code's Command Palette, run **Shell Command: Install 'code' command in PATH**, or open the folder through the GUI. Use `python3`; do not assume an unversioned `python` exists.

### Windows — PowerShell

```powershell
node --version
npm.cmd --version
python --version
code --version
# Only routes B/C need SSH:
ssh -V
```

### Linux — Bash

```bash
node --version
npm --version
python3 --version
code --version
ssh -V
```

### macOS — Terminal (zsh)

```bash
node --version
npm --version
python3 --version
code --version
ssh -V
```

The shell examples shared by Linux and macOS below use portable syntax supported by both Bash and zsh. Approved agent commands run in `/bin/sh` on these systems, so do not ask the agent to rely on Bash/zsh-specific syntax without explicitly invoking that shell.

## 3. Start a model endpoint

If you already have a working **OpenAI-compatible Chat Completions API**, keep it. Record its Base URL, exact model ID, and authentication requirements. A server offering plain text alone is not enough: the later labs require streaming, tool calls, and tool-result continuation.

For a new installation, [Ollama](https://docs.ollama.com/quickstart) is one example across all three systems. Install its official Windows/macOS application; for Linux follow the [official Linux instructions](https://docs.ollama.com/linux). To review the Linux installer before running it:

```bash
curl -fsSL https://ollama.com/install.sh -o ollama-install.sh
less ollama-install.sh
sh ollama-install.sh
```

Start the installed application/service. If no server is running, `ollama serve` starts one in the foreground; leave that terminal open. If the port is already in use, check the existing service instead of starting a second copy.

**Windows PowerShell / CMD, Linux Bash, macOS zsh — same commands:**

```text
ollama --version
ollama pull qwen3:4b
ollama list
ollama run qwen3:4b "Reply with a short greeting. /no_think"
```

`qwen3:4b` is a modest [example model with a tools tag](https://ollama.com/library/qwen3:4b), not a guarantee of reliable coding on your hardware. Choose a model that fits memory and passes Lab 6. Weight size is not total runtime memory; context and concurrent requests also consume memory. GPU support depends on runtime, OS and drivers; CPU inference can be slower. Do not buy hardware based on this exercise alone.

For local Ollama, use `http://127.0.0.1:11434/v1` and the ID reported by `ollama list` / `/v1/models`. Its local compatibility API ignores the supplied key; enter the nonsecret placeholder `ollama` when this workshop prompts. For an authenticated server, use that server's real credential privately. See [Ollama's compatibility documentation](https://docs.ollama.com/api/openai-compatibility). A llama.cpp or other compatible server can use another port; change the settings rather than assuming 11434.

## 4. Probe the API with one portable Python script

Create `probe_api.py` in a temporary course folder. This uses only Python's standard library and never writes the key to a file.

```python
import getpass
import json
import urllib.request

base = input("Base URL [http://127.0.0.1:11434/v1]: ").strip() or "http://127.0.0.1:11434/v1"
model = input("Exact installed model ID: ").strip()
key = getpass.getpass("API key (ollama for a default local Ollama server): ")

def request(route, body=None):
    req = urllib.request.Request(
        base.rstrip("/") + route,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)

models = request("/models")
print(json.dumps(models, indent=2))
if model not in [item["id"] for item in models.get("data", [])]:
    raise SystemExit("Use an exact ID from the model list.")
reply = request("/chat/completions", {
    "model": model, "messages": [{"role": "user", "content": "Reply only OK. /no_think"}],
    "max_tokens": 512, "stream": False,
})
print(reply["choices"][0]["message"]["content"])
```

**Windows:** `python probe_api.py`. **Linux/macOS:** `python3 probe_api.py`.
Use a trusted loopback endpoint: for A run on the model computer; for B run on the client after creating the tunnel below. For C first run on the server. An empty answer may mean a reasoning model exhausted its output budget; inspect the service's supported reasoning controls rather than declaring success.

## 5. Route B: reach another computer through SSH

Skip this section for A. The server must already run the model on its own loopback interface. Enable SSH only on the server:

| Server | Setup |
|---|---|
| Windows | Follow [Microsoft's OpenSSH Server setup](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse); start `sshd` and permit SSH in its firewall. |
| Linux (Debian/Ubuntu) | `sudo apt install openssh-server`, then `sudo systemctl enable --now ssh`; other distributions may call the service `sshd`. |
| macOS | System Settings → General → Sharing → Remote Login; allow your intended account. |

Use an account you are authorized to access. On the **client**, add this block to SSH config (Windows: `$env:USERPROFILE\.ssh\config`; Linux/macOS: `~/.ssh/config`). Replace the uppercase placeholders, keeping the alias `model-server`:

```text
Host model-server
    HostName YOUR_SERVER_HOSTNAME_OR_IP
    User YOUR_SSH_USER
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Connect once with `ssh model-server`, verify the host fingerprint through a trusted channel, and type `exit` after login. Then run this exact command in a dedicated **client terminal** on any of the three platforms:

```text
ssh -N -T -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=yes -L 127.0.0.1:11435:127.0.0.1:11434 model-server
```

Leave it running. Password/passphrase prompts are allowed in this manually opened terminal. A quiet terminal is normal. The first port (11435) belongs to the client; the last (11434) belongs to the server. Change the last port if your model uses another port. Binding the listener to `127.0.0.1` keeps it local; there is no need to expose the model API on `0.0.0.0`. See [OpenSSH port forwarding](https://man.openbsd.org/ssh).

Run the Python probe on the client with Base URL `http://127.0.0.1:11435/v1`. If 11435 is busy, select another free client port and update the Base URL. A successful SSH login does not prove the target API is running. Stop the tunnel with Ctrl+C when finished.

## 6. Configure the completed extension (used in Lab 5)

Use **Preferences: Open User Settings (JSON)** and merge these keys; do not replace your entire settings file. These machine-scoped settings are not taken from project settings. API keys go through **Local Agent: Set API key** into SecretStorage, not this JSON.

**Route A — all client platforms:**

```json
{
  "localagent.transport": "local",
  "localagent.mode": "direct",
  "localagent.baseUrl": "http://127.0.0.1:11434/v1",
  "localagent.modelId": "qwen3:4b"
}
```

For **route B**, keep `transport: local` and change Base URL to `http://127.0.0.1:11435/v1`. Do not choose `ssh` merely because you use a tunnel. The extension starts local Python, which connects through that tunnel.

Empty `localagent.localPython` selects `python` on Windows and `python3` on Linux/macOS. If necessary, set the full executable path, without extra arguments. VS Code may need a restart after PATH changes. Replace `qwen3:4b` with your actual model ID when using another model.

## 7. Route C: optional remote Python bridge

This route launches Python over SSH for every model request; it requires a Linux/macOS server with a POSIX login shell and working noninteractive key authentication. You do not start `ssh -L`. Python is required on the server for live requests and on the client for the offline bridge tests.

If you need a course key, create a **new**, distinct key; never overwrite an existing private key.

**Windows PowerShell:**

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\agent_course"
Get-Content "$env:USERPROFILE\.ssh\agent_course.pub"
```

**Linux/macOS:**

```bash
ssh-keygen -t ed25519 -f "$HOME/.ssh/agent_course"
cat "$HOME/.ssh/agent_course.pub"
```

Append only the public-key line to the server account's `~/.ssh/authorized_keys`; preserve existing keys. On the Linux/macOS server use `mkdir -p ~/.ssh`, `chmod 700 ~/.ssh`, `touch ~/.ssh/authorized_keys`, and `chmod 600 ~/.ssh/authorized_keys`. Unlock an encrypted key in an SSH agent accessible to VS Code. Add `IdentityFile ~/.ssh/agent_course` to the client's `Host model-server` block.

**Any client terminal:**

```text
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes model-server "python3 --version"
```

The command must finish without a password/passphrase prompt. Find the server's Python path if this fails. Then merge:

```json
{
  "localagent.transport": "ssh",
  "localagent.sshHost": "model-server",
  "localagent.sshIdentityFile": "",
  "localagent.remotePython": "python3",
  "localagent.mode": "direct",
  "localagent.baseUrl": "http://127.0.0.1:11434/v1",
  "localagent.modelId": "qwen3:4b"
}
```

An empty identity setting lets OpenSSH use its config/agent. Here Base URL is evaluated **on the server**. In A/B it is evaluated **on the client**. This distinction matters more than the operating system names.

## Acceptance evidence

Record the client OS, model-host OS, route A/B/C, tool execution location, program versions, and successful model discovery plus a short response. Use generic labels in shared notes; omit credentials, account names, host addresses and personal paths. Route A needs no SSH evidence; B needs a working forwarded API; C needs the BatchMode check.

## Knowledge Quiz

**Does a model running on Linux make file tools execute on Linux?**
<details><summary>Answer</summary>No. File tools execute in the VS Code workspace extension host. Server OS and tool execution location are separate.</details>

**Can a Windows model server use route C?**
<details><summary>Answer</summary>Not in this implementation. Use route B; its SSH tunnel does not depend on remote-shell Python quoting.</details>

**Does plain chat prove agent readiness?**
<details><summary>Answer</summary>No. Test streaming, structured tools, and tool-result continuation in the later labs.</details>

**Continue:** [Workshop guide](index.md) · [Lab 2](02-first-extension.md).
