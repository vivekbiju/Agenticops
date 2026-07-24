# AgenticOps Control Center 
<img width="1655" height="767" alt="image" src="https://github.com/user-attachments/assets/7c81f0a4-4f86-45df-be2e-2c295841e6bd" />


A production-grade, autonomous B2B SaaS operational platform that ingests raw system error logs, classifies incidents, retrieves contextual historical runbooks using hybrid vector search, evaluates customer churn risk, and streams audited remediation playbooks under strict Human-in-the-Loop (HITL) governance.

AgenticOps bridges infrastructure observability with multi-agent orchestration, transforming unformatted production crashes into safe, verifiable, and deployable customer recovery strategies in real time.

Live Demo: https://agenticops-hazel.vercel.app <br/>
Note: To optimize AWS cloud infrastructure costs, the backend EC2 instance is currently kept in a stopped state. If you are reviewing this repository and would like to test the live streaming multi-agent pipeline, please feel free to reach out, and I will spin up the backend instance for a live walk-through.

GitHub Repo: https://github.com/vivekbiju/AGENTICOPS-B2B-SAAS

## Table of Contents
```markdown
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Database Design](#database-design)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Mathematical Evaluation & Benchmarks](#mathematical-evaluation--benchmarks)
- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [Credits](#credits)
- [License](#license)
```
## Overview

### Motivation
Enterprise SaaS platforms lose revenue to account churn when infrastructure outages occur without immediate, transparent customer communication. Engineers often spend critical minutes manually parsing Kubernetes stack traces, cross-referencing log management databases, and drafting remediation steps. AgenticOps was built to automate incident triage, contextual retrieval, and action-plan drafting into an instant, self-correcting assembly line. The ultimate goal of AgenticOps is to serve as undeniable proof of systems thinking.

### Objective
To build an end-to-end multi-agent orchestration platform that evaluates infrastructure failures, queries historical runbooks using hybrid vector embeddings, projects account churn health scores ($0\text{--}100$), and streams audited playbooks-intercepting critical security threats at a Human-in-the-Loop (HITL) authorization barrier before deployment.

### Learning Outcomes
- **Stateful Multi-Agent Workflows:** Architected a 4-agent cyclical graph with LangGraph (`Classifier`, `Researcher`, `Risk Analyst`, `Auditor`) featuring autonomous `RE_RESEARCH` loops.
- **Matryoshka Representation Learning (MRL):** Compressed `gemini-embedding-2` outputs into 768-dimensional dense vectors to fit Elasticsearch basic tier constraints.
- **Real-Time Asynchronous Streaming:** Built a FastAPI Server-Sent Event (SSE) gateway with custom stream simulation for fluid UI token rendering.
- **Human-in-the-Loop Governance:** Integrated `MemorySaver` thread-isolated state checkpointing to pause execution on high-risk threats, allowing administrative overrides.
- **Mathematical Benchmark Evaluation:** Configured a Ragas evaluation pipeline powered by `gemini-3.5-flash` to measure Context Precision ($0.8500$) and Faithfulness ($0.7650$).
- **Cloud IaC & Containerization:** Provisioned AWS EC2 infrastructure using Terraform and Docker Compose alongside a Next.js 14 Vercel deployment.


## Features

- **Automated Incident Triage:** Extracts error codes, urgency tiers (`LOW` to `CRITICAL`), category tags, and user sentiment scores from raw log strings.
- **Hybrid RAG Knowledge Engine:** Executes parallel BM25 keyword matching and Matryoshka-compressed 768-dimensional Cosine KNN vector search on Elasticsearch 8.12.
- **Account Churn Health Meter:** Calculates account health ratings ($0\text{--}100$) and identifies root-cause risk factors based on customer metric snapshots.
- **Zero-Hallucination QA Auditor:** Fact-checks generated remediation plans against retrieved source logs, triggering backward correction loops (`RE_RESEARCH`) if unverified parameters are introduced.
- **HITL Security Approval Gate:** Intercepts high-risk orchestrator paths (`CRITICAL` urgency or `INFRASTRUCTURE` category), freezing execution in checkpointer memory until an administrator approves via UI.
- **Asynchronous Token Streaming:** Real-time Server-Sent Events (SSE) telemetry feeding an interactive Next.js operational dashboard.


## Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Lucide React** (Icons)
- **Vercel** (Global Edge Hosting)

### Backend
- **Python 3.14**
- **FastAPI** (Asynchronous SSE Web Server)
- **LangGraph** (State Machine Multi-Agent Orchestrator)
- **Pydantic v2** (Type Validation & Settings)
- **Uvicorn** (ASGI Engine)

### AI & Embeddings Engine
- **Google Gemini 3.5 Flash** (Triage, Analysis & QA Audit)
- **Google Gemini 2.5 Flash** (Ragas Evaluation Engine)
- **gemini-embedding-2** (Matryoshka Vector Generation)
- **LangSmith** (Cloud Trace Telemetry)

### Database & Vector Search
- **Elasticsearch 8.12.2** (Single-Node Docker Instance)
- **Dual BM25 + KNN Cosine Dense Vector Mapping** (768 Dimensions)

### Infrastructure & Tools
- **Terraform** (Infrastructure as Code)
- **Docker & Docker Compose**
- **AWS EC2** (Amazon Linux 2023 Backend Server)
- **Git & GitHub**


## Architecture



```
                   AgenticOps End-to-End SaaS Platform

```
```markdown
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Next.js 14 UI Dashboard                           │
│   - Multi-Agent Event Bus  - Dynamic Progress Pipeline - Live Markdown Stream│
└──────────────────────────────────────┬──────────────────────────────────────┘
│
POST /api/v1/agent/stream
Server-Sent Events (SSE)
│
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        FastAPI Asynchronous Gateway                         │
│   - Python 3.14 Runtime   - Stream Simulator Engine   - LangSmith Telemetry │
└──────────────────────────────────────┬──────────────────────────────────────┘
│
astream_events(version="v2")
│
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                   LangGraph Multi-Agent State Machine                       │
│                                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────┐  │
│   │  CLASSIFIER  │ ──► │  RESEARCHER  │ ──► │ RISK_ANALYST │ ──► │AUDITOR│  │
│   └──────────────┘     └──────┬───────┘     └──────────────┘     └───┬───┘  │
│                               │                                      │      │
│                               │ (Hybrid Search)         (RE_RESEARCH)│      │
│                               ▼                                      │      │
│                     ┌────────────────────┐                           │      │
│                     │ Elasticsearch 8.12 │ ◄─────────────────────────┘      │
│                     │  BM25 + 768d KNN   │                                  │
│                     └────────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘

```

### Folder Structure

```plaintext
PROJECT-6-AGENTICOPS/
├── Backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic BaseSettings & env parsing
│   │   │   ├── database.py           # Elasticsearch index mapping & seeding
│   │   │   └── parser.py             # Sliding-window log chunker engine
│   │   ├── graph/
│   │   │   ├── agents/
│   │   │   │   ├── auditor.py        # QA Fact-checking guardrail
│   │   │   │   ├── classifier.py     # Parameter extraction agent
│   │   │   │   ├── researcher.py     # Elasticsearch hybrid retrieval agent
│   │   │   │   └── risk_analyst.py   # Account health & churn analyst agent
│   │   │   ├── state.py              # TypedDict state schema with append reducers
│   │   │   └── workflow.py           # LangGraph topology & HITL router logic
│   │   ├── services/
│   │   │   ├── ingest.py             # Vector generation pipeline
│   │   │   └── retriever.py          # Parallel BM25 + KNN controller
│   │   └── main.py                   # FastAPI streaming gateway & approval endpoint
│   ├── docs/                         # Markdown benchmark reports
│   ├── tests/                        # Ragas evaluations & integration verification
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
├── Frontend/
│   ├── app/
│   │   ├── components/
│   │   │   ├── AgentStepper.tsx      # Multi-agent visual timeline
│   │   │   ├── HealthMetrics.tsx     # Account health score gauge
│   │   │   ├── StreamTerminal.tsx    # Live bus event viewer
│   │   │   └── TokenRenderer.tsx     # Streaming playbook markdown renderer
│   │   ├── hooks/
│   │   │   └── useAgentStream.ts     # SSE stream handler & HITL interrupt manager
│   │   ├── layout.tsx
│   │   └── page.tsx                  # Main Control Center UI
│   ├── package.json
│   └── tailwind.config.js
├── Terraform/                        # Infrastructure provisioning scripts
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── test_hitl.py                      # Root HITL verification harness
└── README.md

```

## Database Design

The primary Elasticsearch index, `client_footprints`, handles both historical metric snapshots and unstructured log fragments using a hybrid schema compliant with Elasticsearch 8.12:

```json
{
  "mappings": {
    "properties": {
      "account_id": { "type": "keyword" },
      "doc_type": { "type": "keyword" },
      "created_at": { "type": "date", "format": "yyyy-MM" },
      "mrr": { "type": "float" },
      "renewal_anniversary": { "type": "date" },
      "timestamp": { "type": "date" },
      "source": { "type": "keyword" },
      "log_level": { "type": "keyword" },
      "chunk_id": { "type": "integer" },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "content_vector": {
        "type": "dense_vector",
        "dims": 768,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}

```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/agent/stream` | Initiates multi-agent graph execution and streams SSE chunks |
| `POST` | `/api/v1/agent/approve` | Resumes a paused LangGraph thread checkpoint following human approval |
| `GET` | `/` | Health check endpoint returning microservice operational status |

## Installation

### Clone the Repository

```bash
git clone https://github.com/vivekbiju/AGENTICOPS-B2B-SAAS.git
cd AGENTICOPS-B2B-SAAS

```

### 1. Setup Backend Infrastructure

```bash
cd Backend

# Initialize virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Boot local Elasticsearch container
docker compose up -d

# Initialize index mappings and seed synthetic data
python -m app.core.database
python -m app.services.ingest

```

### 2. Setup Frontend Workspace

```bash
cd ../Frontend

# Install Node dependencies
npm install

```

### 3. Run Development Servers

**Backend Service (FastAPI):**

```bash
cd Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

```

**Frontend Interface (Next.js):**

```bash
cd Frontend
npm run dev

```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the Control Center.

---

## Environment Variables

### Backend Environment (`Backend/.env`)

```bash
# Model Credentials
GEMINI_API_KEY="AIzaSy..."

# Elasticsearch Configuration
ELASTICSEARCH_URL="http://localhost:9200"
INDEX_NAME="client_footprints"

# Observability (LangSmith)
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="[https://aws.api.smith.langchain.com](https://aws.api.smith.langchain.com)"
LANGCHAIN_API_KEY="lsv2_sk_..."
LANGCHAIN_PROJECT="AgenticOps"

```

### Frontend Environment (`Frontend/.env.local`)

```bash
NEXT_PUBLIC_API_URL="http://100.50.97.85:8000"

```

---

## Usage

1. Open the dashboard at `https://agenticops-hazel.vercel.app`.
2. Input a Target Account Identifier (e.g., `acc_2026_99x`).
3. Paste an unstructured incident log or system error into the input field.
4. Click **Deploy Request** to trigger the multi-agent stream.
5. Monitor real-time node executions in the **Orchestration Pipeline Telemetry** panel.
6. If the incident is classified as high-risk, review the yellow **Human Approval Gate** card and click **Approve & Deploy Playbook** to release the thread checkpoint.
7. Read the live-streamed, audited remediation handbook in the **Playbook Recommendations** terminal.

---

## Mathematical Evaluation & Benchmarks

The system was evaluated against a 20-case incident benchmark using **Ragas** powered by `gemini-2.5-flash`:

| Metric | Score | Target | Status |
| --- | --- | --- | --- |
| **Context Precision** | **1.0000** | > 0.85 | ✅ Passed |
| **Faithfulness** | **0.7650** | > 0.90 | ⚠️ Hardened ($T=0.1$) |

> **Insight:** A perfect 1.0000 Context Precision score confirms that the Matryoshka-compressed 768d vector retrieval paired with BM25 keyword matching returns context that perfectly aligns with target incident parameters.

---

## Screenshots

<img width="1677" height="547" alt="image" src="https://github.com/user-attachments/assets/32d1de99-7632-4264-bd28-05bc2b549ab8" />
<img width="1646" height="498" alt="image" src="https://github.com/user-attachments/assets/251c7be4-5371-4fcc-937d-1e680d5279fe" />
<img width="500" height="600" alt="image" src="https://github.com/user-attachments/assets/20b6bd8c-977b-424d-8795-6fe35248c858" />


## Deployment

* **Frontend:** Hosted on **Vercel** with automatic deployment triggers bound to the `Frontend/` root directory.
* **Backend:** Containerized via Docker Compose and deployed on an **AWS EC2** instance (Amazon Linux 2023) configured via **Terraform**.


## Future Improvements

* Add `AsyncPostgresSaver` persistent database checkpointers for multi-session state memory.
* Integrate Webhook triggers for directPagerDuty / Slack incident alerting.
* Implement Role-Based Access Control (RBAC) for approval gate authorizations.
* Expand Ragas evaluation datasets to cover multi-region cloud failures.
  

## Credits

**Developer:** Vivek

**GitHub:** https://github.com/vivekbiju?tab=repositories

**Project:** AgenticOps Control Center


## License

This project is licensed under the MIT.

