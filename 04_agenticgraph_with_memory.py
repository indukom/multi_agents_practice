from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph,START,END, add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, List
import os

load_dotenv()

memory = MemorySaver()

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

# 4. Create the node that calls the LLM with tools and saves the state to memory
def tool_calling_llm(state: AgentState) -> AgentState:
    return {
        "messages": [llm_with_tools.invoke(state["messages"])]
    }

# 5. Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("llm_with_tools", tool_calling_llm)
workflow.add_node("tools", ToolNode(tools))

# add edges to the graph
workflow.add_edge(START, "llm_with_tools")
workflow.add_conditional_edges("llm_with_tools", tools_condition, {"tools": "tools", "__end__": END})
workflow.add_edge("tools", "llm_with_tools")

# Compile the graph
graph = workflow.compile(checkpointer=memory)

# 6. Query and response
config = {"configurable": {"thread_id": "1"}}
query = "Give me the recent ai news and then multiply 5 by 10"
response = graph.invoke({"messages": [HumanMessage(content=query)]}, config=config)
print(response["messages"][-1].content)

# 7. Visualize the graph
import subprocess
png_data = graph.get_graph().draw_mermaid_png()
with open('agent_graph.png', 'wb') as f:
    f.write(png_data)
process = subprocess.Popen(['open', 'agent_graph.png'])
process.wait()
os.remove('agent_graph.png')
print("Graph closed and cleaned up")




