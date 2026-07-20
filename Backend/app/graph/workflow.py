# Location: backend/app/graph/workflow.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver # Added for state preservation
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
# Update in backend/app/graph/workflow.py

def router_logic(state: AgenticOpsState) -> str:
    """
    Evaluates the routing_decision token in the state to determine the next node.
    Integrates robust, case-insensitive Human-in-the-Loop policy rules for high-risk paths.
    """
    decision = state.get("routing_decision", "")
    
    # 1. Normalize classification parameters for robust evaluation
    urgency = str(state.get("extracted_parameters", {}).get("urgency", "low")).strip().lower()
    category = str(state.get("extracted_parameters", {}).get("category", "")).strip().lower()
    
    # 2. Check HITL Governance Policies BEFORE exiting or entering error paths
    is_high_risk = urgency in ["high", "critical"] or category in ["infrastructure", "security"]
    
    # If the workflow is ending or entering an error cleanup path, but it's high-risk, force a pause
    if is_high_risk and (decision in ["ERROR_HANDLER", "FORCE_END"] or decision not in ["RESEARCHER", "RISK_ANALYST", "AUDITOR", "RE_RESEARCH"]):
        print(f"🚨 High-risk signature detected (Urgency: {urgency}, Category: {category}). Overriding decision '{decision}' to Human Approval Gate...")
        return "human_approval_gate"

    # 3. Standard fallback routing logic
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
workflow.add_node("human_approval_gate", human_approval_gate) # Register the HITL gate node

# Set the structural entrypoint of the graph boundary
workflow.set_entry_point("classifier")

# Map conditional execution routing out of the classifier
# Map conditional execution routing out of the classifier
workflow.add_conditional_edges(
    "classifier",
    router_logic,
    {
        "researcher": "researcher",
        "error_cleanup": "error_cleanup",
        "human_approval_gate": "human_approval_gate"  # 🔑 Added
    }
)

# Map conditional execution routing out of the researcher
workflow.add_conditional_edges(
    "researcher",
    router_logic,
    {
        "risk_analyst": "risk_analyst",
        "error_cleanup": "error_cleanup",
        "human_approval_gate": "human_approval_gate"  # 🔑 Added
    }
)

# Map conditional execution routing out of the risk analyst
workflow.add_conditional_edges(
    "risk_analyst",
    router_logic,
    {
        "auditor": "auditor",
        "error_cleanup": "error_cleanup",
        "human_approval_gate": "human_approval_gate"  # 🔑 Added
    }
)

# Map conditional execution routing out of the auditor (Already has it!)
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

# Connect terminal paths
workflow.add_edge("error_cleanup", END)
workflow.add_edge("human_approval_gate", END) # Once approved, exit cleanly to END

# 4. Compile the Graph with Memory and State Interrupts
memory = MemorySaver()

# We instruct LangGraph to suspend execution right before entering our manual gate
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_approval_gate"]
)

# Keep both references active to support backward compatibility with evaluation scripts
app_graph = app