

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage

class CartState(TypedDict):
    request: str
    response: str
    boolen_flag: bool
    message_history: list[AnyMessage]

def understand_request(state: CartState):
    request = state["request"].lower()
    category = "support" if "order" in request else "product"
    return {"response": f"Detected category: {category}"}

builder = StateGraph(CartState)

builder.add_node("understand_request", understand_request)
builder.add_edge(START, "understand_request")
builder.add_edge("understand_request", END)

graph = builder.compile()
# result = graph.invoke({"request": "Where is my order?", "response": ""})
result = graph.invoke({"request": "I want to buy a new phone.", "response": ""})
print(result)
