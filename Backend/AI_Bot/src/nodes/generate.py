
from typing import Dict, Any

from langchain_core.messages import HumanMessage

from Backend.AI_Bot.src.config import get_llm
from Backend.AI_Bot.src.prompts import SYSTEM_PROMPT

llm = get_llm()


def generate_node(state) -> Dict[str, Any]:

    question = state["user_question"]

    question_lower = question.lower()

    docs = state.get(
        "retrieved_docs",
        []
    )

    machine_state = state.get(
        "machine_state",
        {}
    )



    latest = machine_state.get(
        "latest",
        {}
    )

    prediction = machine_state.get(
        "prediction",
        {}
    )

    history = machine_state.get(
        "history",
        []
    )

    # -------------------------
    # Intent Detection
    # -------------------------

    if any(
        word in question_lower
        for word in [
            "status",
            "health",
            "condition",
            "current state"
        ]
    ):
        intent = "STATUS"
    elif any(
        word in question_lower
        for word in [
            "trend",
            "increasing",
            "decreasing",
            "getting worse",
            "getting better",
            "history"
        ]
    ):
        intent = "TREND"

    elif any(
        word in question_lower
        for word in [
            "why",
            "cause",
            "critical",
            "failure",
            "increase",
            "risk increasing"
        ]
    ):
        intent = "ROOT_CAUSE"
    
    elif any(
        word in question_lower
        for word in [
            "what should i do",
            "how to fix",
            "how do i reduce",
            "recommend",
            "action",
            "next step"
        ]
    ):
        intent = "RECOMMENDATION"

    elif any(
        phrase in question_lower
        for phrase in [
            "what does this machine do",
            "tell me about this machine",
            "what is this machine"
        ]
    ):
        intent = "DESCRIPTION"

    else:
        intent = "GENERAL"

    # -------------------------
    # Structured Machine Context
    # -------------------------

    machine_context = f"""
Machine Telemetry

Air Temperature:
{latest.get("Air_temperature__K_", "N/A")}

Process Temperature:
{latest.get("Process_temperature__K_", "N/A")}

RPM:
{latest.get("Rotational_speed__rpm_", "N/A")}

Torque:
{latest.get("Torque__Nm_", "N/A")}

Tool Wear:
{latest.get("Tool_wear__min_", "N/A")}

Prediction

Failure Probability:
{prediction.get("failure_probability", "N/A")}

Failure Detected:
{prediction.get("failure_detected", "N/A")}

Failure Type:
{prediction.get("failure_type", "N/A")}

Risk Score:
{prediction.get("risk_score", "N/A")}

Risk Level:
{prediction.get("risk_level", "N/A")}

Anomaly:
{prediction.get("is_anomaly", "N/A")}
"""

    # -------------------------
    # Only use docs when needed
    # -------------------------

    if intent in ["STATUS", "DESCRIPTION"]:
        context = ""
    else:
        context = "\n\n".join(docs)


    trend_context = ""

    if history:

        recent_risk_scores = []

        for item in history:

            if "_prob" in item:

                recent_risk_scores.append(
                    item["_prob"]
                )

        trend_context = f"""
    Recent History:

    Number of Records:
    {len(history)}

    Recent Failure Probabilities:
    {recent_risk_scores[-10:]}
    """
    # -------------------------
    # Prompt
    # -------------------------

    prompt = f"""
{SYSTEM_PROMPT}

Intent:
{intent}

Question:
{question}

Current Machine Data:
{machine_context}


Documentation:
{context}

Trend Data:
{trend_context}

Instructions:

If intent is TREND:

-Answer in this format:

-Trend:
<Increasing / Decreasing / Stable>

-Reason:
<short explanation>

-Current Risk:
<risk level>

-Keep response under 6 lines.

If intent is RECOMMENDATION:

- Recommend actions relevant
  to the detected issue.
- Do not recommend maintenance
  procedures unless supported by
  telemetry or documentation.
- Be practical and concise.

If intent is STATUS:
- Answer in 3-5 lines.
- Mention health state.
- Mention risk level.
- Mention failure probability.
- Do not discuss documentation.

If intent is ROOT_CAUSE:
- Explain WHY the issue exists.
- Use telemetry values.
- Use documentation only if relevant.
- Mention contributing factors.

If intent is DESCRIPTION:
- Explain machine purpose.
- Explain components.
- Ignore current telemetry.

If intent is GENERAL:
- Answer naturally.

Do not assume a fault exists unless telemetry supports it.
Do not mention documentation faults that are not currently occurring.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "answer": response.content
    }
