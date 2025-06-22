#  🏁 Formula 1 MCP Server 🏎️

This project defines a MCP server for Formula 1 data, providing fans, analysts, and developers with easy access to a vast range of F1 statistics and information. Built with Python and powered by the Gradio framework, it offers a user-friendly web interface to explore historical and recent F1 data from the [FastF1](https://docs.fastf1.dev/) library and the official [OpenF1 API](https://openf1.org/).

## Video Demo (Claude Desktop)

[![Demo Video](https://cdn.loom.com/sessions/thumbnails/4ef9cf2e691143db8e5d807a1aef9672-3f6299cea3ac0fd3-full-play.gif)](https://www.loom.com/embed/4ef9cf2e691143db8e5d807a1aef9672?sid=6dabbf2e-71ba-406d-ad86-8b480a29e222)

### Key Features
The interface is organized into several tabs, each dedicated to a specific type of F1 data:

*   **Championship Standings:** View final driver and constructor championship standings for any season from 1950 to the present.
*   **Event Information:** Get detailed information for any Grand Prix, including schedules and circuit details.
*   **Season Calendar:** Display the complete race calendar for a given year.
*   **Track Visualizations:** Generate and view plots of the fastest race lap, visualizing speed, gear changes, and cornering G-forces.
*   **Session Results:** Fetch detailed results for any race session (Practice, Qualifying, or Race).
*   **Driver & Constructor Info:** Look up background information and statistics for drivers and teams.
*   **OpenF1 API Tools:** An advanced toolkit for developers to directly query the OpenF1 API, build custom requests, and view raw JSON responses.

### Tech Stack
*   **Backend:** Python
*   **Web Framework:** Gradio
*   **Data Sources:**
    *   `fastf1` Python library for historical data.
    *   `openf1` for live and recent data via their public API.
*   **Key Libraries:** `pandas`, `matplotlib`


## MCP Server
The MCP server is defined inside `app.py`.

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