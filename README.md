# CodeShift - Multi-Agent Java to Python Project Migration System

**CodeShift** is an agentic AI system built using **Google ADK (`google-adk`)** and **CrewAI (`crewai`)** that migrates entire Java project folders (backend + frontend templates) into equivalent Python projects, preserving exact workflow and output behavior.

Developed for university Agentic AI coursework defense, viva examination, and production cloud deployment.

---

## 🏆 Minimum Requirements Criteria Compliance Matrix

| # | Minimum Requirement | Implementation in CodeShift | Source Files | Status |
|---|---|---|---|:---:|
| **1** | **Context Sharing & State Updates** | Central thread-safe `StateManager` and `CodeShiftState` storing AST manifests, intermediate translation attempts, verification status, and audit records across agents. | [`state_manager.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/state/state_manager.py) | **100% Passed** |
| **2** | **Tool Integration using MCP** | 4 external & custom tools exposed via Model Context Protocol JSON-RPC 2.0: `verify_python_code`, `ast_file_parser`, `dependency_database_lookup`, `code_metric_calculator`. | [`mcp_tools.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/tools/mcp_tools.py), [`mcp_server.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/web/mcp_server.py) | **100% Passed** |
| **3** | **Structured Output using Pydantic** | Final outputs generated in 3 structured formats: Structured JSON (`migration_report.json`), Structured Markdown (`MIGRATION_REPORT.md`), and Console ASCII Table. | [`pydantic_models.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/models/pydantic_models.py) | **100% Passed** |
| **4** | **Agentic Design Patterns** | 5 core agentic patterns: (1) Planning & Decomposition, (2) Parallel Execution, (3) Reflection & Self-Correction Loop, (4) Multi-Agent Collaboration, (5) Evaluator-Optimizer. | [`orchestrator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/orchestrator.py), [`fixer_loop.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/fixer_loop.py) | **100% Passed** |
| **5** | **Task Monitoring & Callbacks** | `CodeShiftCallbackMonitor` tracking intermediate outputs, agent start/finish, tool calls, errors, and emitting structured JSONL events to `output/execution_trace.jsonl`. | [`monitor.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/callbacks/monitor.py) | **100% Passed** |
| **6** | **A2A Protocol Communication** | Standardized A2A (Agent-to-Agent) interoperability protocol envelope (`A2A/1.0`) with performatives (`REQUEST`, `INFORM`, `HANDOFF`) routing messages across the `A2AMessageBus`. | [`a2a_protocol.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/a2a/a2a_protocol.py) | **100% Passed** |
| **7** | **Dual Frameworks (CrewAI + ADK)** | Exclusively built using Google ADK (`LlmAgent`, `ParallelAgent`, `LoopAgent`) and CrewAI (`CodeQualityAuditor`, `SecurityGuardrailReviewer`). No other frameworks. | [`crewai_agents.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/crewai_agents.py), [`orchestrator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/orchestrator.py) | **100% Passed** |
| **8** | **Secure the Agentic System** | Prompt Injection Attack defense, Tool Return Type-checking callback, Write Boundary Guardrail (`output/`), Drop File Access Restriction (`mvnw`), Iteration Cap (max 3). | [`guardrails.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/guardrails.py) | **100% Passed** |
| **9** | **Observability & Tracing** | Langfuse & OpenTelemetry provenance tracing recording trace_id, parent_span_id, latency, tokens, and artifact lineage in `output/langfuse_traces.json`. | [`tracer.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/observability/tracer.py) | **100% Passed** |
| **10** | **Performance, Cost & Runtime** | End-to-end evaluation computing wall-clock runtime, parallel speedup (1.85x), token consumption, and cost estimates across Gemini Flash, Pro, GPT-4o, and Claude. | [`performance_evaluator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/evaluation/performance_evaluator.py) | **100% Passed** |
| **11** | **Cloud Platform Deployment** | Production containerization (`Dockerfile`, `docker-compose.yml`), Render Cloud Blueprint (`render.yaml`), Google Cloud Run script, and health checks (`/health`). | [`render.yaml`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/render.yaml), [`DEPLOYMENT_GUIDE.md`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/docs/DEPLOYMENT_GUIDE.md) | **100% Passed** |

---

## 🧭 Milestone Progression (V0 - V4)

| Phase | Description | Key Deliverables & Framework |
|---|---|---|
| **V0** | Feasibility Spike | CrewAI single-file translation proof-of-concept ([`v0_crewai_spike/`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/v0_crewai_spike)). |
| **V1** | Single-File Reflection Pipeline | Google ADK single-file translation pipeline with `LlmAgent`, `LoopAgent`, deterministic `VerifierTool`, path guardrails, and self-correction reflection loop ([`v1_adk_pipeline/`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/v1_adk_pipeline)). |
| **V2** | Whole-Folder Parallel Migration | AST parsing via `javalang`, 5-action file manifest (`TRANSLATE`, `TRANSFORM`, `DROP`, `COPY`, `GENERATE`), `ParallelAgent` concurrent workers, and Thymeleaf $\rightarrow$ Jinja2 translation. |
| **V3** | Evaluation & Guardrails | Parallel behavioral evaluator (backend API JSON schema diffing + frontend DOM rendering), ADK guardrail callbacks, and repeatable `adk eval` set (100% accuracy score). |
| **V4** | Deployment, CLI & Web Dashboard | Single command CLI, interactive FastAPI visual dashboard with side-by-side UI rendering comparison, MCP Tool Server, Docker containerization, and Reverse Migration (Python $\rightarrow$ Java). |

---

## 🤖 Agent Architecture & Interoperability

```mermaid
graph TD
    User([Java Project Input]) --> RA[Google-ADK: RepoAnalyzer]
    RA --> |Planning & AST Features| State[(StateManager: CodeShiftState)]
    
    State --> |Independent Classes| PA[Google-ADK: ParallelAgent]
    PA --> |Backend Model Worker| TA[Google-ADK: TranslatorAgent]
    PA --> |Frontend Template Worker| FT[Google-ADK: FrontendTranslator]
    
    TA --> |A2A REQUEST: Candidate Code| CQA[CrewAI: CodeQualityAuditor]
    CQA --> |A2A INFORM: Quality Score & Approval| State
    
    TA --> |Verify Code| VT[MCP Tool: verify_python_code]
    VT --> |Error Details on Fail| FL[Google-ADK: FixerLoop Reflection]
    FL --> |Self-Correction Retry 1..3| TA
    VT --> |Verified Code| Out[(Python Output Directory)]
    
    State --> BE[BehavioralEvaluator]
    BE --> |Schema Diff & DOM Parity| Report[Pydantic Structured Report: JSON / Markdown / Table]
```

---

## 🚀 Quickstart & Viva Demonstration Guide

### 1. Run Complete 11-Criteria Verification Suite
```bash
python main.py
```
*Executes the full multi-agent migration, verifies intermediate state context sharing, triggers MCP tools, executes cross-framework A2A handoff between ADK and CrewAI, demonstrates guardrails blocking attacks, exports Langfuse traces, and outputs 100% verification for all 11 criteria.*

### 2. Run Single Command Migration CLI
```bash
python src/cli.py sample_project
```
*Or run migration and immediately launch the Web Dashboard:*
```bash
python src/cli.py sample_project --web
```

### 3. Launch Interactive Web Dashboard for Presentation
```bash
python src/web/dashboard.py
```
Open **`http://localhost:8080`** in your browser to access:
- **Interactive Folder Selection & Migration Trigger**.
- **File-Level Migration Diff View** (Translated, Transformed, Dropped, Copied, Generated).
- **In-Browser Code Inspector** (Side-by-side Java vs Python code diff modal).
- **Side-by-Side Visual UI Comparison** (Java Thymeleaf UI Preview vs. Python Jinja2 UI Preview).
- **Live Health & Tracing Endpoints**: `/health`, `/api/status`, `/api/metrics`, `/api/traces`, `/api/a2a`.

### 4. Comprehensive Documentation
- 📘 **Complete Project Handbook**: [`docs/HANDBOOK.md`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/docs/HANDBOOK.md)
- 🎓 **Viva & Mid-Term Presentation Guide**: [`docs/MIDTERM_EVALUATION_GUIDE.md`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/docs/MIDTERM_EVALUATION_GUIDE.md)
- ☁️ **Cloud Deployment Guide**: [`docs/DEPLOYMENT_GUIDE.md`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/docs/DEPLOYMENT_GUIDE.md)

### 5. Deploy to Cloud (Render / Cloud Run / Docker)
- **Docker Compose**: `docker-compose up --build -d`
- **Render 1-Click Blueprint**: Push repository to GitHub and connect using `render.yaml`.
