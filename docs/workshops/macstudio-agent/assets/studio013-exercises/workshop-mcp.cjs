// Run from the extracted kit after npm ci in source/. No model or credentials.
'use strict';
const http = require('node:http');
const path = require('node:path');
const {createRequire} = require('node:module');
const fromSource = createRequire(path.join(__dirname, '../source/package.json'));
const {Server} = fromSource('@modelcontextprotocol/sdk/server/index.js');
const {StreamableHTTPServerTransport} = fromSource('@modelcontextprotocol/sdk/server/streamableHttp.js');
const {ListToolsRequestSchema, CallToolRequestSchema} = fromSource('@modelcontextprotocol/sdk/types.js');
const server = http.createServer(async (req, res) => {
  if (req.url !== '/mcp' || req.method !== 'POST') {
    res.writeHead(405); res.end(); return;
  }
  let raw = '';
  try {
    for await (const chunk of req) {
      raw += chunk;
      if (Buffer.byteLength(raw) > 16000) { res.writeHead(413); res.end(); return; }
    }
    const transport = new StreamableHTTPServerTransport({sessionIdGenerator: undefined});
    const mcp = new Server({name:'workshop-notes',version:'1.0.0'},{capabilities:{tools:{}}});
    mcp.setRequestHandler(ListToolsRequestSchema, () => ({tools:[{
      name:'workshop_note', description:'Read a fixed, non-private workshop note.',
      inputSchema:{type:'object',properties:{},additionalProperties:false},
      annotations:{readOnlyHint:true,destructiveHint:false}
    }]}));
    mcp.setRequestHandler(CallToolRequestSchema, request => {
      if (request.params.name !== 'workshop_note') throw Error('Unknown workshop tool');
      return {content:[{type:'text',text:'WORKSHOP-MCP-READ-OK: Review changes and verify actual test output.'}]};
    });
    res.on('close', () => mcp.close().catch(() => {}));
    await mcp.connect(transport);
    await transport.handleRequest(req, res, JSON.parse(raw));
  } catch {
    if (!res.headersSent) res.writeHead(400, {'Content-Type':'application/json'});
    if (!res.writableEnded) res.end(JSON.stringify({error:'Invalid workshop request'}));
  }
});
server.listen(18790, '127.0.0.1', () => console.log('Workshop MCP: http://127.0.0.1:18790/mcp'));
