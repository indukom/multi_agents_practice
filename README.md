# MultiAgentPractice

A collection of hands-on [LangGraph](https://langchain-ai.github.io/langgraph/) + [LangChain](https://www.langchain.com/) examples built around an "AxiomCart" e-commerce assistant theme. Scripts progress from a single-node chatbot to multi-agent graphs with tools, memory, subgraphs, parallel fan-out/synthesis, and human-in-the-loop interrupts — using Amazon Bedrock (Claude) as the LLM backend.

## Requirements

- Python 3.12 (see [.python-version](.python-version))
- An AWS account with Bedrock access to the Claude model used in these scripts (`us.anthropic.claude-haiku-4-5-20251001-v1:0` in `us-east-1`)
- A [Tavily](https://tavily.com/) API key (for the web-search tool examples)

## Setup

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (uses uv/pyproject.toml)
uv sync
# or: pip install -e .
```

Create a `.env` file in the project root with:

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
TAVILY_API_KEY=...
```

## Scripts

| File | Concept |
|---|---|
| [01_basic_chatbot.py](01_basic_chatbot.py) | Minimal single-node `StateGraph` chatbot backed by `ChatBedrockConverse`. |
| [02_chatbot_with_tool.py](02_chatbot_with_tool.py) | Manual tool-calling loop using the Tavily search tool. |
| [03_chatbot_with_multiple_tools.py](03_chatbot_with_multiple_tools.py) | `ToolNode` + `tools_condition` graph wiring multiple tools (search + a custom `multiply` tool). |
| [04_agenticgraph_with_memory.py](04_agenticgraph_with_memory.py) | Same tool-calling graph with `MemorySaver` checkpointing for conversational memory. |
| [05_travel_planner.py](05_travel_planner.py) | Multi-turn itinerary planner using prompt templates and message history. |
| [06_basic_graph.py](06_basic_graph.py) | Simplest possible `StateGraph`: one node, no LLM — illustrates state flow. |
| [07_subgraph_shared_state.py](07_subgraph_shared_state.py) | Nesting a compiled subgraph directly as a node, sharing the same state shape as the parent. |
| [08_subgraph_wrapper.py](08_subgraph_wrapper.py) | Wrapping a subgraph with a different state shape and mapping fields between parent/child via a wrapper function. |
| [09_parallel_agents_and_synthesizer.py](09_parallel_agents_and_synthesizer.py) | Fan-out to multiple specialist agents in parallel using `Send`, merging results with a reducer, then synthesizing a final answer. |
| [10_HIL_interrupt_and_resume.py](10_HIL_interrupt_and_resume.py) | Human-in-the-loop pattern: `interrupt()` pauses the graph to ask the user a question, then `Command(resume=...)` continues execution using a checkpointer + thread id. |
| [11_mini_axiomcart_end_to_end.py](11_mini_axiomcart_end_to_end.py) | (WIP) End-to-end AxiomCart assistant combining routing, tools, subgraphs, and memory. |

## Utilities ([utils/](utils/))

- [check_bearer_token.py](utils/check_bearer_token.py) — validates AWS/Bedrock auth tokens.
- [check_models.py](utils/check_models.py) — lists accessible Bedrock models.
- [connect_bedrock.py](utils/connect_bedrock.py) — sanity-checks AWS credentials and prints available Claude models.
- [list_models.py](utils/list_models.py) — lists foundation models available in the configured region.

## Running a script

```bash
source .venv/bin/activate
python3 06_basic_graph.py
```

Most scripts print the final graph state (or an intermediate interrupt payload) to stdout via `print(...)`.
