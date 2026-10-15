import os
import boto3
from typing import TypedDict, Annotated, List
from langgraph import graph
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_aws import ChatBedrock
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

# 1. Define the Agent State
class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]

# 2. Define the agent function that uses the Bedrock model to respond to user messages
def chatbot(state: AgentState) -> AgentState:
    llm = ChatBedrockConverse(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name="us-east-1",
        provider="anthropic",
        temperature=0
    )

    llm_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Answer the user's questions based on the conversation history."),
        ])

    messages = llm_prompt.format_messages() + state["messages"]
    result = llm.invoke(messages)

    return {
        "messages": [result]
    }

# 3. Define the workflow
workflow = StateGraph(AgentState)

workflow.add_node("llmchatbot", chatbot)
workflow.add_edge(START, "llmchatbot")
workflow.add_edge("llmchatbot", END)

graph = workflow.compile()

# 4. Invoke the workflow with a sample user message
response = graph.invoke({"messages": [HumanMessage(content="Hello! Can you help me plan a day trip in Maryland?")]})
print(response["messages"][-1].content)

# 5. Stream the data from the graph
for event in graph.stream({"messages": [HumanMessage(content="Hi, How are you?")]}):
    for value in event.values():
        print(value["messages"][-1].content)

# 6. Visualize the graph
from IPython.display import Image,display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    pass



