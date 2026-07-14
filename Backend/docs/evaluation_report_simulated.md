# AgenticOps E2E Evaluation Report (Simulated Baseline)

Generated on: 2026-07-14 17:10:50
Evaluation framework: Ragas & Gemini Engine

## Executive Metrics Summary

| Metric | Score | Target | Status |
|---|---|---|---|
| **Context Precision** | `1.0000` | `> 0.85` | ✅ Passed |
| **Faithfulness** | `0.7650` | `> 0.90` | ⚠️ Tuning Required |

---

## Step-by-Step Test Dataset Results

| user_input                                                                                                              |   context_precision |   faithfulness |
|:------------------------------------------------------------------------------------------------------------------------|--------------------:|---------------:|
| Database connection timeout during peak hour. High spikes in latency, Postgres container throwing 504 Gateway Timeouts. |                   1 |       0.75     |
| Elasticsearch cluster yellow status. Shards unassigned due to low disk space threshold (watermark exceeded).            |                   1 |       0.75     |
| React frontend crashing. Redux state slice exceeding maximum call stack size in infinite dispatch loop.                 |                   1 |       0.75     |
| Stripe webhook events dropped. Signature verification failing consistently with raw 400 Bad Request.                    |                   1 |       0.75     |
| Gemini API calls throwing 429 ResourceExhausted errors. Operational trace logs showing rate-limit exhaustion.           |                   1 |       1        |
| Docker daemon crashing under high memory loads. OOM Killer terminating Uvicorn container.                               |                   1 |       0.75     |
| AWS S3 bucket uploads rejected with 403 Access Denied on large video chunks.                                            |                   1 |       0.666667 |
| Slow API response times on /api/v1/auth/user due to unindexed foreign keys in dynamic joins.                            |                   1 |       0.666667 |
| Kafka broker failing replication. Under-replicated partition count rising on critical operations log.                   |                   1 |       0.75     |
| Redis cache eviction storm. High CPU usage on AWS ElastiCache due to massive concurrent TTL expirations.                |                   1 |       0.75     |
| Kubernetes Pods stuck in CrashLoopBackOff. Readiness probe failing due to missing system context env variables.         |                   1 |       0.75     |
| FastAPI streaming gateway dropping clients. SSE streams disconnect mid-way with broken pipe signals.                    |                   1 |       0.75     |
| Slow vector queries in Elasticsearch index. Semantic k-NN searches timing out over 5000ms thresholds.                   |                   1 |       0.75     |
| Expired SSL certificates in staging. Automated certbot cronjob blocked by restrictive security group rules.             |                   1 |       0.75     |
| JWT verification failing for external SSO. OpenID Configuration discovery endpoints returning stale public keys.        |                   1 |       1        |
| Next.js server-side hydration errors. Mismatch between server-generated HTML and client-rendered React DOM.             |                   1 |       0.75     |
| Disk pressure on logs node. Root file system full from uncompressed local syslog configurations.                        |                   1 |       0.75     |
| N+1 query pattern discovered. Main system dashboard fetching profiles inside an active dashboard loop.                  |                   1 |       0.666667 |
| Cross-Origin Resource Sharing (CORS) blocks on external static asset CDN distribution.                                  |                   1 |       0.75     |
| Memory leak in node-based streaming daemon. Heap usage climbing endlessly with active user sessions.                    |                   1 |       0.8      |
