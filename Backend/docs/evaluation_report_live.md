# AgenticOps E2E Evaluation Report (LIVE Performance)

Generated on: 2026-07-14 17:54:44
Evaluation framework: Ragas & Gemini Engine (Live System Execution)

## Executive Metrics Summary

| Metric | Score | Target | Status |
|---|---|---|---|
| **Context Precision** | `0.0000` | `> 0.85` | ⚠️ Tuning Required |
| **Faithfulness** | `0.0000` | `> 0.90` | ⚠️ Tuning Required |

---

## Live System Test Dataset Results

| user_input                                                                                                              |   context_precision |   faithfulness |
|:------------------------------------------------------------------------------------------------------------------------|--------------------:|---------------:|
| Database connection timeout during peak hour. High spikes in latency, Postgres container throwing 504 Gateway Timeouts. |                   0 |              0 |
| Elasticsearch cluster yellow status. Shards unassigned due to low disk space threshold (watermark exceeded).            |                   0 |              0 |
| React frontend crashing. Redux state slice exceeding maximum call stack size in infinite dispatch loop.                 |                   0 |              0 |
| Stripe webhook events dropped. Signature verification failing consistently with raw 400 Bad Request.                    |                   0 |              0 |
| Gemini API calls throwing 429 ResourceExhausted errors. Operational trace logs showing rate-limit exhaustion.           |                   0 |              0 |
| Docker daemon crashing under high memory loads. OOM Killer terminating Uvicorn container.                               |                   0 |              0 |
| AWS S3 bucket uploads rejected with 403 Access Denied on large video chunks.                                            |                   0 |              0 |
| Slow API response times on /api/v1/auth/user due to unindexed foreign keys in dynamic joins.                            |                   0 |              0 |
| Kafka broker failing replication. Under-replicated partition count rising on critical operations log.                   |                   0 |              0 |
| Redis cache eviction storm. High CPU usage on AWS ElastiCache due to massive concurrent TTL expirations.                |                   0 |              0 |
| Kubernetes Pods stuck in CrashLoopBackOff. Readiness probe failing due to missing system context env variables.         |                   0 |              0 |
| FastAPI streaming gateway dropping clients. SSE streams disconnect mid-way with broken pipe signals.                    |                   0 |              0 |
| Slow vector queries in Elasticsearch index. Semantic k-NN searches timing out over 5000ms thresholds.                   |                   0 |              0 |
| Expired SSL certificates in staging. Automated certbot cronjob blocked by restrictive security group rules.             |                   0 |              0 |
| JWT verification failing for external SSO. OpenID Configuration discovery endpoints returning stale public keys.        |                   0 |              0 |
| Next.js server-side hydration errors. Mismatch between server-generated HTML and client-rendered React DOM.             |                   0 |              0 |
| Disk pressure on logs node. Root file system full from uncompressed local syslog configurations.                        |                   0 |              0 |
| N+1 query pattern discovered. Main system dashboard fetching profiles inside an active dashboard loop.                  |                   0 |              0 |
| Cross-Origin Resource Sharing (CORS) blocks on external static asset CDN distribution.                                  |                   0 |              0 |
| Memory leak in node-based streaming daemon. Heap usage climbing endlessly with active user sessions.                    |                   0 |              0 |
