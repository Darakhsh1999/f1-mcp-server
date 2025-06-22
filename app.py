import gradio as gr

# Local modules
import fastf1_tools
import openf1_tools
from utils.constants import (
    DRIVER_NAMES,
    CONSTRUCTOR_NAMES,
    CURRENT_YEAR,
    DROPDOWN_SESSION_TYPES,
    MARKDOWN_INTRODUCTION,
    HTML_INTRODUCTION,
    MARKDOWN_OPENF1_EXAMPLES,
    OPENF1_TOOL_DESCRIPTION,
    CONSTRUCTORS_PER_SEASON,
    DRIVERS_PER_SEASON
)

with gr.Blocks() as iface_driver_championship_standings:
    gr.Markdown("## World Driver Championship Standings\nGet the world driver championship standings for a specific driver. Note that the older data has gaps and may not be entirely complete.")

    with gr.Row():
        year_input = gr.Number(label="Calendar year", value=CURRENT_YEAR, minimum=1950, maximum=CURRENT_YEAR)
        driver_dropdown = gr.Dropdown(label="Driver", choices=DRIVERS_PER_SEASON.get(str(year_input.value), []))
    output_text = gr.Textbox(label="Result")
    submit_btn = gr.Button("Submit")

    def update_drivers(year):
        choices = DRIVERS_PER_SEASON.get(str(year), [])
        return gr.update(choices=choices, value=(choices[0] if choices else None))

    year_input.blur(
        update_drivers,
        inputs=year_input,
        outputs=driver_dropdown
    )
    submit_btn.click(
        fastf1_tools.driver_championship_standings,
        inputs=[year_input, driver_dropdown],
        outputs=output_text
    )

with gr.Blocks() as iface_constructor_championship_standings:
    gr.Markdown("## World Constructor Championship Standings\nGet the current/past world constructor championship standings for a specific constructor. Note that the older data has gaps and may not be entirely complete.")
    
    with gr.Row():
        year_input = gr.Number(label="Calendar year", value=CURRENT_YEAR, minimum=1950, maximum=CURRENT_YEAR)
        constructor_dropdown = gr.Dropdown(label="Constructor", choices=CONSTRUCTORS_PER_SEASON.get(str(year_input.value), []))
    output_text = gr.Textbox(label="Result")
    submit_btn = gr.Button("Submit")

    def update_constructors(year):
        choices = CONSTRUCTORS_PER_SEASON.get(str(year), [])
        return gr.update(choices=choices, value=(choices[0] if choices else None))

    year_input.blur(
        update_constructors,
        inputs=year_input,
        outputs=constructor_dropdown
    )
    submit_btn.click(
        fastf1_tools.constructor_championship_standings,
        inputs=[year_input, constructor_dropdown],
        outputs=output_text
    )

iface_event_info = gr.Interface(
    fn=fastf1_tools.get_event_info,
    inputs=[
        gr.Number(label="Calendar year", value=CURRENT_YEAR, minimum=1950, maximum=CURRENT_YEAR),
        gr.Textbox(label="Grand Prix", placeholder="Ex: Monaco", info="The name of the GP/country/location (Fuzzy matching supported) or round number"),
        gr.Radio(["human", "LLM"], label="Display format", value="human", info="Toggle between human-readable (parsed) and LLM output (raw)")
    ],
    outputs="text",
    title="Event Info",
    description="Get information about a specific Grand Prix event. Example: (2025,Monaco,human)"
)

iface_season_calendar = gr.Interface(
    fn=fastf1_tools.get_season_calendar,
    inputs=[
        gr.Number(label="Calendar year", value=CURRENT_YEAR, minimum=1950, maximum=CURRENT_YEAR),
    ],
    outputs="text",
    title="Season Calendar",
    description="Get the season calendar for the given year"
)

iface_track_visualization = gr.Interface(
    fn=fastf1_tools.track_visualization,
    inputs=[
        gr.Number(label="Calendar year", value=CURRENT_YEAR, minimum=1950, maximum=CURRENT_YEAR),
        gr.Textbox(label="Grand Prix", placeholder="Ex: Monaco", info="The name of the GP/country/location (Fuzzy matching supported) or round number"),
        gr.Radio(["speed", "corners", "gear"], label="Visualization type", value="speed", info="What type of track visualization to generate"),
    ],
    outputs="image",
    title="Track Visualizations",
    description="Get the track visualization (speed/corners/gear) for the fastest lap at the specific Grand Prix race. Example: (2025,Monaco,speed)"
)

iface_session_results = gr.Interface(
    fn=fastf1_tools.get_session_results,
    inputs=[
        gr.Number(label="Calendar year", value=CURRENT_YEAR, minimum=1950, maximum=CURRENT_YEAR),
        gr.Textbox(label="Grand Prix", placeholder="Ex: Monaco", info="The name of the GP/country/location (Fuzzy matching supported) or round number"),
        gr.Dropdown([session_type for session_type in DROPDOWN_SESSION_TYPES if "practice" not in session_type], label="Session type", value="race", info="The session type to get results for. Dataframe's columns vary depending on session type.")
    ],
    outputs=gr.Dataframe(
        headers=None,              # Let it infer from returned DataFrame
        row_count=(0, "dynamic"),  # Start empty, allow it to grow
        col_count=(0, "dynamic")   # Let columns adjust too
    ),
    title="Session Results",
    description="Get the session results for the given Grand Prix. Example: (2025,Monaco,qualifying)"
)

iface_driver_info = gr.Interface(
    fn=fastf1_tools.get_driver_info,
    inputs=[
        gr.Dropdown(label="Driver", choices=DRIVER_NAMES)
    ],
    outputs="text",
    title="Driver Info",
    description="Get background information about a specific driver from the 2025 Formula 1 season"
)

iface_constructor_info = gr.Interface(
    fn=fastf1_tools.get_constructor_info,
    inputs=[
        gr.Dropdown(label="Constructor", choices=CONSTRUCTOR_NAMES)
    ],
    outputs="text",
    title="Constructor Info",
    description="Get background information about a specific constructor from the 2025 Formula 1 season"
)


# About introduction tab
with gr.Blocks() as markdown_tab:
    gr.HTML(HTML_INTRODUCTION)


# OpenF1 tools tab
def openf1_tools_tab():
    with gr.Blocks() as openf1_tools_tab:
        gr.Markdown(OPENF1_TOOL_DESCRIPTION)
        with gr.Accordion("get_api_endpoints()", open=False):
            btn = gr.Button("Get all endpoints")
            output = gr.JSON()
            btn.click(openf1_tools.get_api_endpoints, outputs=output)
        with gr.Accordion("get_api_endpoint(endpoint)", open=False):
            endpoint_in = gr.Textbox(label="Endpoint", placeholder="e.g. sessions")
            btn = gr.Button("Get endpoint info")
            output = gr.JSON()
            btn.click(openf1_tools.get_api_endpoint, inputs=endpoint_in, outputs=output)
        with gr.Accordion("get_endpoint_info(endpoint)", open=False):
            endpoint_in = gr.Textbox(label="Endpoint", placeholder="e.g. sessions")
            btn = gr.Button("Get endpoint details")
            output = gr.JSON()
            btn.click(openf1_tools.get_endpoint_info, inputs=endpoint_in, outputs=output)
        with gr.Accordion("get_filter_info(filter_name)", open=False):
            filter_in = gr.Textbox(label="Filter name", placeholder="e.g. driver_number")
            btn = gr.Button("Get filter info")
            output = gr.JSON()
            btn.click(openf1_tools.get_filter_info, inputs=filter_in, outputs=output)
        with gr.Accordion("get_filter_string(filter_name, filter_value, operator)", open=False):
            filter_name = gr.Textbox(label="Filter name", placeholder="e.g. driver_number")
            filter_value = gr.Textbox(label="Filter value", placeholder="e.g. 16")
            operator = gr.Dropdown(label="Operator", choices=["=", ">", "<", ">=", "<="], value="=")
            btn = gr.Button("Get filter string")
            output = gr.Textbox(label="Filter string", info="Example: driver_number=16&")
            btn.click(openf1_tools.get_filter_string, inputs=[filter_name, filter_value, operator], outputs=output)
        with gr.Accordion("apply_filters(api_string, *filters)", open=False):
            api_string = gr.Textbox(label="Base API string", placeholder="e.g. https://api.openf1.org/v1/sessions?")
            filters = gr.Textbox(label="Filters (comma-separated)", placeholder="e.g. driver_number=16&,session_key=123&")
            btn = gr.Button("Apply filters")
            output = gr.Textbox(label="Full API string")
            btn.click(openf1_tools.apply_filters, inputs=[api_string, filters], outputs=output)
        with gr.Accordion("send_request(api_string)", open=False):
            with gr.Accordion("Example API requests (copy & paste into text box below)", open=False):
                gr.Markdown(MARKDOWN_OPENF1_EXAMPLES)
            api_string = gr.Textbox(label="Full API string", placeholder="e.g. https://api.openf1.org/v1/sessions?driver_number=16")
            btn = gr.Button("Send API request")
            output = gr.JSON()
            btn.click(openf1_tools.send_request, inputs=api_string, outputs=output)
    return openf1_tools_tab

# OpenF1 tabs

named_interfaces = {
    "About": markdown_tab,
    "Driver Championship Standings": iface_driver_championship_standings,
    "Constructor Championship Standings": iface_constructor_championship_standings,
    "Event Info": iface_event_info,
    "Season Calendar": iface_season_calendar,
    "Track Visualizations": iface_track_visualization,
    "Session Results": iface_session_results,
    "Driver Info": iface_driver_info,
    "Constructor Info": iface_constructor_info,
    "OpenF1 Tools": openf1_tools_tab()
}

# Tab names and interfaces
tab_names = list(named_interfaces.keys())
interface_list = list(named_interfaces.values())


# Combine all the interfaces into a single TabbedInterface
gradio_server = gr.TabbedInterface(
    interface_list,
    tab_names=tab_names,
    title="🏁 Formula 1 MCP server 🏎️"
)

# Launch the interface and MCP server
if __name__ == "__main__":
    gradio_server.launch(mcp_server=True)