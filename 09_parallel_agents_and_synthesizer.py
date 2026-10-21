from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

class State(TypedDict):
    request: str
    results: Annotated[list[str], add]
    final_answer: str

def router(state: State):
    text = state["request"].lower()
    support_keywords = ["order", "shipping", "delivery"]
    product_keywords = ["product", "headphone", "alternative"]

    destinations = []

    if any(k in text for k in support_keywords):
        destinations.append(Send("support_agent", {"request": state["request"], "results": []}))

    if any(k in text for k in product_keywords):
        destinations.append(Send("product_agent", {"request": state["request"], "results": []}))

    return destinations

def product_agent(state: State):
    # Simulate product agent processing
    return {"results": state["results"] + ["Product agent response"]}

def support_agent(state: State):
    # Simulate support agent processing
    return {"results": state["results"] + ["Support agent response"]}

def synthesizer(state: State):
    # Combine results from both agents
    combined_results = state["results"]
    final_answer = " | ".join(combined_results)
    return {"final_answer": final_answer}

builder = StateGraph(State)
builder.add_node("router", router)
builder.add_node("product_agent", product_agent)
builder.add_node("support_agent", support_agent)
builder.add_node("synthesizer", synthesizer)

builder.add_conditional_edges(START, router, ["product_agent", "support_agent"])
builder.add_edge("product_agent", "synthesizer")
builder.add_edge("support_agent", "synthesizer")
builder.add_edge("synthesizer", END)

graph = builder.compile()
result = graph.invoke({
    "request": "I want to buy a new headphone and let me know the status of my order", 
    "results": [],
    })
print(result)
