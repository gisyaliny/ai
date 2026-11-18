(localagent-lab-03)=
# 03 - Local/SSH Transport and Streaming

**Format:** hands-on lab · **Suggested time:** 50 minutes · **Original course lessons:** 5–6.

```{admonition} Learning objectives
:class: tip
Write the Python bridge and Node transport; assemble SSE fragments; make a real model request.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 5. Build a portable Python bridge

Create `src/bridge.py` in the client source tree. It is shipped as text with the extension. In local transport, Node runs this file with local Python. This works for a same-machine API or a manually opened SSH tunnel. In SSH transport, Node sends the program to a Linux/macOS server; no manual server copy is needed.

Its input is one JSON object on standard input. A probe calls `/models`; an inference request calls `/chat/completions`. Successful standard output is protocol data only. Diagnostic errors go to standard error so they cannot corrupt the response stream.

**Create `src/bridge.py`:**

```python
"""Ephemeral local/SSH bridge. Credentials arrive on stdin or from configured JSON; stdout is protocol only."""
import json
import os
import sys
import urllib.request
import urllib.error
from urllib.parse import urlparse


def main():
    request = json.load(sys.stdin)
    mode = request.get('mode', 'openclaw')
    payload = request.get('payload', {})
    if mode != 'direct':
        with open(os.path.expanduser(request['config']), encoding='utf-8') as f:
            config = json.load(f)
    if mode == 'direct':
        direct = request.get('direct', {})
        base = direct.get('baseUrl', '').rstrip('/')
        parsed = urlparse(base)
        if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('localhost', '127.0.0.1', '::1') or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('Direct endpoint must be a loopback HTTP(S) URL on the bridge host')
        key = direct.get('apiKey')
        payload['model'] = direct.get('model')
        if not isinstance(payload['model'], str) or not payload['model'].strip():
            raise ValueError('Model ID is required')
    elif mode == 'openclaw':
        gateway = config.get('gateway', {})
        base = 'http://127.0.0.1:' + str(int(gateway.get('port', 18789))) + '/v1'
        auth = gateway.get('auth', {})
        key = auth.get('token') if auth.get('mode', 'token') == 'token' else auth.get('password')
        payload['model'] = 'openclaw/main'
    elif mode == 'qwen':
        primary = config['agents']['defaults']['model']['primary']
        provider_id, model_id = primary.split('/', 1)
        provider = config['models']['providers'][provider_id]
        base, key = provider['baseUrl'].rstrip('/'), provider.get('apiKey')
        if urlparse(base).hostname not in ('localhost', '127.0.0.1', '::1'):
            raise ValueError('Direct model must run on the bridge host loopback interface')
        payload['model'] = model_id
        payload['chat_template_kwargs'] = {'enable_thinking': False, 'reasoning_effort': 'none'}
        payload.update(temperature=0.7, top_p=0.8, presence_penalty=1.5)
    else:
        raise ValueError('Unknown mode')
    if not isinstance(key, str) or not key:
        raise ValueError('Remote credential is missing or uses an unsupported SecretRef')
    probe = request.get('operation') == 'probe'
    url = base + ('/models' if probe else '/chat/completions')
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=None if probe else json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=int(request.get('timeout', 600))) as response:
            if probe:
                data = json.load(response)
                print(json.dumps({'ok': True, 'mode': mode, 'models': [x['id'] for x in data.get('data', [])]}), flush=True)
            else:
                for line in response:
                    sys.stdout.buffer.write(line)
                    sys.stdout.buffer.flush()
    except urllib.error.HTTPError as error:
        detail = error.read(4096).decode(errors='replace').replace(key, '[redacted]')
        if error.code == 404 and mode == 'openclaw':
            detail = 'Enable gateway.http.endpoints.chatCompletions.enabled on the bridge host.'
        raise RuntimeError('Remote HTTP %s: %s' % (error.code, detail)) from None


try:
    main()
except BrokenPipeError:
    pass
except Exception as error:
    print(str(error), file=sys.stderr)
    sys.exit(1)
```

Read the `direct` branch first. It validates a loopback HTTP(S) URL, uses the explicit model ID, and adds the Bearer token. The two other branches are compatibility modes; you do not need OpenClaw for the beginner path.

The loopback check avoids intentionally routing the direct-mode credential to an arbitrary host in the URL. It is not a comprehensive network sandbox: the trusted local service, redirects, local proxy configuration, and the account environment still matter. Do not use untrusted endpoints or treat this implementation as a security boundary against a hostile local service.

The API key exists temporarily in the extension and Python process memory. Base64 encoding of the program is not encryption. SSH provides transport encryption. The key travels through standard input, not as a command-line argument in the remote Python command.

The source preserves legacy configuration behavior: `direct` needs no OpenClaw file; `qwen` and `openclaw` read the configured JSON file. This reader does not implement JSON5 or dynamically resolved secret references.

**Checkpoint:** Compile without executing network requests:

**Windows PowerShell:**

```powershell
python -c "import ast,pathlib; ast.parse(pathlib.Path('src/bridge.py').read_text(encoding='utf-8')); print('Python syntax OK')"
```

**Linux Bash / macOS zsh:**

```bash
python -c "import ast,pathlib; ast.parse(pathlib.Path('src/bridge.py').read_text(encoding='utf-8')); print('Python syntax OK')"
```

## 6. Add transport and streaming

### 6.1 Understand streaming before parsing it

The model's streaming response uses **Server-Sent Events / SSE（服务器发送事件）**. A typical text fragment looks like this:

```text
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":" world"}}]}

data: [DONE]

```

This is an illustrative wire fragment, not a file to create. A chunk arriving from the bridge is not necessarily a full event or even a full JSON string. Buffer until the blank line marking an event boundary. Tool names and argument strings may arrive in fragments too. Assemble them before parsing arguments or executing a tool.

### 6.2 Create the complete transport

**Create `src/transport.js`:**

```javascript
'use strict';
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const bridge = fs.readFileSync(path.join(__dirname, 'bridge.py'), 'utf8');
const quote = value => "'" + String(value).replace(/'/g, "'\\''") + "'";

class SSEReader {
  constructor(onEvent) { this.buffer = ''; this.onEvent = onEvent; }
  push(chunk) {
    this.buffer += chunk;
    if (this.buffer.length > 2_000_000) throw new Error('Server event exceeded size limit');
    let match;
    while ((match = /\r?\n\r?\n/.exec(this.buffer))) {
      const block = this.buffer.slice(0, match.index);
      this.buffer = this.buffer.slice(match.index + match[0].length);
      const data = block.split(/\r?\n/).filter(x => x.startsWith('data:')).map(x => x.slice(5).trimStart()).join('\n');
      if (data) this.onEvent(data);
    }
  }
}


function sshCommand(options) {
  if (!/^[a-zA-Z0-9_][a-zA-Z0-9_.@:\-]*$/.test(options.host || '')) throw new Error('Invalid SSH host');
  const args = ['-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12', '-o', 'ServerAliveInterval=20', '-o', 'ServerAliveCountMax=3'];
  if (options.identity) args.push('-o', 'IdentitiesOnly=yes', '-i', options.identity.replace(/^~(?=[/\\])/, os.homedir()));
  const encoded = Buffer.from(bridge).toString('base64');
  const code = `import base64;exec(compile(base64.b64decode('${encoded}'),'<agent-bridge>','exec'))`;
  args.push(options.host, `${quote(options.python || 'python3')} -u -c ${quote(code)}`);
  return { executable: options.executable || 'ssh', args };
}

function bridgeRequest(options, request, signal, onData) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new Error('Stopped'));
    const transport = options.transport || 'local';
    let executable, args;
    if (transport === 'local') {
      executable = options.localPython || (process.platform === 'win32' ? 'python' : 'python3');
      args = ['-u', path.join(__dirname, 'bridge.py')];
    } else if (transport === 'ssh') {
      ({ executable, args } = sshCommand(options));
    } else return reject(new Error('Unknown transport: ' + transport));
    const child = spawn(executable, args, {
      windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    let stderr = '', output = '', failure, timer;
    const abort = () => { failure = new Error('Stopped; remote operations may still be finishing.'); child.kill(); };
    signal?.addEventListener('abort', abort, { once: true });
    timer = setTimeout(() => { failure = new Error('Connection or inference timed out. Check Python, the tunnel (if used), and the model service.'); child.kill(); }, ((request.timeout || 600) + 15) * 1000);
    child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
    child.stdout.on('data', data => {
      try {
        if (onData) onData(data);
        else { output += data; if (output.length > 2_000_000) throw new Error('Response too large'); }
      } catch (error) { failure = error; child.kill(); }
    });
    child.stderr.on('data', data => { stderr = (stderr + data).slice(-4096); });
    child.stdin.on('error', () => {});
    child.on('error', error => { failure = error; });
    child.on('close', code => {
      clearTimeout(timer); signal?.removeEventListener('abort', abort);
      if (failure) reject(failure);
      else if (code !== 0) reject(new Error(stderr.trim() || `Bridge exited (${code})`));
      else resolve(output);
    });
    child.stdin.end(JSON.stringify({ ...request, direct: options.direct, config: options.config || '~/.openclaw/openclaw.json' }));
  });
}

async function completion(options, payload, signal, onText = () => {}) {
  const message = { role: 'assistant', content: '' }, calls = new Map();
  let done = false, finish;
  const reader = new SSEReader(data => {
    if (data === '[DONE]') { done = true; return; }
    const event = JSON.parse(data);
    if (event.error) throw new Error(event.error.message || 'Remote API error');
    const choice = event.choices?.[0];
    if (!choice) return;
    if (choice.finish_reason) finish = choice.finish_reason;
    const delta = choice.delta || {};
    if (delta.content) { message.content += delta.content; onText(delta.content); }
    if (message.content.length > 500_000) throw new Error('Reply exceeded size limit');
    for (const part of delta.tool_calls || []) {
      const index = part.index ?? 0;
      const call = calls.get(index) || { id: '', type: 'function', function: { name: '', arguments: '' } };
      if (part.id) call.id = part.id;
      if (part.function?.name) call.function.name += part.function.name;
      if (part.function?.arguments) call.function.arguments += part.function.arguments;
      if (call.function.arguments.length > 200_000) throw new Error('Tool arguments exceeded size limit');
      calls.set(index, call);
    }
  });
  await bridgeRequest(options, { mode: options.mode, timeout: options.timeout, payload: { ...payload, stream: true } }, signal, chunk => reader.push(chunk));
  if (!done) throw new Error('Incomplete response. Unfinished tool calls were not executed.');
  if (finish === 'length') throw new Error('Output limit reached. Reduce the task or increase the output limit.');
  if (calls.size) {
    message.tool_calls = [...calls.values()];
    for (const call of message.tool_calls) if (!call.id || !call.function.name) throw new Error('Incomplete tool call');
  }
  if (!message.content && !calls.size) throw new Error('Empty model response');
  return message;
}

module.exports = { SSEReader, sshCommand, bridgeRequest, completion };
```

`bridgeRequest()` selects local Python by default; `sshCommand()` is used only for the optional Linux/macOS remote route. Local Python receives UTF-8 input and requires no shell quoting. `spawn()` receives an argument array so local shell expansion does not interpret the host or code. The optional remote command requires a POSIX login shell; `quote()` handles embedded single quotes. Host validation rejects option-shaped values such as `-oProxyCommand=...`.

`BatchMode=yes` prevents hidden password waits. `StrictHostKeyChecking=yes` requires a previously trusted server. Specifying a key uses `IdentitiesOnly=yes` so the test matches the intended credential.

The `completion()` function produces an assistant message. If it contains tool calls, those calls are complete enough for the controller to dispatch only after the stream ends. A missing `[DONE]`, malformed JSON, or output-length finish condition prevents unfinished tool execution.

This parser expects the service behavior exercised by our live tests, including a `[DONE]` sentinel. “OpenAI-compatible” is not a guarantee that every server streams identically. Validate a replacement service before trusting its tools.

### 6.3 Make the first request without the sidebar

Create `test/options.js` before the smoke test. All live tests share these environment-driven options. They do not read VS Code settings.

```javascript
// Shared by terminal tests; VS Code settings are configured separately.
module.exports = function testOptions(mode = 'direct') {
  const env = process.env;
  return {
    transport: env.AGENT_TRANSPORT || 'local',
    localPython: env.AGENT_PYTHON,
    host: env.AGENT_SSH_HOST || 'model-server',
    identity: env.AGENT_SSH_IDENTITY || '',
    python: env.AGENT_REMOTE_PYTHON || 'python3',
    mode, timeout: 300,
    direct: {
      baseUrl: env.AGENT_BASE_URL || 'http://127.0.0.1:11434/v1',
      model: env.AGENT_MODEL || 'YOUR_MODEL_ID',
      apiKey: env.LOCALAGENT_API_KEY
    }
  };
};
```


**Create `test/smoke.js`:**

```javascript
const { bridgeRequest, completion } = require('../src/transport');

async function main() {
  if (!process.env.LOCALAGENT_API_KEY) throw new Error('Set LOCALAGENT_API_KEY first');
  const options = require('./options')();
  console.log(await bridgeRequest(options, {mode: 'direct', operation: 'probe', timeout: 20}));
  await completion(options, {
    messages: [{role: 'user', content: 'Explain what an extension host does in one sentence.'}],
    max_tokens: 256
  }, undefined, text => process.stdout.write(text));
  process.stdout.write('\n');
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
```

**Create `test/with-key.py`:**

```python
import getpass
import os
import subprocess
import sys

if len(sys.argv) < 2:
    raise SystemExit("Usage: python test/with-key.py node test/smoke.js")
env = os.environ.copy()
env["LOCALAGENT_API_KEY"] = getpass.getpass("API key (ollama for default local Ollama): ")
raise SystemExit(subprocess.call(sys.argv[1:], env=env))
```

For terminal-only tests, configure the endpoint and model in the current process. The Python launcher prompts privately for a credential and passes it only to the test subprocess; it does not save it or place it in shell history. For default local Ollama enter `ollama`; for another service enter its configured key.

**Windows PowerShell:**

```powershell
$env:AGENT_BASE_URL = 'http://127.0.0.1:11434/v1'
$env:AGENT_MODEL = 'qwen3:4b'
python test/with-key.py node test/smoke.js
```

**Linux Bash / macOS zsh:**

```bash
export AGENT_BASE_URL='http://127.0.0.1:11434/v1'
export AGENT_MODEL='qwen3:4b'
python3 test/with-key.py node test/smoke.js
```

For route B change the Base URL to port 11435 and keep the tunnel open. For route C set `AGENT_TRANSPORT=ssh`, `AGENT_SSH_HOST=model-server`, and the server-side Base URL; optionally set `AGENT_REMOTE_PYTHON` and `AGENT_SSH_IDENTITY`. PowerShell uses `$env:NAME = 'value'`; Bash/zsh uses `export NAME='value'`. `AGENT_PYTHON` overrides local Python for tests only; the installed extension uses `localagent.localPython`.

**Checkpoint:** You see a model list followed by a streamed explanation. If this fails, fix the transport before debugging the UI. The production extension will use a password input and SecretStorage rather than this environment-variable workflow.

```{admonition} Lab acceptance evidence
:class: important
Run test/smoke.js and capture the advertised model IDs and a streamed reply without recording the API key.
```


**Continue:** [Previous](02-first-extension.md) · [Next](04-project-tools.md) · [Workshop guide](index.md)

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Does Base64 encrypt the bridge?**

<details>
<summary>Answer</summary>

No. Base64 encodes program text; SSH provides transport encryption.

</details>

**2. Why must the parser buffer chunks?**

<details>
<summary>Answer</summary>

A transport chunk can contain only part of an SSE event, JSON string, or tool argument.

</details>

**3. What happens if DONE never arrives?**

<details>
<summary>Answer</summary>

The transport rejects the incomplete response rather than executing unfinished tool calls.

</details>
