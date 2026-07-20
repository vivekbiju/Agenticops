# Location: backend/app/graph/workflow.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.state import AgenticOpsState
from app.graph.agents.classifier import IssueClassifierAgent
from app.graph.agents.researcher import IssueResearcherAgent
from app.graph.agents.risk_analyst import RiskAnalystAgent 
from app.graph.agents.auditor import AuditorAgent

# 1. Initialize isolated agent class instances
classifier_agent = IssueClassifierAgent()
researcher_agent = IssueResearcherAgent()
risk_analyst_agent = RiskAnalystAgent()
auditor_agent = AuditorAgent()


# 2. Define the Router function to handle dynamic workflow orchestration
def router_logic(state: AgenticOpsState) -> str:
    decision = state.get("routing_decision", "")
    
    urgency = str(state.get("extracted_parameters", {}).get("urgency", "low")).strip().lower()
    category = str(state.get("extracted_parameters", {}).get("category", "")).strip().lower()
    
    is_high_risk = urgency in ["high", "critical"] or category in ["infrastructure", "security"]
    
    # 🔑 ONLY intercept and pause at HITL gate after Risk Analyst compiles recommendations
    # (i.e. decision == "AUDITOR")
    if is_high_risk and decision == "AUDITOR":
        print(f"🚨 High-risk signature detected. Intercepting before Auditor node -> Routing to Human Approval Gate...")
        return "human_approval_gate"

    # Standard routing logic
    if decision == "RESEARCHER":
        return "researcher"
    elif decision == "RISK_ANALYST":
        return "risk_analyst"
    elif decision == "AUDITOR":
        return "auditor"
    elif decision == "RE_RESEARCH":
        return "researcher"
    elif decision in ["ERROR_HANDLER", "FORCE_END"]:
        return "error_cleanup"
    else:
        return END

def error_cleanup_node(state: AgenticOpsState):
    """Fallback node to gracefully handle execution failures or forced overrides within the network."""
    return {
        "agent_logs": ["[Workflow Supervisor] Router caught an operational exception or safety stop. Short-circuiting execution."]
    }


def human_approval_gate(state: AgenticOpsState):
    """
    This node acts as an isolated state checkpoint. 
    The workflow is configured to pause BEFORE entering this node.
    """
    print("⏳ System paused at Human-in-the-Loop Gate. Awaiting engineer authorization...")
    return {
        "agent_logs": ["[HITL Gate] Workflow paused. System awaiting administrator authorization."]
    }


# 3. Assemble and build the LangGraph StateGraph
workflow = StateGraph(AgenticOpsState)

# Add Node entrypoints
workflow.add_node("classifier", classifier_agent.classify_incoming_issue)
workflow.add_node("researcher", researcher_agent.research_historical_context)
workflow.add_node("risk_analyst", risk_analyst_agent.analyze_account_risk)
workflow.add_node("auditor", auditor_agent.audit_recommendations)
workflow.add_node("error_cleanup", error_cleanup_node)
workflow.add_node("human_approval_gate", human_approval_gate)

# Set structural entrypoint
workflow.set_entry_point("classifier")

# Map conditional execution routing out of classifier
workflow.add_conditional_edges(
    "classifier",
    router_logic,
    {
        "researcher": "researcher",
        "error_cleanup": "error_cleanup",
        "human_approval_gate": "human_approval_gate"
    }
)

# Map conditional execution routing out of researcher
workflow.add_conditional_edges(
    "researcher",
    router_logic,
    {
        "risk_analyst": "risk_analyst",
        "error_cleanup": "error_cleanup",
        "human_approval_gate": "human_approval_gate"
    }
)

# Map conditional execution routing out of risk analyst
workflow.add_conditional_edges(
    "risk_analyst",
    router_logic,
    {
        "auditor": "auditor",
        "error_cleanup": "error_cleanup",
        "human_approval_gate": "human_approval_gate"
    }
)

# Map conditional execution routing out of auditor
workflow.add_conditional_edges(
    "auditor",
    router_logic,
    {
        "researcher": "researcher",      
        "error_cleanup": "error_cleanup",  
        "human_approval_gate": "human_approval_gate", 
        END: END
    }
)

# Connect terminal and bridge paths cleanly
workflow.add_edge("human_approval_gate", "auditor")
workflow.add_edge("error_cleanup", END)

# 4. Compile the Graph with Memory and State Interrupts
memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_approval_gate"]
)

# Keep both references active for compatibility
app_graph = app