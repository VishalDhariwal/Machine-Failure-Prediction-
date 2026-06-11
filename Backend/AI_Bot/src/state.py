from typing import TypedDict, Dict, Any, List, Optional


class AgentState(TypedDict):
    user_question: str

    machine_state: Dict[str, Any]

    retrieved_docs: List[str]

    answer: Optional[str]