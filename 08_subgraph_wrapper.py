from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class ProductState(TypedDict):
    query: str
    recommendation: str

def recommend_product(state: ProductState):
    query = state["query"].lower()
    recommendation = "We recommend the latest smartphone." if "phone" in query else "We recommend our best-selling laptop."
    return {"recommendation": recommendation}

sub_builder = StateGraph(ProductState)
sub_builder.add_node("recommend_product", recommend_product)
sub_builder.add_edge(START, "recommend_product")
sub_builder.add_edge("recommend_product", END)
product_subgraph = sub_builder.compile()

# Parent graph
class ParentState(TypedDict):
    customer_request: str
    final_answer: str

#wrapper function to invoke the subgraph
def invoke_product_subgraph(state: ParentState):
    result = product_subgraph.invoke({
        "query": state["customer_request"],
        "recommendation": ""
    })

    # get the recommendation from the subgraph result and return it in the parent state
    return {"final_answer": result["recommendation"]}

parent_builder = StateGraph(ParentState)
parent_builder.add_node("invoke_product_subgraph", invoke_product_subgraph)
parent_builder.add_edge(START, "invoke_product_subgraph")
parent_builder.add_edge("invoke_product_subgraph", END)
parent_graph = parent_builder.compile()

results = parent_graph.invoke({
    "customer_request": "Can you suggest a good product to buy?",
    "final_answer": ""
})

print(results)