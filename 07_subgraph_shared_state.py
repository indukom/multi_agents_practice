from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    request: str
    result: str

# Product sub graph
def search_catalog(state: State):
    return {"result": f"Found headphones for: {state['request']}"}

product_builder = StateGraph(State)
product_builder.add_node("search_catalog", search_catalog)
product_builder.add_edge(START, "search_catalog")
product_builder.add_edge("search_catalog", END)
product_subgraph = product_builder.compile()

# ----- PARENT GRAPH -----
parent_builder = StateGraph(State)
parent_builder.add_node("product_agent", product_subgraph)
parent_builder.add_edge(START, "product_agent")
parent_builder.add_edge("product_agent", END)
parent_graph = parent_builder.compile()

result = parent_graph.invoke({"request": "wireless headphones under $300", "result": ""})
print(result)