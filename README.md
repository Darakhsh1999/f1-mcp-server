---
title: F1 MCP Server
emoji: 🏎️
colorFrom: red
colorTo: gray
sdk: gradio
sdk_version: 5.32.0
app_file: app.py
pinned: true
license: apache-2.0
short_description: 'Universal F1 data retrieval and agentic race strategy.'
video_url: https://www.loom.com/share/bfa4e3e5d70d47f9bce406a0714893fd?sid=634b543c-684e-4872-b926-14cbb56396de
tags:
  - 'mcp-server-track'
  - 'agent-demo-track'
---


## MCP Server
The MCP server is defined inside `app.py` and is hosted on HuggingFace spaces using the Gradio template.

## MCP Client
The MCP client and AI agent is defined inside `mcp_client.py` and allows interaction with the MCP server through server side events (SSE) transport.


## MCP configuration file
For MCP clients that support SSE transport (for Claude Desktop, see below), the following configuration can be used:

```json
{
  "mcpServers": {
    "gradio": {
      "url": "https://agents-mcp-hackathon-f1-mcp-server.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

For Claude Desktop, the following configuration can instead be used, but make sure you have Node.js installed:

```json
{
  "mcpServers": {
    "gradio": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://agents-mcp-hackathon-f1-mcp-server.hf.space/gradio_api/mcp/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}
```

