import os
import boto3
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
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
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    itinerary: str
    city: str
    user_message: str

# Initialize the Bedrock Runtime client with AWS credentials
bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)
model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
provider_id = "anthropic"

llm = ChatBedrockConverse(
    model_id=model_id,
    region_name="us-east-1",
    provider=provider_id,
    temperature=0,
    max_tokens=None,
    client=bedrock_client,
)

itinerary_prompt = """You are a helpful travel assistant. Create a day trip itinerary for {city} based on the user's interests. 
    Follow these instructions:
    1. Use the below chat conversation and the latest input from Human to get the user interests.
    2. Always account for travel time and meal times - if its not possible to do everything, then say so.
    3. If the user hasn't stated a time of year or season, assume summer season in {city} and state this assumption in your response.
    4. If the user hasn't stated a travel budget, assume a reasonable dollar amount and state this assumption in your response.
    5. Provide a brief, bulleted itinerary in chronological order with specific hours of day.
"""
itinerary_prompt_template = ChatPromptTemplate.from_messages(
    [
     "system", itinerary_prompt,
     "human", MessagesPlaceholder(variable_name="messages"),
     "human", "{user_message}"
     ])

# test = llm.invoke("Create a day trip itinerary for New York City. I am interested in art, history, and food. I am visiting in the summer and have a budget of $100.")
# print(test.content)

def input_interests(state: State) -> State:
    # user_message is already provided via the initial state; nothing to do here.
    return state

def create_itinerary(state: State) -> State:
    existing_messages = state.get("messages", [])
    prompt = itinerary_prompt_template.format_prompt(
        messages=existing_messages,
        user_message=state["user_message"],
        city=state["city"]
    )
    response = llm.invoke(prompt.to_messages())
    state["itinerary"] = response.content
    # Append this turn's human/AI messages so future turns retain context.
    state["messages"] = [
        HumanMessage(content=state["user_message"]),
        AIMessage(content=response.content),
    ]
    return state

# Create the Graph and define the workflow
workflow = StateGraph(State)
workflow.add_node("input_interests", input_interests)
workflow.add_node("create_itinerary", create_itinerary)
workflow.set_entry_point("input_interests")

workflow.add_edge("input_interests", "create_itinerary")
workflow.add_edge("create_itinerary", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )
)

#********************************************************
# Running the worflow
def run_travel_planner(user_request: str, config_dict: dict):
    print(f"Current user request: {user_request}")
    # Note: "messages" is intentionally omitted so the checkpointer's existing
    # history (keyed by thread_id) is preserved across turns instead of being reset.
    init_input = {"user_message": user_request, "city": "Maryland"}

    final_state = None
    for output in app.stream(init_input, config=config_dict, stream_mode="values"):
        final_state = output

    print("\n--- Itinerary ---\n")
    print(final_state["itinerary"])

config = {"configurable": {"thread_id": "1"}}
user_request = "Can you create a itinerary for a day trip in Maryland with boating and swimming options. Need a complete plan"
run_travel_planner(user_request, config)
#********************************************************
config = {"configurable": {"thread_id": "1"}}
user_request = "Can you add white water rafting to this itinerary"
run_travel_planner(user_request, config)
#********************************************************
config = {"configurable": {"thread_id": "11"}}
user_request = "Can you add white water rafting to itinerary"
run_travel_planner(user_request, config)
#********************************************************



