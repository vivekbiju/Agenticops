"""
AgenticOps - Phase 6: Mathematical Validation Metrics (E2E Master Script)
File: /backend/tests/run_evaluation.py

This script performs mathematical validation of the AgenticOps pipeline using Ragas and Gemini.
It contains both the simulated pipeline (commented out) and the live system pipeline (active).
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Ragas 0.2.x imports
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics import ContextPrecision, Faithfulness
from ragas.llms import LangchainLLMWrapper
from ragas.run_config import RunConfig
from langchain_google_genai import ChatGoogleGenerativeAI

# Add the backend directory to the system path to guarantee clean module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Dynamic, self-healing import of your LangGraph workflow
try:
    import app.graph.workflow as graph_module
    print("✅ Successfully imported 'app.graph.workflow' module.")
except ModuleNotFoundError as e:
    print(f"❌ Critical Import Error: Could not resolve 'app.graph.workflow'. details: {e}")
    print("Please make sure you are executing this file from the '/backend' folder using:")
    print("  python -m tests.run_evaluation")
    sys.exit(1)

# Load environment variables
load_dotenv()

# --- 1. BASELINE EVALUATION DATASET (20 Multi-faceted Challenges) ---
EVALUATION_DATASET_RAW = [
    {
        "account_id": "ACC_8801",
        "question": "Database connection timeout during peak hour. High spikes in latency, Postgres container throwing 504 Gateway Timeouts.",
        "ground_truth": "Scale active Postgres replicas, flush transient connection pools in PgBouncer, and implement exponential backoff on retry clients."
    },
    {
        "account_id": "ACC_4402",
        "question": "Elasticsearch cluster yellow status. Shards unassigned due to low disk space threshold (watermark exceeded).",
        "ground_truth": "Delete legacy indexes or modify the transient cluster routing settings to relax disk watermarks temporarily while mounting extra EBS volumes."
    },
    {
        "account_id": "ACC_1103",
        "question": "React frontend crashing. Redux state slice exceeding maximum call stack size in infinite dispatch loop.",
        "ground_truth": "Break cyclic dispatch dependency chain in useEffect, use memoized selectors, and throttle rapid websocket state pushes."
    },
    {
        "account_id": "ACC_2204",
        "question": "Stripe webhook events dropped. Signature verification failing consistently with raw 400 Bad Request.",
        "ground_truth": "Update local webhook signing secret in configuration parameters, match the exact timestamp header, and verify payload buffer raw formatting."
    },
    {
        "account_id": "ACC_9505",
        "question": "Gemini API calls throwing 429 ResourceExhausted errors. Operational trace logs showing rate-limit exhaustion.",
        "ground_truth": "Introduce TokenBucket rate limiters locally, configure LangGraph to fall back to a secondary model region, and apply Jittered Backoff."
    },
    {
        "account_id": "ACC_3106",
        "question": "Docker daemon crashing under high memory loads. OOM Killer terminating Uvicorn container.",
        "ground_truth": "Enable memory limits and reservation structures in docker-compose.yml and tune Uvicorn concurrency workers down."
    },
    {
        "account_id": "ACC_7707",
        "question": "AWS S3 bucket uploads rejected with 403 Access Denied on large video chunks.",
        "ground_truth": "Enable multipart upload policies in IAM bucket CORS configurations and verify active role STS credentials."
    },
    {
        "account_id": "ACC_8808",
        "question": "Slow API response times on /api/v1/auth/user due to unindexed foreign keys in dynamic joins.",
        "ground_truth": "Create standard composite B-Tree indexes on user_id and session_id tracking tables inside the central relational database."
    },
    {
        "account_id": "ACC_5509",
        "question": "Kafka broker failing replication. Under-replicated partition count rising on critical operations log.",
        "ground_truth": "Increase partition replication factor to 3, balance broker metadata, and increase file descriptor limits."
    },
    {
        "account_id": "ACC_6610",
        "question": "Redis cache eviction storm. High CPU usage on AWS ElastiCache due to massive concurrent TTL expirations.",
        "ground_truth": "Switch eviction policy to volatile-lru, stagger cache TTL keys with random offsets, and upgrade node instance class."
    },
    {
        "account_id": "ACC_1211",
        "question": "Kubernetes Pods stuck in CrashLoopBackOff. Readiness probe failing due to missing system context env variables.",
        "ground_truth": "Inject dependent configurations using ConfigMaps and Secrets, verify startup probe timeouts, and monitor initial process boots."
    },
    {
        "account_id": "ACC_3412",
        "question": "FastAPI streaming gateway dropping clients. SSE streams disconnect mid-way with broken pipe signals.",
        "ground_truth": "Tweak Keep-Alive headers in FastAPI streaming responses, disable buffering in Nginx reverse-proxies, and handle asyncio.CancelledError."
    },
    {
        "account_id": "ACC_5613",
        "question": "Slow vector queries in Elasticsearch index. Semantic k-NN searches timing out over 5000ms thresholds.",
        "ground_truth": "Tune the num_candidates hyperparameter, shrink embedding dimensions, or pre-filter datasets using strict categorical matches."
    },
    {
        "account_id": "ACC_7814",
        "question": "Expired SSL certificates in staging. Automated certbot cronjob blocked by restrictive security group rules.",
        "ground_truth": "Modify port 80/443 security group access dynamically, run manual Certbot standalone challenge verification, and restart systemd Nginx."
    },
    {
        "account_id": "ACC_9015",
        "question": "JWT verification failing for external SSO. OpenID Configuration discovery endpoints returning stale public keys.",
        "ground_truth": "Invalidate JWT cache stores, force refresh auth secrets every 24 hours, and handle key rotation events gracefully."
    },
    {
        "account_id": "ACC_1316",
        "question": "Next.js server-side hydration errors. Mismatch between server-generated HTML and client-rendered React DOM.",
        "ground_truth": "Use useEffect to execute client-only components, avoid layout manipulations directly using document properties, and clean up inline dates."
    },
    {
        "account_id": "ACC_4217",
        "question": "Disk pressure on logs node. Root file system full from uncompressed local syslog configurations.",
        "ground_truth": "Configure strict daily Logrotate setups, compress rotated files, and route stdout logs directly to CloudWatch or Datadog."
    },
    {
        "account_id": "ACC_6418",
        "question": "N+1 query pattern discovered. Main system dashboard fetching profiles inside an active dashboard loop.",
        "ground_truth": "Optimize ORM queries utilizing joined-load selectors and construct a single parameterized batch select query."
    },
    {
        "account_id": "ACC_8619",
        "question": "Cross-Origin Resource Sharing (CORS) blocks on external static asset CDN distribution.",
        "ground_truth": "Verify Access-Control-Allow-Origin headers match correct production hostnames, allow GET requests, and invalidate cloud cache."
    },
    {
        "account_id": "ACC_9920",
        "question": "Memory leak in node-based streaming daemon. Heap usage climbing endlessly with active user sessions.",
        "ground_truth": "Track and close active listener sockets, remove dead event emitter bindings, and run garbage collection analysis."
    }
]


# --- 2. RAW TEXT / SIMULATED VALIDATION PIPELINE (COMMENTED OUT) ---
# We already successfully ran and generated reports with this. Keeping it documented here.
"""
def run_simulated_pipeline(account_id: str, issue_input: str, ground_truth: str) -> dict:
    simulated_context = [
        f"OPERATIONAL INCIDENT LOG - ID: {account_id}\\n"
        f"Telemetry metrics flagged: {issue_input}\\n"
        f"Historical playbook solution match: {ground_truth}"
    ]
    simulated_response = (
        f"Based on system log telemetry snapshots for account {account_id}, "
        f"the following action plan is recommended: {ground_truth}"
    )
    return {
        "contexts": simulated_context,
        "response": simulated_response
    }
"""


# --- 3. LIVE SYSTEM VALIDATION PIPELINE (ACTIVE) ---
def run_live_pipeline(account_id: str, issue_input: str) -> dict:
    """
    Submits evaluation prompts to your actual compiled LangGraph execution state.
    Uses app.invoke (synchronous execution) to prevent Python 3.14 async timeout errors.
    """
    print(f" -> Executing LIVE state-machine run for {account_id}...")
    try:
        # Dynamically find the executable compiled graph inside your workflow module
        if hasattr(graph_module, 'app'):
            app = graph_module.app
        elif hasattr(graph_module, 'workflow'):
            # If workflow exists but isn't compiled, compile it
            app = graph_module.workflow.compile() if hasattr(graph_module.workflow, 'compile') else graph_module.workflow
        else:
            raise AttributeError("Could not find executable state machine ('app' or 'workflow') in app.graph.workflow.")
        
        # Trigger your real graph workflow synchronously
        final_state = app.invoke({
            "account_id": account_id,
            "raw_issue_input": issue_input,
            "semantic_context_fragments": [],
            "agent_logs": []
        })
        
        # Safely extract retrieved Elasticsearch database context chunks
        retrieved_docs = final_state.get("semantic_context_fragments", [])
        
        # Format the retrieved contexts cleanly into a List[str] for Ragas
        contexts = []
        for doc in retrieved_docs:
            if isinstance(doc, dict):
                contexts.append(doc.get("content", ""))
            else:
                contexts.append(str(doc))
                
        if not contexts:
            contexts = ["No matching reference context found in database."]
        
        # Grab your live LLM markdown response
        response = final_state.get("generated_recommendations", "No recommendation compiled.")
        
        return {
            "contexts": contexts,
            "response": response
        }
        
    except Exception as e:
        print(f"  ⚠️ Live execution failed for {account_id}. Details: {str(e)}")
        # Fallback details to keep the pipeline execution from breaking mid-way
        return {
            "contexts": [f"Execution Error: {str(e)}"],
            "response": f"Live run encountered an exception during processing: {str(e)}"
        }


# --- 4. MAIN RUN PIPELINE ---
def main():
    print("==================================================")
    print("🚀 Starting AgenticOps LIVE Evaluation Pipeline (Phase 6)")
    print("==================================================")
    
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        print("❌ CRITICAL ERROR: GEMINI_API_KEY is not set in environment.")
        return

    # 1. Gather outputs using the active live system pipeline
    print(f"Step 1: Running {len(EVALUATION_DATASET_RAW)} live test cases through LangGraph...")
    samples = []
    for idx, case in enumerate(EVALUATION_DATASET_RAW, 1):
        print(f"[{idx}/20]", end="")
        result = run_live_pipeline(case["account_id"], case["question"])
        
        sample = SingleTurnSample(
            user_input=case["question"],
            response=result["response"],
            reference=case["ground_truth"],
            retrieved_contexts=result["contexts"]
        )
        samples.append(sample)
        
    eval_dataset = EvaluationDataset(samples=samples)
    print("✅ Completed live system runs. Structuring data for Ragas...\n")

    # 2. Authenticate Evaluator Model
    print("Step 2: Authenticating Evaluator Models with Gemini...")
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",  # Highly performant, supported Gemini model
        google_api_key=gemini_key
    )
    eval_llm = LangchainLLMWrapper(gemini_llm)

    # Setup core Ragas metrics
    context_precision = ContextPrecision(llm=eval_llm)
    faithfulness = Faithfulness(llm=eval_llm)
    metrics = [context_precision, faithfulness]

    # 3. Execute Run
    print("Step 3: Calculating mathematical benchmarks...")
    
    # max_workers=1 completely avoids Python 3.14 async event-loop/timeout locks!
    config = RunConfig(
        timeout=180,
        max_retries=1,
        max_workers=1  
    )
    
    evaluation_results = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        run_config=config
    )
    
    df_results = evaluation_results.to_pandas()
    
    avg_precision = df_results["context_precision"].mean()
    avg_faithfulness = df_results["faithfulness"].mean()

    print("\n==================================================")
    print("🏆 AgenticOps LIVE Performance Metrics Report")
    print("==================================================")
    print(f"📊 Context Precision:  {avg_precision:.4f} (Target: >0.85)")
    print(f"📊 Faithfulness:       {avg_faithfulness:.4f} (Target: >0.90)")
    print("==================================================")

    # 4. Generate Markdown Documentation
    report_filename = f"docs/evaluation_report_live.md"
    os.makedirs("docs", exist_ok=True)
    
    markdown_report = f"""# AgenticOps E2E Evaluation Report (LIVE Performance)

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Evaluation framework: Ragas & Gemini Engine (Live System Execution)

## Executive Metrics Summary

| Metric | Score | Target | Status |
|---|---|---|---|
| **Context Precision** | `{avg_precision:.4f}` | `> 0.85` | {"✅ Passed" if avg_precision >= 0.85 else "⚠️ Tuning Required"} |
| **Faithfulness** | `{avg_faithfulness:.4f}` | `> 0.90` | {"✅ Passed" if avg_faithfulness >= 0.90 else "⚠️ Tuning Required"} |

---

## Live System Test Dataset Results

{df_results[['user_input', 'context_precision', 'faithfulness']].to_markdown(index=False)}
"""

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(markdown_report)
        
    print(f"📝 Live Markdown report successfully written to: {report_filename}")

if __name__ == "__main__":
    main()