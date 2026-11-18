(macstudio-lab-04)=
# 04 - Project Tools and the Agent Loop

**Format:** hands-on lab · **Suggested time:** 45 minutes · **Original course lessons:** 7–8.

```{admonition} Learning objectives
:class: tip
Implement guarded file reads and exact edits; understand schemas, tool IDs, and conversation state.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 7. Implement project file operations

The model should use project-relative paths. Do not accept a model-generated absolute path and pass it directly to `readFile()`.

Our helper blocks common sensitive names, rejects traversal, resolves existing ancestors to check links, limits reads, and replaces an exact unique substring. For a new file, the old text must be empty; for an existing file, it must occur exactly once.

**Create `src/files.js`:**

```javascript
'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const ignored = new Set(['.git', '.ssh', '.aws', '.azure', '.gnupg', '.codex', '.openclaw', '.vscode', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next']);
function blocked(relative) {
  return relative.replace(/\\/g, '/').split('/').some(x => ignored.has(x.toLowerCase()) || /^\.env(?:\.|$)/i.test(x) || /^(?:id_rsa|id_ed25519|credentials(?:\.json)?|secrets?(?:\..*)?|\.npmrc|\.pypirc)$/i.test(x) || /\.(?:pem|key|p12|pfx)$/i.test(x));
}
function within(root, candidate) { const r = path.relative(root, candidate); return r === '' || (!r.startsWith('..' + path.sep) && r !== '..' && !path.isAbsolute(r)); }
async function resolvePath(root, relative, allowRoot = false) {
  if (typeof relative !== 'string' || relative.includes('\0') || relative.includes(':') || path.isAbsolute(relative) || /^[\\/]/.test(relative)) throw new Error('Use a project-relative path');
  if (relative.split(/[\\/]/).includes('..') || blocked(relative)) throw new Error('This path is not allowed');
  const realRoot = await fs.realpath(root), target = path.resolve(realRoot, relative);
  if (!within(realRoot, target) || (!allowRoot && target === realRoot)) throw new Error('Path escapes the project');
  let parent = target;
  while (true) {
    try {
      const real = await fs.realpath(parent);
      if (!within(realRoot, real) || blocked(path.relative(realRoot, real))) throw new Error('Link points outside the project or into a restricted directory');
      break;
    }
    catch (error) { if (error.code !== 'ENOENT') throw error; parent = path.dirname(parent); }
  }
  return target;
}
function hash(text) { return crypto.createHash('sha256').update(text).digest('hex'); }
function editText(original, oldText, newText, exists) {
  if (typeof oldText !== 'string' || typeof newText !== 'string') throw new Error('Edit arguments must be strings');
  if (newText.length > 120_000) throw new Error('Edit too large; split the file');
  if (!exists) { if (oldText !== '') throw new Error('old_text must be empty for a new file'); return newText; }
  if (!oldText) throw new Error('Existing files require nonempty unique old_text');
  const pos = original.indexOf(oldText);
  if (pos < 0 || original.indexOf(oldText, pos + 1) >= 0) throw new Error('old_text was missing or ambiguous; read the file again');
  return original.slice(0, pos) + newText + original.slice(pos + oldText.length);
}
async function readText(root, relative) {
  const target = await resolvePath(root, relative);
  const stat = await fs.stat(target);
  if (!stat.isFile() || stat.size > 160_000) throw new Error('Only text files up to 160 KB are supported');
  const text = await fs.readFile(target, 'utf8');
  if (text.includes('\0')) throw new Error('Binary files are not supported');
  return text;
}
async function listFiles(root, relative = '.', limit = 400) {
  const start = await resolvePath(root, relative, true), result = [], queue = [start];
  while (queue.length && result.length < limit) {
    const dir = queue.shift();
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries.sort((a,b) => a.name.localeCompare(b.name))) {
      const full = path.join(dir, entry.name), rel = path.relative(await fs.realpath(root), full).split(path.sep).join('/');
      if (blocked(rel) || entry.isSymbolicLink()) continue;
      if (entry.isDirectory()) queue.push(full);
      else if (entry.isFile()) result.push(rel);
      if (result.length >= limit) break;
    }
    if (queue.length > 1000) break;
  }
  return { files: result, truncated: result.length >= limit || queue.length > 0 };
}
module.exports = { blocked, within, resolvePath, hash, editText, readText, listFiles };
```

Notice the difference between a proposal and a write. `editText()` returns the proposed new string; it does not save anything. The extension controller will store the original content and a hash, display the diff, and check for intervening changes before applying it.

These helpers are practical safeguards for a trusted local workspace, not a complete filesystem sandbox. A path can change between validation and use; a hostile process racing symlinks is outside this design. The filename denylist is not a secret scanner. The NUL-byte test catches common binary content, not every possible encoding. Reads are UTF-8-oriented. Large repositories are only partially listed and searched, and this implementation does not parse `.gitignore`.

**Create `test/core.test.js`:**

```javascript
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { SSEReader, sshRequest } = require('../src/transport');
const { resolvePath, readText, listFiles, editText, hash } = require('../src/files');

test('SSE handles fragmented CRLF, multiple events and comments', () => {
  const events = [], parser = new SSEReader(x => events.push(x));
  for (const piece of [': ping\r\n\r\nda', 'ta: {"v":"café"}\r', '\n\r\ndata: [DO', 'NE]\n\n']) parser.push(piece);
  assert.deepEqual(events, ['{"v":"café"}', '[DONE]']);
});

test('workspace access rejects traversal, credentials and escaping symlinks', async t => {
  const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'macstudio-path-'));
  t.after(() => fs.rm(temp, { recursive: true, force: true }));
  const root = path.join(temp, 'project'), outside = path.join(temp, 'outside');
  await fs.mkdir(root); await fs.mkdir(outside);
  await fs.writeFile(path.join(root, 'hello.txt'), 'hello');
  await fs.writeFile(path.join(root, '.env'), 'not-a-real-secret');
  await fs.symlink(outside, path.join(root, 'escape'), process.platform === 'win32' ? 'junction' : 'dir');
  await fs.mkdir(path.join(root, '.ssh'));
  await fs.symlink(path.join(root, '.ssh'), path.join(root, 'hidden-link'), process.platform === 'win32' ? 'junction' : 'dir');
  for (const value of ['../outside/x', '..\\outside\\x', '/etc/passwd', 'C:\\Users\\x', '.env', '.ssh/key', 'a.pem', '.git/config', 'escape/new.txt', 'hidden-link/file']) {
    await assert.rejects(resolvePath(root, value), undefined, value);
  }
  assert.equal(await readText(root, 'hello.txt'), 'hello');
  assert.deepEqual((await listFiles(root)).files, ['hello.txt']);
  await fs.writeFile(path.join(root, 'binary.bin'), Buffer.from([0, 1, 2]));
  await assert.rejects(readText(root, 'binary.bin'));
});

test('edits require unique exact anchors and preserve surrounding content', () => {
  assert.equal(editText('a\nb\nc', 'b', 'B', true), 'a\nB\nc');
  assert.throws(() => editText('a a', 'a', 'b', true));
  assert.throws(() => editText('a', 'x', 'b', true));
  assert.throws(() => editText('a', '', 'b', true));
  assert.equal(editText('', '', 'new', false), 'new');
  assert.notEqual(hash('original'), hash('changed'));
});

test('SSH refuses option-shaped host and pre-cancelled requests', async () => {
  await assert.rejects(sshRequest({ host: '-oProxyCommand=bad' }, {}), /SSH/);
  const controller = new AbortController(); controller.abort();
  await assert.rejects(sshRequest({ host: 'macstudio' }, {}, controller.signal), /Stop/);
});
```

**Run on Windows:**

```powershell
npm.cmd test
```

Expect four passing tests. The link test creates temporary directories and junctions. A permissions error creating the link is a test-environment failure, not proof that the path validation is correct. Run the test where temporary directory/junction creation is allowed rather than silently dropping the test.

**Checkpoint:** Explain why `../outside.txt`, `.env`, and a link to a directory outside the project must all be rejected, while `src/main.py` may be accepted.

## 8. Understand tools, state, and the controller

Before pasting the full controller, understand its vocabulary. A tool schema describes the name, intended use, argument types, and required arguments. It does not grant permission or execute code.

**Illustration — one tool description:**

```javascript
const exampleTool = {
  type: 'function',
  function: {
    name: 'local_read_file',
    description: 'Read a UTF-8 file in the client project.',
    parameters: {
      type: 'object',
      properties: { path: { type: 'string' } },
      required: ['path'],
      additionalProperties: false
    }
  }
};
```

Our implementation validates important arguments again in tool handlers. It does not include a general JSON Schema validator. Never assume that sending `additionalProperties: false` makes a model's output trustworthy.

### 8.1 Follow one exchange

**Illustration — conversation messages, not a standalone API request:**

```json
[
  {"role":"user","content":"Read fixture.js and explain its bug."},
  {"role":"assistant","content":"","tool_calls":[
    {"id":"call_1","type":"function","function":{
      "name":"local_read_file","arguments":"{\"path\":\"fixture.js\"}"
    }}
  ]},
  {"role":"tool","tool_call_id":"call_1","content":"{\"content\":\"function add(a,b){return a-b;}\"}"}
]
```

The controller sends these messages back to the model, which can now reason from the actual file content. The call ID connects the result to its request. `function.arguments` is a JSON-encoded string and must be parsed once it is complete.

### 8.2 Know what each state variable owns

| State | Purpose | Persistence |
|---|---|---|
| `history` | Protocol messages sent to the model | Current extension session |
| `messages` | Rows displayed in the sidebar | Current extension session, bounded |
| `pending` | Proposed changes awaiting review | Current extension session |
| `attachments` | Selected file text for the next turn | Consumed when sent |
| `root` | Selected project directory | Until new chat |
| `controller` | Abort signal for active generation | Current request |
| SecretStorage entry | Direct-mode API credential | Managed by VS Code |

The sidebar gets a limited state object. It does not get the API key or the full original/replacement text for every edit. The extension owns actual file operations and credentials.

### 8.3 Understand the review boundary

A proposed edit has an ID, path, explanation, original content hash, and replacement content. The model receives `proposed_only`. It must not claim the file was changed. The user opens a native diff and clicks Apply. Before applying, the controller reads the latest editor content and rejects stale proposals.

The user can still approve a harmful command; a terminal command has the user's normal permissions. The system prompt asks the model not to bypass edit review with shell commands, but that sentence is not enforcement. Review the complete command before approving it.

**Checkpoint:** Explain why an assistant sentence saying “I fixed it” is not evidence that a file changed. The application should record and display the actual write result.

```{admonition} Lab acceptance evidence
:class: important
Pass the four core tests and explain one read-tool exchange using a matching tool_call_id.
```

> **Image Suggestion (Nanobanana Prompt)**: Create a clean educational illustration for “Project Tools and the Agent Loop”, using a neutral VS Code-inspired desktop palette, legible monospace labels, a Windows workstation and a Mac Studio where relevant, and clearly marked “Illustration” text. Emphasize the lab's actual control or execution boundary. Include no real credentials, personal paths, or fabricated test results. Use even lighting and a flat technical-documentation style rather than decorative effects.

**Continue:** [Previous](03-ssh-and-streaming.md) · [Next](05-controller-and-interface.md) · [Workshop guide](index.md)

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. Does editText save a file?**

<details>
<summary>Answer</summary>

No. It creates a proposed replacement string for later review.

</details>

**2. Does a tool schema enforce filesystem permissions?**

<details>
<summary>Answer</summary>

No. The application must validate arguments and enforce path and approval policy.

</details>

**3. Why check a content hash before applying?**

<details>
<summary>Answer</summary>

To detect a proposal based on content that the user has subsequently changed.

</details>
