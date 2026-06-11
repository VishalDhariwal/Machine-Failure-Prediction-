from typing import Dict, Any

from Backend.AI_Bot.src.retriever import retrieve


def retrieve_node(state) -> Dict[str, Any]:

    query = state["user_question"]

    docs = retrieve(query)

    docs_text = [
        doc.page_content
        for doc in docs
    ]

    return {
        "retrieved_docs": docs_text
    }