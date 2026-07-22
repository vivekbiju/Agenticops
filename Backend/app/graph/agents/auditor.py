# Location: backend/app/graph/agents/auditor.py
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.graph.state import AgenticOpsState
from app.core.config import settings

class AuditSchema(BaseModel):
    is_hallucination: bool = Field(..., description="True if recommendations contain claims not supported by the context fragments")
    audit_reasoning: str = Field(..., description="Explanation of why it passed or what specific hallucination was detected")

class AuditorAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def audit_recommendations(self, state: AgenticOpsState) -> Dict[str, Any]:
        """Cross-references generated recommendations against source context fragments to catch hallucinations."""
        context_str = "\n".join([str(frag) for frag in state.get("semantic_context_fragments", [])])
        recommendation = state.get("generated_recommendations", "")
        current_loops = state.get("loop_count", 0)
        
        # Guardrail against infinite routing loops
        if current_loops >= 3:
            return {
                "routing_decision": "FORCE_END",
                "agent_logs": ["Auditor: Maximum audit loop iterations reached. Forcing termination to avoid infinite cycle."]
            }
            
        # SYSTEM INSTRUCTION STRENGTHENED FOR THE AUDITOR NODE
        prompt = f"""
        You are a strict, objective QA Auditor. Cross-reference the Generated Recommendation against the Provided Factual Source Context.
        
        [AUDIT CRITERIA]
        Ensure all recommendations are strictly derived from the retrieved context. 
        Do not allow external steps, unverified assumptions, or extractions not present in the logs.
        If the recommendation contains claims or parameters not found in the context, flag 'is_hallucination' as True.
        
        Provided Factual Source Context (Logs/Metrics):
        {context_str}
        
        Generated Recommendation:
        {recommendation}
        
        Determine if the Generated Recommendation introduces unverified assumptions, fake parameters, or hallucinated facts not found in the Source Context.
        """
        
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AuditSchema,
                temperature=0.1
            )
        )
        
        audit_result = AuditSchema.model_validate_json(response.text)
        
        # Determine next routing decision based on audit results
        decision = "RE_RESEARCH" if audit_result.is_hallucination else "PASSED"
        clean_recommendation = recommendation.replace("\\n", "\n").strip()
        # Format output using dynamic LLM recommendations if present
        if clean_recommendation:
            playbook_text = (
                f"### Actionable Remediation Playbook\n\n"
                f"**Audit Status:** {decision}\n"
                f"**Audit Reasoning:** {audit_result.audit_reasoning}\n\n"
                f"**Recommended Steps:**\n"
                f"{clean_recommendation}"
            )
        else:
            playbook_text = (
                f"### Actionable Remediation Playbook\n\n"
                f"**Audit Status:** {decision}\n"
                f"**Audit Reasoning:** {audit_result.audit_reasoning}\n\n"
                f"**Recommended Steps:**\n"
                f"1. Isolate nodes exhibiting latency spikes.\n"
                f"2. Inspect resource metrics and database connection pools.\n"
                f"3. Apply mitigation configuration and monitor telemetry."
            )
        playbook_text = playbook_text.replace("\\n", "\n")
        return {
            "generated_recommendations": playbook_text,
            "audit_history": [f"Iteration {current_loops + 1}: {audit_result.audit_reasoning}"],
            "loop_count": current_loops + 1,
            "routing_decision": decision,
            "agent_logs": [f"Auditor completed check. Result: {decision}."]
        }