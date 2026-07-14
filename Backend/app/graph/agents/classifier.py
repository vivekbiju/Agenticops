import json
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from langsmith import wrappers
from app.core.config import settings
from app.graph.state import AgenticOpsState

# Define a strict schema for Gemini to return structured JSON parameters
class IssueClassificationSchema(BaseModel):
    category: str = Field(description="Categories: 'BUG', 'BILLING', 'PERFORMANCE', or 'INFRASTRUCTURE'")
    urgency: str = Field(description="Levels: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'")
    bug_code: str = Field(description="Extract any specific error codes, hex signatures, or 'NONE' if not present")
    sentiment_score: float = Field(description="Floating point value representing user sentiment from 0.0 (furious) to 1.0 (calm)")

class IssueClassifierAgent:
    def __init__(self):
        # Initialize modern client passing validated system configurations
        raw_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Wrap the Gemini client to enable automatic LangSmith tracing
        self.ai = wrappers.wrap_gemini(
            raw_client,
            tracing_extra={
                "tags": ["agenticops", "classifier"],
                "metadata": {"integration": "google-genai"}
            }
        )
        self.model_name = "gemini-3.5-flash"

    def classify_incoming_issue(self, state: AgenticOpsState) -> Dict[str, Any]:
        """
        Agent node that reads raw problem text out of the shared state,
        extracts structural parameters using structured JSON generation,
        and pushes them back to the state boundary.
        """
        raw_input = state.get("raw_issue_input", "")
        account_id = state.get("account_id", "unknown")
        
        system_instruction = (
            "You are an expert enterprise customer intelligence triage agent. "
            "Analyze the incoming engineering issue text, extract specific infrastructure codes, "
            "and compute structural metadata parameters accurately."
        )

        try:
            # Enforce structured output via modern google-genai SDK configurations
            response = self.ai.models.generate_content(
                model=self.model_name,
                contents=f"Classify this issue for account '{account_id}': {raw_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=IssueClassificationSchema,
                    temperature=0.1 # Low variance for deterministic classifications
                )
            )
            
            # The SDK parses directly into JSON when the response schema is enforced
            parsed_data = json.loads(response.text)
            
            # Formulate the node output dictionary following LangGraph state reducer rules
            return {
                "extracted_parameters": parsed_data,
                "routing_decision": "RESEARCHER", # Tell the workflow supervisor to navigate to research next
                "agent_logs": [f"[ClassifierAgent] Processed issue for {account_id}. Category: {parsed_data['category']}."]
            }
            
        except Exception as e:
            return {
                "routing_decision": "ERROR_HANDLER",
                "agent_logs": [f"[ClassifierAgent Error] Processing failed: {str(e)}"]
            }