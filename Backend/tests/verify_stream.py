# Location: backend/tests/verify_stream.py
import asyncio
import json
import httpx

async def verify_sse_stream():
    url = "http://127.0.0.1:8000/api/v1/agent/stream"
    payload = {
        "account_id": "acc_2026_99x",
        "raw_issue_input": "High latency errors surfacing on the historical payment processing cluster."
    }
    
    print("🚀 Initiating stream verification against FastAPI service...")
    
    # Use an async client with a generous timeout to allow the multi-agent graph to loop
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                print(f"❌ Error: Received status code {response.status_code}")
                return

            print("✅ Connection established. Streaming wire events:\n" + "-"*50)
            
            # Read line-by-line matching the SSE specification
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    # Strip the SSE prefix to isolate the clean JSON payload
                    raw_json = line.replace("data: ", "").strip()
                    try:
                        event_data = json.loads(raw_json)
                        event_type = event_data.get("event")
                        node = event_data.get("node")
                        
                        # Format console layout based on stream chunk type
                        if event_type == "workflow_start":
                            print(f"\n[WORKFLOW RUN] {event_data.get('message')}")
                        elif event_type == "node_complete":
                            print(f"\n⚡ [NODE HIT] {node.upper()} finalized its execution boundary.")
                            print(f"   -> Metrics: {event_data.get('metrics')}")
                            if "sources" in event_data:
                                print(f"   -> Retained Context Fragments: {len(event_data['sources'])} items loaded.")
                        elif event_type == "token":
                            # Stream individual tokens horizontally 
                            print(event_data.get("text"), end="", flush=True)
                        elif event_type == "workflow_end":
                            print(f"\n\n[WORKFLOW COMPLETE] Processing complete. Total internal loops: {event_data['metrics']['loop_count']}")
                    
                    except json.JSONDecodeError:
                        print(f"\n⚠️ Non-JSON or malformed packet received: {line}")

if __name__ == "__main__":
    asyncio.run(verify_sse_stream())