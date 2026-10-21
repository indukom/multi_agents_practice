from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    request: str
    order_id: str
    response: str

ORDERS = {
    "ORD102": "Shipped - Expected delivery in 1 day",
    "ORD105": "Delayed - Expected delivery in 7 days",
}

def support_node(state: State):
    order_id = state["order_id"]

    if not order_id:
        order_id = interrupt({
            "question": "Please provide your order ID to check the status.",
            "example": "ORD102"
        })
    status = ORDERS.get(order_id, "Order ID not found.")
    return {
        "order_id": order_id,
        "response": f"{order_id} status: {status}"
    }

builder = StateGraph(State)
builder.add_node("support_node", support_node)
builder.add_edge(START, "support_node")
builder.add_edge("support_node", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {
    "configurable": {
        "thread_id": "customer-1"
    }
}

paused = graph.invoke({
    "request": "Where is my order?",
    "order_id": "",
    "response": ""
}, config=config)

paused
print(paused)

# Resume the same thread
# Resume the SAME thread.
completed = graph.invoke(
    Command(resume="ORD102"),
    config=config
)
completed
print(completed)
