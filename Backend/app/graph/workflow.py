# Location: backend/app/graph/workflow.py
from langgraph.graph import StateGraph, END
from app.graph.state import AgenticOpsState
from app.graph.agents.classifier import IssueClassifierAgent
from app.graph.agents.researcher import IssueResearcherAgent
# Import your new agents built in Phase 3
from app.graph.agents.risk_analyst import RiskAnalystAgent 
from app.graph.agents.auditor import AuditorAgent

# 1. Initialize our isolated agent class instances
classifier_agent = IssueClassifierAgent()
researcher_agent = IssueResearcherAgent()
risk_analyst_agent = RiskAnalystAgent()
auditor_agent = AuditorAgent()

# 2. Define the Router function to handle dynamic workflow orchestration
def router_logic(state: AgenticOpsState) -> str:
    """Evaluates the routing_decision token in the state to determine the next node."""
    decision = state.get("routing_decision")
    
    if decision == "RESEARCHER":
        return "researcher"
    elif decision == "RISK_ANALYST":
        return "risk_analyst"
    elif decision == "AUDITOR":
        return "auditor"
    elif decision == "RE_RESEARCH":
        return "researcher"  # Route back to researcher for cyclical loop
    elif decision == "ERROR_HANDLER" or decision == "FORCE_END":
        return "error_cleanup"
    else:
        return END

def error_cleanup_node(state: AgenticOpsState):
    """Fallback node to gracefully handle execution failures or forced overrides within the network."""
    return {
        "agent_logs": ["[Workflow Supervisor] Router caught an operational exception or safety stop. Short-circuiting execution."]
    }

# 3. Assemble and build the LangGraph StateGraph
workflow = StateGraph(AgenticOpsState)

# Add Node entrypoints
workflow.add_node("classifier", classifier_agent.classify_incoming_issue)
workflow.add_node("researcher", researcher_agent.research_historical_context)
workflow.add_node("risk_analyst", risk_analyst_agent.analyze_account_risk)
workflow.add_node("auditor", auditor_agent.audit_recommendations)
workflow.add_node("error_cleanup", error_cleanup_node)

# Set the structural entrypoint of the graph boundary
workflow.set_entry_point("classifier")

# Map conditional execution routing out of the classifier
workflow.add_conditional_edges(
    "classifier",
    router_logic,
    {
        "researcher": "researcher",
        "error_cleanup": "error_cleanup"
    }
)

# Map conditional execution routing out of the researcher
workflow.add_conditional_edges(
    "researcher",
    router_logic,
    {
        "risk_analyst": "risk_analyst",
        "error_cleanup": "error_cleanup"
    }
)

# Map conditional execution routing out of the risk analyst
workflow.add_conditional_edges(
    "risk_analyst",
    router_logic,
    {
        "auditor": "auditor",
        "error_cleanup": "error_cleanup"
    }
)

# Map conditional execution routing out of the auditor (Handles loops & final exit)
workflow.add_conditional_edges(
    "auditor",
    router_logic,
    {
        "researcher": "researcher",      # Sends it back on hallucination flag
        "error_cleanup": "error_cleanup",  # Catches FORCE_END (max loops reached)
        END: END
    }
)

# Connect terminal paths
workflow.add_edge("error_cleanup", END)

# Compile the graph into an executable application layer component
app_graph = workflow.compile()