# Location: backend/app/main.py
# 1. SECURE INITIALIZATION: Load your local .env keys straight into os.environ

from dotenv import load_dotenv
load_dotenv()

import os
import json
import asyncio
import traceback
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 2. Now import settings and your graph safely
from app.core.config import settings
from app.graph.workflow import app_graph
from app.graph.state import AgenticOpsState

app = FastAPI(
    title="AgenticOps Core Streaming Microservice",
    version="1.0.0",
    description="Production Phase 4 asynchronous graph execution and telemetry interface."
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamRequest(BaseModel):
    account_id: str = Field(..., example="acc_2026_99x")
    raw_issue_input: str = Field(..., example="High latency errors surfacing on the historical payment processing cluster.")

async def transform_graph_stream(account_id: str, raw_issue_input: str) -> AsyncGenerator[str, None]:
    """
    Executes the compiled LangGraph asynchronously, captures operational events,
    and yields strictly structured SSE chunks detailing execution segments.
    
    If the underlying LLM does not stream native tokens, this stream handler 
    simulates a high-speed token stream using the completed response to ensure
    the frontend UI streams the text seamlessly.
    """
    initial_state = {
        "account_id": account_id,
        "raw_issue_input": raw_issue_input,
        "extracted_parameters": {},
        "semantic_context_fragments": [],
        "routing_decision": "",
        "agent_logs": ["[API Gateway] Initializing asynchronous state loop."],
        "risk_analysis": {},
        "generated_recommendations": "",
        "audit_history": [],
        "loop_count": 0
    }

    try:
        event_stream = app_graph.astream_events(
            initial_state, 
            version="v2",
            config={"configurable": {"account_id": account_id}}
        )
        
        async for event in event_stream:
            if not isinstance(event, dict):
                continue
            
            kind = event.get("event")
            event_name = event.get("name")
            metadata = event.get("metadata")
            metadata_dict = metadata if isinstance(metadata, dict) else {}
            node_name = metadata_dict.get("langgraph_node", "orchestrator")
            data_field = event.get("data")
            data_dict = data_field if isinstance(data_field, dict) else {}

            try:
                # Handle Root Workflow Start
                if kind == "on_chain_start" and event_name == "LangGraph":
                    yield f"data: {json.dumps({'event': 'workflow_start', 'node': 'root', 'message': 'Assembly line activated'})}\n\n"
                
                # Handle Root Workflow End
                elif kind == "on_chain_end" and event_name == "LangGraph":
                    final_output = data_dict.get("output")
                    loop_val = 0
                    sources_val = []
                    
                    if isinstance(final_output, dict):
                        loop_val = final_output.get("loop_count", 0)
                        sources_val = final_output.get("semantic_context_fragments", [])
                        
                    yield f"data: {json.dumps({'event': 'workflow_end', 'node': 'root', 'metrics': {'loop_count': loop_val}, 'sources': sources_val})}\n\n"

                # Track Individual Node Completions & Stream Simulated Tokens
                elif kind == "on_chain_end" and "langgraph_node" in metadata_dict:
                    node_output = data_dict.get("output")
                    
                    if isinstance(node_output, dict):
                        payload = {
                            "event": "node_complete",
                            "node": str(node_name),
                            "metrics": {
                                "loop_count": int(node_output.get("loop_count", 0) or 0),
                                "routing": str(node_output.get("routing_decision", "UNKNOWN"))
                            }
                        }
                        
                        if node_name == "researcher" and "semantic_context_fragments" in node_output:
                            payload["sources"] = node_output["semantic_context_fragments"]
                        if node_name == "risk_analyst" and "risk_analysis" in node_output:
                            payload["risk_analysis"] = node_output["risk_analysis"]

                        yield f"data: {json.dumps(payload)}\n\n"

                        # --- STREAM SIMULATOR: Splits by line and injects explicit frontend [BREAK] handles ---
                        recommendations = node_output.get("generated_recommendations", "")
                        if recommendations:
                            lines = recommendations.replace("\r\n", "\n").split("\n")
                            for r_idx, line in enumerate(lines):
                                if not line.strip():
                                    continue
                                
                                words = line.split(" ")
                                for w_idx, word in enumerate(words):
                                    token_payload = {
                                        "event": "token",
                                        "node": str(node_name),
                                        "text": word + (" " if w_idx < len(words) - 1 else "")
                                    }
                                    yield f"data: {json.dumps(token_payload)}\n\n"
                                    await asyncio.sleep(0.01)
                                
                                # Appends a custom structural separation token to split bullet rows cleanly
                                if r_idx < len(lines) - 1:
                                    token_payload = {
                                        "event": "token",
                                        "node": str(node_name),
                                        "text": " [BREAK] "
                                    }
                                    yield f"data: {json.dumps(token_payload)}\n\n"
                                    await asyncio.sleep(0.01)

                # Stream Native Incremental LLM Tokens (kept for fallback)
                elif kind == "on_chat_model_stream":
                    chunk = data_dict.get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        token_payload = {
                            "event": "token",
                            "node": str(node_name),
                            "text": str(chunk.content)
                        }
                        yield f"data: {json.dumps(token_payload)}\n\n"

            except (AttributeError, TypeError, ValueError):
                continue

            await asyncio.sleep(0.001)

    except Exception as e:
        print("\n❌ CRITICAL GRAPH EXECUTION EXCEPTION DETECTED:")
        traceback.print_exc()
        
        error_payload = {
            "event": "system_exception",
            "node": "global_error_handler",
            "message": str(e)
        }
        yield f"data: {json.dumps(error_payload)}\n\n"

@app.post("/api/v1/agent/stream")
async def stream_agent_pipeline(request: StreamRequest):
    if not request.account_id or not request.raw_issue_input:
        raise HTTPException(status_code=400, detail="Missing baseline structural targets.")

    return StreamingResponse(
        transform_graph_stream(request.account_id, request.raw_issue_input),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/")
async def root_ping():
    return {"status": "healthy", "service": "AgenticOps Streaming Gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)