# Location: backend/app/graph/agents/risk_analyst.py
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from langsmith import wrappers
from app.graph.state import AgenticOpsState
from app.core.config import settings

class RiskAnalysisSchema(BaseModel):
    health_score: int = Field(..., description="Absolute numerical customer health score from 0 (critical/churn risk) to 100 (perfectly healthy)")
    churn_flag: bool = Field(..., description="True if health_score is below 50 or critical system bugs are found")
    risk_factors: list[str] = Field(..., description="List of primary drivers for this score")
    recommended_action_plan: str = Field(..., description="Draft copy of remediation steps or recommendations for this client")

class RiskAnalystAgent:
    def __init__(self):
        # Initializing updated google-genai client syntax
        raw_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Wrap the Gemini client to enable automatic LangSmith tracing
        self.client = wrappers.wrap_gemini(
            raw_client,
            tracing_extra={
                "tags": ["agenticops", "risk_analyst"],
                "metadata": {"integration": "google-genai"}
            }
        )

    def analyze_account_risk(self, state: AgenticOpsState) -> Dict[str, Any]:
        """Evaluates numerical metrics and logs to calculate account health scores."""
        # Compile the context fragments gathered by the Researcher
        context_str = "\n".join([str(frag) for frag in state.get("semantic_context_fragments", [])])
        params = state.get("extracted_parameters", {})
        
        # SYSTEM INSTRUCTION STRENGTHENED TO REDUCE HALLUCINATIONS
       
        prompt = f"""
        You are an expert Risk Analyst evaluating account health.

        [SYSTEM INSTRUCTION]
        Ensure all recommendations are strictly derived from the retrieved context. 
        Do not extrapolate, assume, or introduce external steps not present in the logs.

        Account ID: {state['account_id']}
        Extracted Parameters from Input: {params}
        Retrieved Logs & Technical Context:
        {context_str}

        Analyze the raw input and system log details above. Calculate a definitive health score (0-100).

        Draft a comprehensive, factual action plan or recommendation to resolve the client's core issue without speculating beyond the logs.
        CRITICAL FORMATTING: Output the "recommended_action_plan" as a clean numbered list (e.g., 1. First step, 2. Second step) with double newlines (\n\n) separating each numbered item so the frontend can split the stream perfectly.
        """
        
        
        
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',  # Upgraded model to match modern active endpoints
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RiskAnalysisSchema,
                temperature=0.1  # Dropped from 0.2 to 0.1 to guarantee high determinism
            )
        )
        
        # Parse the structured JSON response
        analysis_data = RiskAnalysisSchema.model_validate_json(response.text)
        
        return {
            "risk_analysis": {
                "health_score": analysis_data.health_score,
                "churn_flag": analysis_data.churn_flag,
                "risk_factors": analysis_data.risk_factors
            },
            "generated_recommendations": analysis_data.recommended_action_plan,
            "routing_decision": "AUDITOR",
            "agent_logs": ["Risk Analyst evaluated health metrics and compiled recommendations."]
        }