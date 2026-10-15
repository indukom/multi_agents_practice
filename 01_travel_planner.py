import os
import boto3
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_aws import ChatBedrock
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# Agent State
class State(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "The message in the conversation"]
    itinerary: str
    city: str
    user_message: str

# Initialize the Bedrock Runtime client with AWS credentials
bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)
model_id = "us.anthropic.claude-opus-4-1-20250805-v1:0"
provider_id = "anthropic"

llm = ChatBedrockConverse(
    model_id=model_id,
    region_name="us-east-1",
    provider=provider_id,
    temperature=0,
    max_tokens=None,
    client=bedrock_client,
)

print("LLM initialized successfully!")
print(f"Model: {model_id}")
print(f"Region: us-east-1")
print(f"Provider: {provider_id}")
print("\n✓ Bedrock connection setup complete")
print("\nTo invoke the model, use:")
print("  response = llm.invoke('Your question here')")

test = llm.invoke("How are you")
print(test)

