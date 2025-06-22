import os
import datetime
import gradio as gr
import openf1_tools
from smolagents import InferenceClientModel, LiteLLMModel, ToolCallingAgent, MCPClient
from dotenv import load_dotenv



import logging
logging.basicConfig(
    filename="agent.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Can manully set this to a specific time to make the agent think it is in the past
time = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
spanish_gp_race_plus1h = "2025-06-01T13:45:00Z" # Race start +45 minutes

SYSTEM_PROMPT = f"""You are a helpful Formula 1 assistant and strategist. You have access to various F1 data and tools to help answer questions about races, drivers, teams, and more. Be concise and accurate in your responses. You must use the available tools to find the information.
In addition, you will be asked to act as a live race engineer strategist during a Formula 1 race, making crucial calls during the event.
For formula 1 related tasks, start by calling get_api_endpoints() to see all available endpoints and use them to access the OpenF1 API.
Then retrieve information about a specific endpoint, using get_endpoint_info(endpoint), to make sure it does what you want it to do.
If you are unsure what a filter does, get its description using get_filter_info(filter_name).
Lastly, combine the endpoint and filters to create a request to the OpenF1 API and call send_request() to send the request.

Current UTC time (ISO 8601): {spanish_gp_race_plus1h}"""


def agent_chat(message: str, history: list):
    logger.info(f"Running agent with user message: {message}")
    message = f"{SYSTEM_PROMPT}\n\nTask: {message}"
    return agent.run(message, max_steps=80)


if __name__ == "__main__":

    list_tools = False # Set to True to only list tools (used for debugging)
    local_model = False # If you have Ollama installed, set this to True
    openf1_tool_only = True
    provider = "sambanova" # "nebius" (mistral) or "sambanova" (deepseek/llama4)
    
    try:

        # Connect to my MCP server hosted on HF spaces
        mcp_client = MCPClient(
            {"url": "https://agents-mcp-hackathon-f1-mcp-server.hf.space/gradio_api/mcp/sse", "transport": "sse"})
        logger.info("Connected to MCP server.")
        tools = mcp_client.get_tools()
        logger.info(f"Retrieved {len(tools)} tools from MCP server.")

        # Filter tools to only use the OpenF1 library
        if openf1_tool_only:
            openf1_fn_names = [f"f1_mcp_server_{fn}" for fn in dir(openf1_tools) if callable(getattr(openf1_tools, fn))]
            openf1_fn_names.remove("f1_mcp_server_urlopen")
            tools = [t for t in tools if (t.name in openf1_fn_names)]
            logger.info(f"Filtered tools to only OpenF1 tools: {len(tools)} remaining.")

        if list_tools:
            logger.info("### MCP tools ### ")
            logger.info("\n".join(f"Tool {1+i}: {t.name}: {t.description}" for i,t in enumerate(tools)))
            mcp_client.disconnect()
            exit(0)

        # Define model
        if local_model:
            model = LiteLLMModel(
                model_id="ollama_chat/qwen3:1.7b",
                api_base="http://127.0.0.1:11434", # Default ollama server
                num_ctx=32768,
            )
        else:
            # Get model ID 
            model_id_env_mapping = {
                "nebius": "deepseek-ai/DeepSeek-R1-0528",
                "sambanova": "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
            }
            model_id = model_id_env_mapping[provider]

            # Get API key from environment variable
            provider_env_mapping = {
                "nebius": "NEBIUS_API_KEY",
                "sambanova": "SAMBANOVA_API_KEY"
            }
            api_key = os.getenv(provider_env_mapping[provider])

            logger.info(f"Provider: {provider} | Model ID: {model_id}, API key: {api_key[:5]}...{api_key[-5:]}")

            model = InferenceClientModel(
                model_id=model_id,
                provider=provider,
                api_key=api_key,
                temperature=0
            )
            logger.info("InferenceClientModel initialized.")

        agent = ToolCallingAgent(model=model, tools=[*tools])
        logger.info("ToolCallingAgent initialized.")
        # invoked through agent.run("This is the task i want you to do.")

        # Launch chat interface
        chat_interface = gr.ChatInterface(
            fn=agent_chat,
            type="messages",
            examples=[
                "What is the calendar for the 2024 Formula 1 season?",
                "Who won the Monaco 2024 GP"
            ],
            title="🏎️ Formula 1 Assistant",
            description="This is a simple agent that uses MCP tools to answer questions about Formula 1."
        )

        logger.info("Launching Gradio chat interface...")
        chat_interface.launch()

    finally:
        logger.info("Disconnecting MCP client...")
        mcp_client.disconnect()