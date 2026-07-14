from typing import Dict, Any
import traceback
from app.core.database import get_es_client
from app.services.retriever import HybridRetrieverController
from app.graph.state import AgenticOpsState

class IssueResearcherAgent:
    def __init__(self):
        # Bind our functional elasticsearch hybrid engine
        self.es_client = get_es_client()
        self.retriever = HybridRetrieverController(es_client=self.es_client)

    def research_historical_context(self, state: AgenticOpsState) -> Dict[str, Any]:
        """
        Agent node that takes classification targets out of the state,
        queries the dual-engine Elasticsearch cluster, and logs traceable
        historical fragments back to the graph context.
        """
        account_id = state.get("account_id")
        raw_issue = state.get("raw_issue_input")
        
        # Pull parameters dynamically populated by the prior classifier node
        params = state.get("extracted_parameters", {})
        category = params.get("category", "GENERAL")
        bug_code = params.get("bug_code", "NONE")

        # Build an optimized target search string using classification details
        search_query = f"{raw_issue} category:{category}"
        if bug_code != "NONE":
            search_query += f" error_code:{bug_code}"

        try:
            # Execute our 8.12-compliant hybrid lookup
            hits = self.retriever.hybrid_search(
                query_text=search_query,
                account_id=account_id,
                top_k=3
            )
            
            # Format logs for downstream analysis
            fragments = []
            for hit in hits:
                fragments.append({
                    "content": hit["content"],
                    "source": hit["metadata"]["source"],
                    "timestamp": hit["metadata"]["timestamp"]
                })
                
            return {
                "semantic_context_fragments": fragments,
                "routing_decision": "RISK_ANALYST", # Route forward to our next analysis node
                "agent_logs": [f"[ResearcherAgent] Located {len(fragments)} historical contextual anchors for account {account_id}."]
            }
            
        except Exception as e:
            # --- DIAGNOSTIC PRINT ADDED HERE ---
            print("\n" + "="*80)
            print("❌ CRITICAL ERROR IN RESEARCHER AGENT:")
            print("="*80)
            traceback.print_exc()  # This prints the complete traceback to your uvicorn console
            print("="*80 + "\n")
            # -----------------------------------
            
            return {
                "routing_decision": "ERROR_HANDLER",
                "agent_logs": [f"[ResearcherAgent Error] Retrieval extraction failed: {str(e)}"]
            }