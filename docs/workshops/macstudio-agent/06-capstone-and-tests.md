(macstudio-lab-06)=
# 06 - Capstone: Fix, Review, and Verify

**Format:** hands-on lab · **Suggested time:** 60 minutes · **Original course lessons:** 11–12.

```{admonition} Learning objectives
:class: tip
Fix a deliberately broken function and verify the full edit workflow; run offline, live, and host tests.
```

**Start here:** [Workshop guide](index.md). Download the reference bundle there before the lab. Each file block is complete unless marked Illustration. In this workshop, “Lesson” refers to the original numbered sections retained below.

## 11. Complete a coding task from request to verified change

Use a toy project first. Keep it outside the extension source tree so you can distinguish the code that implements the assistant from the code it edits.

**Run on Windows in a separate PowerShell terminal:**

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\agent-playground"
Set-Location "$env:USERPROFILE\Documents\agent-playground"
@'
function add(a, b) {
  return a - b;
}
module.exports = { add };
'@ | Set-Content -Encoding utf8 math.js
@'
const assert = require('node:assert/strict');
const { add } = require('./math');
assert.equal(add(2, 3), 5);
console.log('PASS');
'@ | Set-Content -Encoding utf8 math.test.js
node math.test.js
```

The assertion should fail. That is intentional. Open this folder in the Development Host and send:

```text
Read math.js and math.test.js. Explain why the test fails.
Do not change files or run commands yet.
```

Expect read-tool activity and an explanation that subtraction does not implement addition. Then send:

```text
Propose the smallest change to fix add(). Read the file first.
Do not use terminal commands to edit it. Leave the change for my review.
```

Expect a pending change card. Open **View diff**. The before side should use `a - b`; the after side should use `a + b`. Confirm the file has not changed yet. Click **Apply and save**, then send:

```text
Run node math.test.js to verify the applied change.
```

Check the approval dialog: the directory should be your disposable project and the command should be the requested test. Approve once. Expect `PASS` and exit code 0.

### Failure drill: prevent a stale overwrite

Ask for another small proposal, then manually edit the target file before applying it. The extension should refuse to overwrite your new content. Reject the stale proposal and ask the model to reread the file. Never resolve the failure by deleting the comparison check.

### Failure drill: inspect command rejection

Ask the model to run `node --version`, then cancel the approval dialog. The model should receive a denied result, not an invented version string. A refusal should leave the command unexecuted.

### Attach only relevant context

Open a text file, select a function, and choose **File / selection**. Send a question about that selection. The attachment is consumed with the next message. File contents and tool output are lower-trust data; instructions hidden in a source file should not override the user's request.

**Checkpoint:** A real file changed only after review, and an actual test—not the model's confidence—verified the result.

## 12. Test each boundary

Use three levels: offline logic tests, live model-protocol tests, and a real VS Code extension-host test. A passing HTTP request does not prove the tool loop works. A passing tool loop does not prove the Webview loaded. A successful proposed edit does not prove stale edits are rejected.

### 12.1 Test the Python bridge without a model

**Create `test/bridge_test.py`:**

```python
"""Offline regression: direct mode works without OpenClaw and rejects nonlocal URLs."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import subprocess
import sys
import threading
import unittest


class BridgeTest(unittest.TestCase):
    def test_direct_transport(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.headers.get('Authorization') != 'Bearer fixture-key':
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b'Invalid fixture-key')
                    return
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"fixture-model"}]}')

            def log_message(self, *args):
                pass

        server = HTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        request = {'mode': 'direct', 'operation': 'probe', 'config': 'does-not-exist.json',
                   'direct': {'baseUrl': f'http://127.0.0.1:{server.server_port}/v1',
                              'model': 'fixture-model', 'apiKey': 'fixture-key'}}

        def run():
            return subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'src/bridge.py')],
                                  input=json.dumps(request), text=True, capture_output=True, timeout=5)

        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['models'], ['fixture-model'])
        for url in ['http://example.com/v1', 'file:///etc/passwd', 'http://user:pass@127.0.0.1/v1']:
            request['direct']['baseUrl'] = url
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('loopback', result.stderr)


if __name__ == '__main__':
    unittest.main()
```

**Run:** `npm.cmd run test:bridge`.

The fixture server runs on local loopback. The test proves direct mode works without an OpenClaw configuration and rejects the tested non-loopback or credential-bearing URLs. It does not test all HTTP failures, redirects, or real credentials. If your execution environment forbids loopback sockets, run this test in a normal local terminal.

### 12.2 Test actual tool calling and continuation

**Create `test/live.js`:**

```javascript
// Explicit live test: calls the user's Mac; uses fixture text only, never sends messages.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { completion, sshRequest } = require('../src/transport');
async function main() {
  const results = [];
  for (const mode of (process.env.MACSTUDIO_TEST_MODES || 'direct').split(',')) {
    const options = { host: 'macstudio', identity: '~/.ssh/macstudio_course', mode, timeout: 300 };
    if (mode === 'direct') {
      assert.ok(process.env.MACSTUDIO_API_KEY, 'Set MACSTUDIO_API_KEY for the live test');
      options.direct = { baseUrl: 'http://127.0.0.1:11436/v1', model: 'YOUR_MODEL_ID', apiKey: process.env.MACSTUDIO_API_KEY };
    }
    const probe = JSON.parse(await sshRequest(options, { mode, operation: 'probe', timeout: 30 }));
    assert.equal(probe.ok, true);
    console.log(mode, 'probe passed');
    const tools = [{ type: 'function', function: { name: 'local_read_file', description: 'Read a test fixture on the CLIENT PC. The remote host cannot read this file.', parameters: { type: 'object', properties: { path: { type: 'string' } }, required: ['path'], additionalProperties: false } } }];
    const session = 'vscode-test:' + Date.now();
    const messages = [{ role: 'system', content: 'Integration test. Use only the supplied client local_read_file function. Do not send messages, access server files, execute commands, or modify anything.' }, { role: 'user', content: 'Call local_read_file with path fixture.txt. After its result, reply only with the code contained in the fixture.' }];
    const started = Date.now();
    const first = await completion(options, { messages, tools, tool_choice: { type: 'function', function: { name: 'local_read_file' } }, max_tokens: 1024, user: session });
    assert.equal(first.tool_calls?.[0]?.function.name, 'local_read_file');
    assert.equal(JSON.parse(first.tool_calls[0].function.arguments).path, 'fixture.txt');
    messages.push(first);
    for (const call of first.tool_calls) messages.push({ role: 'tool', tool_call_id: call.id, content: 'Fixture code: WINDOWS_MAC_BRIDGE_OK' });
    const last = await completion(options, { messages, tools, tool_choice: 'none', max_tokens: 1024, user: session });
    assert.match(last.content, /WINDOWS_MAC_BRIDGE_OK/);
    results.push({ mode, success: true, seconds: (Date.now() - started) / 1000, answer: last.content });
    console.log(mode, 'tool call + tool-result continuation passed', last.content);
  }
  await fs.mkdir(path.join(__dirname, '../test-results'), { recursive: true });
  await fs.writeFile(path.join(__dirname, '../test-results/live.json'), JSON.stringify(results, null, 2));
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
```

Set `MACSTUDIO_API_KEY` with the secure-prompt pattern from Lesson 6, then run:

```powershell
npm.cmd run test:live
```

This test forces a fixture read call, supplies a synthetic tool result, and verifies that the next answer includes the returned fixture code. It tests protocol handling, not actual filesystem access. The default mode is direct; legacy modes are opt-in through `MACSTUDIO_TEST_MODES`.

Expected output includes:

```text
direct probe passed
direct tool call + tool-result continuation passed WINDOWS_MAC_BRIDGE_OK
```

If a different model ignores forced tool selection, emits malformed arguments, or fails continuation, do not call that deployment agent-ready merely because plain chat works. Inspect its serving template and supported parameters.

### 12.3 Test the actual VS Code host

**Create `test/host.js`:**

```javascript
const vscode = require('vscode');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
exports.run = async function () {
  const extension = vscode.extensions.getExtension('workshop-example.macstudio-assistant');
  assert.ok(extension);
  const assistant = await extension.activate();
  assert.ok(assistant);
  assert.ok(process.env.MACSTUDIO_API_KEY, 'Set MACSTUDIO_API_KEY for direct API host test');
  await assistant.context.secrets.store('macstudio.apiKey', process.env.MACSTUDIO_API_KEY);
  await vscode.workspace.getConfiguration('macstudio').update('mode', 'direct', vscode.ConfigurationTarget.Global);
  const connection = await assistant.connect();
  assert.ok(connection.models.includes('YOUR_MODEL_ID'));
  await vscode.commands.executeCommand('macstudio.open');
  const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
  const read = await assistant.executeTool('local_read_file', { path: 'fixture.txt' });
  assert.match(read.content, /original/);
  const proposed = await assistant.executeTool('local_propose_edit', { path: 'fixture.txt', old_text: 'original', new_text: 'reviewed', summary: 'Fixture change' });
  assert.match(await fs.readFile(path.join(root, 'fixture.txt'), 'utf8'), /original/);
  await assistant.preview(proposed.id);
  await assistant.apply(proposed.id);
  assert.match(await fs.readFile(path.join(root, 'fixture.txt'), 'utf8'), /reviewed/);
  const stale = await assistant.executeTool('local_propose_edit', { path: 'fixture.txt', old_text: 'reviewed', new_text: 'should-not-apply', summary: 'Stale fixture' });
  const document = await vscode.workspace.openTextDocument(vscode.Uri.file(path.join(root, 'fixture.txt')));
  const edit = new vscode.WorkspaceEdit(); edit.insert(document.uri, new vscode.Position(0, 0), 'user edit\n'); await vscode.workspace.applyEdit(edit);
  await assert.rejects(assistant.apply(stale.id), /changed/);
  assert.ok(!document.getText().includes('should-not-apply'));
  await document.save();
  const created = await assistant.executeTool('local_propose_edit', { path: 'new-fixture.txt', old_text: '', new_text: 'created only after review', summary: 'Create fixture' });
  await assistant.apply(created.id);
  assert.equal(await fs.readFile(path.join(root, 'new-fixture.txt'), 'utf8'), 'created only after review');
  await assert.rejects(assistant.executeTool('local_read_file', { path: '../escape.txt' }));
  for (let i = 0; i < 50 && !assistant.webviewReady; i++) await new Promise(resolve => setTimeout(resolve, 100));
  assert.equal(assistant.webviewReady, true, 'Webview script should load and post ready');
  await assistant.newChat();
  const agentFile = path.join(root, 'agent-fixture.js');
  const original = 'export function add(a, b) { return a - b; }\n';
  await fs.writeFile(agentFile, original);
  await assistant.send('Integration test. Use only local_read_file and local_propose_edit on the client file agent-fixture.js. Read it, replace subtraction with addition in add(), and propose the edit for review. Do not run commands, send external messages, or access Mac files. Briefly explain when finished.');
  assert.equal(await fs.readFile(agentFile, 'utf8'), original, 'Model may only propose before review');
  const change = [...assistant.pending.values()].find(x => x.relative === 'agent-fixture.js');
  assert.ok(change, 'Direct model should request a local edit proposal');
  assert.match(change.updated, /a\s*\+\s*b/);
  await assistant.apply(change.id);
  assert.match(await fs.readFile(agentFile, 'utf8'), /a\s*\+\s*b/);
  await fs.writeFile(path.resolve(__dirname, '../test-results/host.json'), JSON.stringify({ activated: true, webviewReady: true, viewOpened: true, diffOpened: true, applied: true, staleEditBlocked: true, createFile: true, traversalBlocked: true, liveDirectEditFlow: true }, null, 2));
  await assistant.context.secrets.delete('macstudio.apiKey');
  console.log('PASS: extension activation, webview, actual diff/apply, stale-edit guard, new file, path restrictions, live direct read/propose/apply');
};
```

**Create `test/run-host.js`:**

```javascript
const { downloadAndUnzipVSCode } = require('@vscode/test-electron');
const fs = require('node:fs/promises');
const { spawn } = require('node:child_process');
const path = require('node:path');
async function main() {
  const workspace = path.resolve(__dirname, '../test-results/workspace');
  await fs.mkdir(workspace, { recursive: true });
  await fs.rm(path.join(workspace, 'new-fixture.txt'), { force: true });
  await fs.writeFile(path.join(workspace, 'fixture.txt'), 'first\noriginal\nlast\n');
  const executable = process.env.VSCODE_EXECUTABLE || await downloadAndUnzipVSCode('stable');
  const log = await fs.open(path.resolve(__dirname, '../test-results/host-run.log'), 'w');
  await new Promise((resolve, reject) => {
    // Pass argument boundaries directly: the workspace path contains spaces.
    const child = spawn(executable, [workspace, '--disable-extensions', '--disable-updates', '--skip-welcome', '--skip-release-notes', '--disable-workspace-trust', '--user-data-dir', path.resolve(__dirname, '../test-results/vscode-profile'), '--extensions-dir', path.resolve(__dirname, '../test-results/extensions'), '--extensionDevelopmentPath=' + path.resolve(__dirname, '..'), '--extensionTestsPath=' + path.resolve(__dirname, 'host.js')], { windowsHide: true, stdio: ['ignore', log.fd, log.fd] });
    child.on('error', reject);
    child.on('close', code => code === 0 ? resolve() : reject(new Error('Extension host test failed (' + code + '); see test-results/host-run.log')));
  });
  await log.close();
  console.log('VS Code extension host tests passed.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
```

The runner launches an isolated VS Code profile and a fixture workspace. It tests extension activation, Webview readiness, diffs, approved application, stale-change rejection, new-file creation, and a real model-generated read/propose/apply flow. Automated `apply()` calls here stand in for the human click; they do not exercise a person reading the diff or accepting a shell-command dialog.

Set `MACSTUDIO_API_KEY` in the terminal as before. If you already have VS Code installed at the usual user location, run:

```powershell
$env:VSCODE_EXECUTABLE = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
Test-Path $env:VSCODE_EXECUTABLE
npm.cmd run test:host
```

If the path check returns `False`, set your actual executable path. If you omit the variable, the runner uses the VS Code test package to obtain a test build, which requires a network download.

The runner intentionally disables workspace trust for its isolated, generated fixture. Do not transfer that flag to your everyday workflow. It also creates a test profile with temporary SecretStorage data; the success path deletes the key entry. A failed run can leave the test profile on disk. Inspect and remove the specific generated profile if you need to clean it up; never delete your real VS Code user profile.

Inspect `test-results/host.json`, `test-results/live.json`, and `test-results/host-run.log`. Remove test environment variables when finished:

```powershell
Remove-Item Env:MACSTUDIO_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:VSCODE_EXECUTABLE -ErrorAction SilentlyContinue
Remove-Variable courseSecret -ErrorAction SilentlyContinue
```

### 12.4 Keep the limits visible

| Guard in this reference | Meaning |
|---|---|
| 12 model rounds by default | A turn cannot run indefinitely through tools |
| 4,096 output tokens by default | Not the same as context capacity |
| 240,000 serialized history characters | A coarse application check, not token counting |
| 400 listed files / 30 search matches | Search can be incomplete |
| 160,000-byte disk-read limit | Large files need a smaller selection or another tool |
| 60-second command timer | Commands may time out before they finish |
| Last 24,000 command-output characters | Earlier output can be truncated |

The history check occurs at the start of a turn; tool results can add more text during that turn. A production token budgeter should reserve room before every model call. A server advertising 262K context does not mean this application safely fills that window. Do not describe the character guard as a tokenizer.

**Checkpoint:** Record which tests ran, which service/model they used, and which behaviors remain manual or untested.

```{admonition} Lab acceptance evidence
:class: important
Submit a before/after diff, a passing test, and evidence that stale changes and rejected commands are handled correctly.
```

> **Image Suggestion (Nanobanana Prompt)**: Create a clean educational illustration for “Capstone: Fix, Review, and Verify”, using a neutral VS Code-inspired desktop palette, legible monospace labels, a Windows workstation and a Mac Studio where relevant, and clearly marked “Illustration” text. Emphasize the lab's actual control or execution boundary. Include no real credentials, personal paths, or fabricated test results. Use even lighting and a flat technical-documentation style rather than decorative effects.

**Continue:** [Previous](05-controller-and-interface.md) · [Next](07-package-and-models.md) · [Workshop guide](index.md)

## Read More

- [VS Code extension tutorial](https://code.visualstudio.com/api/get-started/your-first-extension) — Extension activation and debugging.
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview) — UI messages, resources, and content security.
- [Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust) — Trust boundaries for extension authors.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) — Hosts, clients, servers, and capability discovery.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills) — Optional server-side instruction packages.

## Knowledge Quiz

**1. What proves the bug is fixed?**

<details>
<summary>Answer</summary>

An applied change and an actual passing test, not the model saying it is fixed.

</details>

**2. What does the live protocol test not prove?**

<details>
<summary>Answer</summary>

Its synthetic tool result does not prove actual filesystem access or UI behavior.

</details>

**3. Is a 240,000-character history check a token budget?**

<details>
<summary>Answer</summary>

No. Characters and tokens differ, and tool results can grow the history during the turn.

</details>
