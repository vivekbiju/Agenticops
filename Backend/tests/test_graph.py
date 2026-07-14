# Location: tests/test_graph.py
import os
from app.graph.workflow import app_graph

def test_workflow_compilation():
    print("Initializing LangGraph Phase 3 State Machine End-to-End Test...")
    
    # 1. Structure an expanded mock incoming sandbox state payload
    mock_initial_state = {
        "account_id": "cust_enterprise_01",
        "raw_issue_input": "Our engineering cluster is throwing critical timeouts with hex error code: 0xDEADBEEF. Performance is degraded.",
        "extracted_parameters": {},
        "semantic_context_fragments": [],
        "routing_decision": "",
        "agent_logs": [],
        
        # New Phase 3 State Fields
        "risk_analysis": {},
        "generated_recommendations": "",
        "audit_history": [],
        "loop_count": 0
    }
    
    try:
        # 2. Invoke the compiled graph execution sync layer
        print("Dispatching mock payload through the multi-agent network...")
        final_state = app_graph.invoke(mock_initial_state)
        
        print("\n✅ LANGGRAPH EXECUTION COMPLETE")
        print(f"Final Routing Decision: {final_state.get('routing_decision')}")
        
        print("\n==================== OPERATIONAL LOGS ====================")
        print("Agent Execution Logs Trace:")
        for log in final_state.get("agent_logs", []):
            print(f" - {log}")
            
        print("\n==================== PHASE 1 & 2 DATA ====================")
        print("Extracted Parameter Structure Matrix:")
        print(final_state.get("extracted_parameters"))
        
        print("\n==================== PHASE 3 METRICS ====================")
        risk_data = final_state.get("risk_analysis", {})
        print(f"Computed Health Score : {risk_data.get('health_score', 'N/A')} / 100")
        print(f"Churn Warning Flag    : {risk_data.get('churn_flag', 'N/A')}")
        print(f"Identified Risk Factors: {risk_data.get('risk_factors', [])}")
        
        print("\n==================== AUDITOR TELEMETRY ====================")
        print(f"Total Iteration Loops Run: {final_state.get('loop_count', 0)}")
        print("Audit History Log:")
        for record in final_state.get("audit_history", []):
            print(f" - {record}")
            
        print("\n==================== FINAL RECOMMENDATION ====================")
        print(final_state.get("generated_recommendations"))
        print("==============================================================")
        
    except Exception as e:
        print(f"\n❌ Integration Graph Test Failed: {str(e)}")

if __name__ == "__main__":
    test_workflow_compilation()