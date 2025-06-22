import json
import datetime

# Architecture image
IMAGE_BASE64: str = json.load(open("assets/image_base64.json"))['image_base64']

# Variables
CURRENT_YEAR = datetime.datetime.now().year

AVAILABLE_SESSION_TYPES = [
    "fp1", "fp2", "fp3", "q", "s", "ss", "sq", "r",
    "practice 1", "practice 2", "practice 3", "sprint",
    "sprint qualifying", "qualifying", "race"
    ]

DROPDOWN_SESSION_TYPES = [
    "practice 1", "practice 2", "practice 3", "sprint",
    "sprint qualifying", "qualifying", "race"
    ]

# Load in driver names
DRIVER_NAMES: list[str] = json.load(open("assets/driver_names.json"))["drivers"]

# Load in constructor team names
CONSTRUCTOR_NAMES: list[str] = json.load(open("assets/constructors.json"))["constructors"]

# Load in driver details
DRIVER_DETAILS: dict[str, dict[str, str]] = json.load(open("assets/driver_details.json"))

# Load in constructor details
CONSTRUCTOR_DETAILS: dict[str, dict[str, str]] = json.load(open("assets/constructor_details.json"))

# Load in constructor per season
CONSTRUCTORS_PER_SEASON: dict[int, list[str]] = json.load(open("assets/constructors_per_season.json"))

# Load in driver per season
DRIVERS_PER_SEASON: dict[int, list[str]] = json.load(open("assets/drivers_per_season.json"))

OPENF1_TOOL_DESCRIPTION = """
## OpenF1 Tools - API Endpoints.

This UI Interface/Tab collects all the MCP tools that are based on the `OpenF1` API, which are a bit less user friendly compared to the tools in the other tabs, which are implemented using the `FastF1` library.
In essence, the tools listed below make it possible to access the `OpenF1` API directly within the MCP server, thus allowing a LLM to interact with the `OpenF1` API using natural language.
The API exposes several **_endpoints_** that can be used to access different types of real-time and historical data about Formula 1 races, sessions, drivers, and constructor teams.
Each of these endpoints have different **_filters_** that can be used to specify the data returned from the endpoint. The data communication is entirely in JSON format making it optimized for the LLM.

The implemented functions make it possible to:
- Get all available endpoints - `get_api_endpoints()`
- Get api string for a specific endpoint - `get_api_endpoint(endpoint)`
- Get details about a specific endpoint - `get_endpoint_info(endpoint)`
- Get information about a specific filter - `get_filter_info(filter_name)`
- Get a filter string for a specific filter - `get_filter_string(filter_name, filter_value, operator)`
- Apply filters to an API string - `apply_filters(api_string, *filters)`
- Send a request to the OpenF1 API - `send_request(api_string)`

The inputs are strings while the output is a JSON object. The examples are listed in an order that would be expected to be used in a real-life scenario. Some example API strings are listed below in the final tool `send_request(api_string)`.

"""


MARKDOWN_OPENF1_EXAMPLES = """

Retrieve data about car number 55 with session_key 9159 where the speed was greater than 315 <br>
```https://api.openf1.org/v1/car_data?driver_number=55&session_key=9159&speed>=315```

Retrieve data about driver number 1 with session_key 9158 <br>
```https://api.openf1.org/v1/drivers?driver_number=1&session_key=9158```

Retrieve data about intervals with session_key 9165 where the interval was less than 0.005s <br>
```https://api.openf1.org/v1/intervals?session_key=9165&interval<0.005```

Retrieve data about laps with session_key 9161 for driver number 63 on lap number 8 <br>
```https://api.openf1.org/v1/laps?session_key=9161&driver_number=63&lap_number=8```

Retrieve data about meetings in 2023 for Singapore <br>
```https://api.openf1.org/v1/meetings?year=2023&country_name=Singapore```

Retrieve data about pit stops with session_key 9158 where the pit duration was less than 31s <br>
```https://api.openf1.org/v1/pit?session_key=9158&pit_duration<31```

"""



MARKDOWN_INTRODUCTION = f"""
# 🏁 Formula 1 MCP server 🏎️

Welcome to the Formula 1 MCP server, your one-stop destination for Formula 1 data retrieval and race real-time race strategy analysis.
<br>
This application leverages the FastF1 library and OpenF1 API to provide detailed insights into Formula 1 races, drivers, and teams.

## Video Demonstration & Submissions

### Short demo (Claude Desktop)
Minimalistic demo of the MCP server using Claude Desktop.
<!-- <iframe src="https://www.loom.com/embed/4e0a5dbf7b8e4c428a7e2a8a8a8edc3b" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe> -->

### Longer demo and yap sesh (Gradio UI + mcp_client.py + Claude Desktop)
More in-depth demo of interacting with the MCP server using Gradio UI, mcp_client.py and Claude Desktop.
<!-- <iframe src="https://www.loom.com/embed/4e0a5dbf7b8e4c428a7e2a8a8a8edc3b" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe> -->

## Architecture (Created with Excalidraw and icons from Lobehub)

<img src="data:image/png;base64,{IMAGE_BASE64}" width="800" />


## Available Tools in Gradio UI

### Championship Standings
- **Driver Standings**: Retrieve live or past driver championship standings for a specific driver
- **Constructor Standings**: Retrieve live or past constructor championship standings for a specific constructor

### Race Information
- **Event Info**: Get detailed information about a specific Grand Prix event
- **Season Calendar**: View the complete race calendar for any season
- **Session Results**: Access race, qualifying, and sprint session results

### Driver & Team Data
- **Driver Info**: Retrieve detailed driver information from the 2025 Formula 1 season
- **Constructor Info**: Retrieve detailed constructor information from the 2025 Formula 1 season
- **Track Visualizations**: Explore interactive track maps with speed, gear, and corner visualizations

### OpenF1 Tools
- **OpenF1 Tools**: Access the OpenF1 API directly within the MCP server, allowing a LLM to interact with the API using natural language.

## Usage

There are different ways to interact with the MCP server:

1) (recommended) Add the MCP server to your `mcp.json` file. This is the most user-friendly way to interact with the MCP server. See the section below for the MCP config file.

2) (Good for demo) One can also use the Gradio interface directly to interact with the MCP server's tools. Note, however, the UI for the OpenF1 tools is purely limted to strings and JSON. 

3) (Advanced) One can establish an MCP client by running `mcp_client.py`. This client is connected to the MCP server hosted on HuggingFace spaces.
""" + """

## MCP json configuration file

For MCP clients that support SSE transport (For Claude desktop see below), the following configuration can be used in your `mcp.json` file (or its equivalent):

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
"""


HTML_INTRODUCTION = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Formula 1 MCP Server</title>
</head>
<body>
    <h1>Formula 1 MCP Server</h1>
    <p>Welcome to the Formula 1 MCP server, your one-stop destination for Formula 1 data retrieval and race real-time race strategy analysis.</p>
    <p>This application leverages the FastF1 library and OpenF1 API to provide detailed insights into Formula 1 races, drivers, and teams.</p>

    <h2>Quick demo (Claude Desktop)</h2>
    <p>Quick demo of the MCP server using Claude Desktop.</p>
    <iframe width="640" height="399" src="https://www.loom.com/embed/4ef9cf2e691143db8e5d807a1aef9672?sid=2acf26b1-49a0-4157-ac6b-3fdf08be8ea2" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

    <h2>Longer demo and yap sesh (Gradio UI / mcp_client.py / Claude Desktop)</h2>
    <p>More in-depth demo of interacting with the MCP server using Gradio UI, mcp_client.py and Claude Desktop. Swedish accent warning, watch on 1.5x to stay sane</p>
    <iframe width="640" height="399" src="https://www.loom.com/embed/bfa4e3e5d70d47f9bce406a0714893fd?sid=63dfe49d-09db-4242-ac86-ec4ba9cfec34" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

    <h2>Architecture (Created with Excalidraw and icons from Lobehub)</h2>
    <img src="data:image/png;base64,{IMAGE_BASE64}" width="640" />

    <h2>Available Tools in Gradio UI</h2>
    <h3>Championship Standings</h3>
    <ul>
        <li>Driver Standings: Retrieve live or past driver championship standings for a specific driver</li>
        <li>Constructor Standings: Retrieve live or past constructor championship standings for a specific constructor</li>
    </ul>

    <h3>Race Information</h3>
    <ul>
        <li>Event Info: Get detailed information about a specific Grand Prix event</li>
        <li>Season Calendar: View the complete race calendar for any season</li>
        <li>Session Results: Access race, qualifying, and sprint session results</li>
    </ul>

    <h3>Driver & Team Data</h3>
    <ul>
        <li>Driver Info: Retrieve detailed driver information from the 2025 Formula 1 season</li>
        <li>Constructor Info: Retrieve detailed constructor information from the 2025 Formula 1 season</li>
        <li>Track Visualizations: Explore interactive track maps with speed, gear, and corner visualizations</li>
    </ul>

    <h3>OpenF1 Tools</h3>
    <ul>
        <li>OpenF1 Tools: Access the OpenF1 API directly within the MCP server, allowing a LLM to interact with the API using natural language.</li>
    </ul>
""" + """
    <h2>Acknowledgements</h2>
    <p>Many thanks to Hugging Face, especially to the Gradio team for setting up this exciting Hackaton. Thanks to the external providers for their models and API credits.</p>

    <h2>MCP json configuration file</h2>
    <p>For MCP clients that support SSE transport (For Claude desktop see below), the following configuration can be used in your <code>mcp.json</code> file (or its equivalent):</p>
    <pre><code>
{
  "mcpServers": {
    "gradio": {
      "url": "https://agents-mcp-hackathon-f1-mcp-server.hf.space/gradio_api/mcp/sse"
    }
  }
}
    </code></pre>

    <p>For Claude Desktop, the following configuration can instead be used, but make sure you have Node.js installed:</p>
    <pre><code>
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
    </code></pre>

    </body>
    </html>

"""
    
    