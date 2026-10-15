from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
import os

load_dotenv()

search_tool = TavilySearch(
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5)

llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-east-1",
    provider="anthropic",
    temperature=0
)

tools = [search_tool]
llm_with_tools = llm.bind_tools(tools)

messages = [{"role": "user", "content": "What are the top 5 tourist attractions in New York City?"}]

while True:
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_result = search_tool.invoke(tool_call["args"]["query"])

        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call["id"],
                    "content": str(tool_result)
                }
            ]
        })
    else:
        print(response.content)
        break