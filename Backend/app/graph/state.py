# Location: backend/app/graph/state.py
from typing import TypedDict, Dict, Any, Annotated
from operator import add

def append_reducer(left: list, right: list) -> list:
    return left + right

class AgenticOpsState(TypedDict):
    # Phase 1 & 2 Fields
    account_id: str
    raw_issue_input: str
    extracted_parameters: Dict[str, Any]
    semantic_context_fragments: Annotated[list, append_reducer]
    routing_decision: str
    agent_logs: Annotated[list, append_reducer]
    
    # Phase 3 Fields
    risk_analysis: Dict[str, Any]       # Stores numerical score (0-100), churn_flags, and reasoning
    generated_recommendations: str     # The draft response/action plan for the customer
    audit_history: Annotated[list, append_reducer] # Tracks loop counts or mitigation notes
    loop_count: int                    # Explicit counter to prevent infinite loops