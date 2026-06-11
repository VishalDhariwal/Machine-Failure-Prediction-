from langgraph.graph import StateGraph, END

from Backend.AI_Bot.src.state import AgentState
from Backend.AI_Bot.src.nodes.retrieve import retrieve_node
from Backend.AI_Bot.src.nodes.generate import generate_node


builder = StateGraph(AgentState)

builder.add_node(
    "retrieve",
    retrieve_node
)

builder.add_node(
    "generate",
    generate_node
)

builder.set_entry_point("retrieve")

builder.add_edge(
    "retrieve",
    "generate"
)

builder.add_edge(
    "generate",
    END
)

graph = builder.compile()