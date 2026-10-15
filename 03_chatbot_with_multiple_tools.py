from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph,START,END, add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import os
from typing import TypedDict, Annotated, List

load_dotenv()

# Define tools
# Tool 1: Tavily Search Tool
search_tool = TavilySearch(
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5)

# Tool 2: Multiply Tool
@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b"""
    return a * b

# 2. Define the LLM with tools
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-east-1",
    provider="anthropic",
    temperature=0
)

tools = [search_tool, multiply]
llm_with_tools = llm.bind_tools(tools)

# 3. Define the Agent State
class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]

# 4. Define the agent function that uses the Bedrock model with tools to respond to user messages
def tool_calling_llm(state: AgentState) -> AgentState:
    return {
        "messages": state["messages"] + [llm_with_tools.invoke(state["messages"])]
    }

# 5. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("llm_with_tools", tool_calling_llm)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "llm_with_tools")
workflow.add_conditional_edges("llm_with_tools", tools_condition, {"tools": "tools", "__end__": END})
workflow.add_edge("tools", "llm_with_tools")

graph = workflow.compile()

# Visualize the graph
import subprocess
import os
png_data = graph.get_graph().draw_mermaid_png()
with open('agent_graph.png', 'wb') as f:
    f.write(png_data)
process = subprocess.Popen(['open', 'agent_graph.png'])
process.wait()
os.remove('agent_graph.png')
print("Graph closed and cleaned up")

# 6. Query and response
query = "Give me the recent ai news and then multiply 5 by 10"
response = graph.invoke({"messages": [HumanMessage(content=query)]})
print(response["messages"][-1].content)

