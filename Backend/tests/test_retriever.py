# Location: tests/test_retriever.py
import pytest
from app.services.retriever import ParallelHybridRetriever # Assuming this is your class name
from app.graph.state import AgenticOpsState

def test_hybrid_retrieval_with_expanded_state():
    print("Initializing Hybrid Retrieval Layer Integration Test...")
    
    # 1. Initialize the retriever service
    # (If your retriever requires structural config or client connections, inject it here)
    retriever = ParallelHybridRetriever()
    
    # 2. Build the Phase 3 compliant state payload
    mock_state: AgenticOpsState = {
        "account_id": "cust_enterprise_01",
        "raw_issue_input": "Our engineering cluster is throwing critical timeouts with hex error code: 0xDEADBEEF.",
        "extracted_parameters": {
            "category": "infrastructure",
            "urgency": "high",
            "bug_code": "0xDEADBEEF"
        },
        "semantic_context_fragments": [],
        "routing_decision": "RESEARCHER",
        "agent_logs": [],
        
        # Phase 3 Fields must be initialized to pass typing/validation constraints
        "risk_analysis": {},
        "generated_recommendations": "",
        "audit_history": [],
        "loop_count": 0
    }
    
    # 3. Simulate the exact operational query string generation your Researcher uses
    optimized_query = f"{mock_state['extracted_parameters'].get('bug_code')} {mock_state['extracted_parameters'].get('category')} timeout"
    
    try:
        print(f"Executing parallel BM25 and KNN query for account: {mock_state['account_id']}")
        
        # Execute the controller (this matches your Phase 2 hybrid query schema layout)
        # Assuming top_k=5 for testing
        hits = retriever.execute_hybrid_search(
            account_id=mock_state["account_id"], 
            query_text=optimized_query, 
            top_k=5
        )
        
        # 4. Assert structural integrity of database response
        assert isinstance(hits, list), "Retriever must return a structured list of context hits."
        print(f"✅ Retrieval successful. Extracted {len(hits)} semantic fragments from Elasticsearch.")
        
        # Verify that if entries exist, they map cleanly to what your downstream nodes expect
        if len(hits) > 0:
            assert "content" in hits[0], "Retrieved fragment is missing the standard tokenized 'content' field."
            print(f"Sample Fragment Context Preview: {hits[0]['content'][:100]}...")

    except Exception as e:
        pytest.fail(f"❌ Hybrid Retriever Integration Test Failed: {str(e)}")

if __name__ == "__main__":
    test_hybrid_retrieval_with_expanded_state()