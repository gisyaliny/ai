(macstudio-lab-03)=
# 03 - SSH Bridge and Streaming Responses

**Format:** hands-on lab · **Suggested time:** 50 minutes · **Original course lessons:** 5–6.

```{admonition} Learning objectives
:class: tip
Write the Python bridge and Node transport; assemble SSE fragments; make a real model request.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 5. Build the remote Python bridge

Create `src/bridge.py` in the Windows source tree. It is shipped as text with the extension. The Node transport will send its program text to Python on the Mac; you do not need to copy or install the file on the Mac manually.

Its input is one JSON object on standard input. A probe calls `/models`; an inference request calls `/chat/completions`. Successful standard output is protocol data only. Diagnostic errors go to standard error so they cannot corrupt the response stream.

**Create `src/bridge.py`:**

```python
"""Ephemeral SSH bridge. Credentials are passed over SSH or loaded remotely; stdout is protocol only."""
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
            raise ValueError('Direct endpoint must be a loopback HTTP(S) URL on the Mac')
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
            raise ValueError('Direct model must run on the remote Mac loopback interface')
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
            detail = 'Enable gateway.http.endpoints.chatCompletions.enabled on the Mac.'
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

The API key exists temporarily in the Windows extension and remote process memory. Base64 encoding of the program is not encryption. SSH provides transport encryption. The key travels through standard input, not as a command-line argument in the remote Python command.

The source preserves legacy configuration behavior: `direct` needs no OpenClaw file; `qwen` and `openclaw` read the configured JSON file. This reader does not implement JSON5 or dynamically resolved secret references.

**Checkpoint:** Compile without executing network requests:

```powershell
python -c "import ast,pathlib; ast.parse(pathlib.Path('src/bridge.py').read_text(encoding='utf-8')); print('Python syntax OK')"
```

## 6. Add SSH transport and streaming

### 6.1 Understand streaming before parsing it

The model's streaming response uses **Server-Sent Events / SSE（服务器发送事件）**. A typical text fragment looks like this:

```text
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":" world"}}]}

data: [DONE]

```

This is an illustrative wire fragment, not a file to create. A chunk arriving from SSH is not necessarily a full event or even a full JSON string. Buffer until the blank line marking an event boundary. Tool names and argument strings may arrive in fragments too. Assemble them before parsing arguments or executing a tool.

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

function sshRequest(options, request, signal, onData) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new Error('Stopped'));
    if (!/^[a-zA-Z0-9_][a-zA-Z0-9_.@:\-]*$/.test(options.host || '')) return reject(new Error('Invalid SSH host'));
    const args = ['-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12', '-o', 'ServerAliveInterval=20', '-o', 'ServerAliveCountMax=3'];
    if (options.identity) args.push('-o', 'IdentitiesOnly=yes', '-i', options.identity.replace(/^~(?=[/\\])/, os.homedir()));
    const encoded = Buffer.from(bridge).toString('base64');
    const code = `import base64;exec(compile(base64.b64decode('${encoded}'),'<macstudio-bridge>','exec'))`;
    args.push(options.host, `${quote(options.python || '/usr/bin/python3')} -u -c ${quote(code)}`);
    const child = spawn(options.executable || 'ssh', args, { windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'] });
    let stderr = '', output = '', failure, timer;
    const abort = () => { failure = new Error('Stopped; remote operations may still be finishing.'); child.kill(); };
    signal?.addEventListener('abort', abort, { once: true });
    timer = setTimeout(() => { failure = new Error('Connection or inference timed out. Check the VPN and Mac service.'); child.kill(); }, ((request.timeout || 600) + 15) * 1000);
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
      else if (code !== 0) reject(new Error(stderr.trim() || `SSH exited (${code})`));
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
  await sshRequest(options, { mode: options.mode, timeout: options.timeout, payload: { ...payload, stream: true } }, signal, chunk => reader.push(chunk));
  if (!done) throw new Error('Incomplete response. Unfinished tool calls were not executed.');
  if (finish === 'length') throw new Error('Output limit reached. Reduce the task or increase the output limit.');
  if (calls.size) {
    message.tool_calls = [...calls.values()];
    for (const call of message.tool_calls) if (!call.id || !call.function.name) throw new Error('Incomplete tool call');
  }
  if (!message.content && !calls.size) throw new Error('Empty model response');
  return message;
}

module.exports = { SSEReader, sshRequest, completion };
```

`spawn()` receives an argument array so local shell expansion does not interpret the host or code. The remote command still requires shell quoting; `quote()` handles embedded single quotes. Host validation rejects option-shaped values such as `-oProxyCommand=...`.

`BatchMode=yes` prevents hidden password waits. `StrictHostKeyChecking=yes` requires a previously trusted server. Specifying a key uses `IdentitiesOnly=yes` so the test matches the intended credential.

The `completion()` function produces an assistant message. If it contains tool calls, those calls are complete enough for the controller to dispatch only after the stream ends. A missing `[DONE]`, malformed JSON, or output-length finish condition prevents unfinished tool execution.

This parser expects the service behavior exercised by our live tests, including a `[DONE]` sentinel. “OpenAI-compatible” is not a guarantee that every server streams identically. Validate a replacement service before trusting its tools.

### 6.3 Make the first request without the sidebar

**Create `test/smoke.js`:**

```javascript
const { sshRequest, completion } = require('../src/transport');

async function main() {
  if (!process.env.MACSTUDIO_API_KEY) throw new Error('Set MACSTUDIO_API_KEY first');
  const options = {
    host: 'macstudio', identity: '~/.ssh/macstudio_course',
    python: '/usr/bin/python3', mode: 'direct', timeout: 120,
    direct: {
      baseUrl: 'http://127.0.0.1:11436/v1',
      model: 'YOUR_MODEL_ID',
      apiKey: process.env.MACSTUDIO_API_KEY
    }
  };
  console.log(await sshRequest(options, {mode: 'direct', operation: 'probe', timeout: 20}));
  await completion(options, {
    messages: [{role: 'user', content: 'Explain what an extension host does in one sentence.'}],
    max_tokens: 256
  }, undefined, text => process.stdout.write(text));
  process.stdout.write('\n');
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
```

For terminal-only tests, set the API key in this PowerShell process. The following works in Windows PowerShell by prompting for a secure string and converting it only for the child process environment. The environment value is still plaintext while the test runs; do not print it or save it in a script.

```powershell
$courseSecret = Read-Host 'Local API key' -AsSecureString
$env:MACSTUDIO_API_KEY = [System.Net.NetworkCredential]::new('', $courseSecret).Password
node test/smoke.js
Remove-Item Env:MACSTUDIO_API_KEY
Remove-Variable courseSecret
```

**Checkpoint:** You see a model list followed by a streamed explanation. If this fails, fix the transport before debugging the UI. The production extension will use a password input and SecretStorage rather than this environment-variable workflow.

```{admonition} Lab acceptance evidence
:class: important
Run test/smoke.js and capture the advertised model IDs and a streamed reply without recording the API key.
```

> **Image Suggestion (Nanobanana Prompt)**: Create a clean educational illustration for “SSH Bridge and Streaming Responses”, using a neutral VS Code-inspired desktop palette, legible monospace labels, a Windows workstation and a Mac Studio where relevant, and clearly marked “Illustration” text. Emphasize the lab's actual control or execution boundary. Include no real credentials, personal paths, or fabricated test results. Use even lighting and a flat technical-documentation style rather than decorative effects.

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
