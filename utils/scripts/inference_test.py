import os
from smolagents import InferenceClientModel, LiteLLMModel, ToolCallingAgent, MCPClient, CodeAgent
from huggingface_hub import InferenceClient

# Create the Nebius-backed HuggingFace InferenceClient
# hf_client = InferenceClient(
#     provider="nebius",
#     api_key=os.getenv("NEBIUS_API_KEY")
# )

# Wrap it for smolagents agentic interface
model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-VL-72B-Instruct",
    provider="nebius",
    api_key=os.getenv("NEBIUS_API_KEY")
)

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me an easy ice cream recipe."},
]

# completion = client.chat.completions.create(
#     model="Qwen/Qwen2.5-VL-72B-Instruct",  
#     messages=messages, 
#     max_tokens=500
# )

# print(completion.choices[0].message.content)

# Example: No tools, just agentic reasoning (tool use can be added if desired)
agent = ToolCallingAgent(model=model, tools=[])

response = agent.run(messages[-1]['content'], max_steps=10)
print(response)