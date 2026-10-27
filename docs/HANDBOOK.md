# 📘 CodeShift Project Handbook: Architecture, Agents & Operation Guide

> **A Comprehensive Guide to the Multi-Agent Java to Python Project Migration System**  
> Built with **Google ADK (`google-adk`)** and **CrewAI (`crewai`)**  
> Designed for coursework defense, viva examination, and enterprise migration workflows.

---

## 📑 Table of Contents
1. [🌟 Executive Summary & Mission](#1-executive-summary--mission)
2. [🗂️ Clean Project Directory Structure](#2-clean-project-directory-structure)
3. [🤖 All Agents: Names, Frameworks & Responsibilities](#3-all-agents-names-frameworks--responsibilities)
4. [💡 How the System Works in Simple Terms](#4-how-the-system-works-in-simple-terms)
5. [🏆 The 11 Minimum Requirements Criteria Matrix](#5-the-11-minimum-requirements-criteria-matrix)
6. [🚀 How to Run CodeShift (All Modes)](#6-how-to-run-codeshift-all-modes)
7. [🔒 Security Guardrails & Validation Callbacks](#7-security-guardrails--validation-callbacks)
8. [📊 Tracing, Observability & Auditing](#8-tracing-observability--auditing)
9. [☁️ Cloud Deployment & Containerization](#9-cloud-deployment--containerization)

---

## 1. 🌟 Executive Summary & Mission

### The Problem
Migrating legacy enterprise Java applications (e.g., Spring Boot, Thymeleaf, Maven) to modern Python (FastAPI, Jinja2, Pydantic) manually is notoriously expensive, slow, and prone to regression bugs. Single-prompt LLMs fail because whole projects have inter-file dependencies, shared configuration, database mappings, and frontend-backend contracts.

### The CodeShift Solution
**CodeShift** uses a specialized team of autonomous agents operating under **Google ADK** and **CrewAI**, communicating through the standardized **A2A (Agent-to-Agent)** protocol and **Model Context Protocol (MCP)** tools. CodeShift parses the complete repository AST, forms an execution DAG, translates backend code and frontend templates concurrently, validates correctness through a compiler-guided reflection loop, and evaluates behavioral schema parity.

---

## 2. 🗂️ Clean Project Directory Structure

The project has been restructured into an intuitive, modular `src/` layout so that every component has an unambiguous location:

```text
CodeShift/
├── main.py                        # Root test runner & 11-criteria verification suite
├── Dockerfile                     # Production container blueprint for dashboard & agents
├── docker-compose.yml             # Single-command local container orchestration
├── render.yaml                    # 1-Click cloud deployment blueprint for Render
├── requirements.txt               # Unified project dependencies (ADK, CrewAI, FastAPI, etc.)
├── sample_project/                # Reference Java Spring Boot source code (Pet Clinic)
│   ├── pom.xml
│   └── src/main/...
│
├── src/                           # Core implementation codebase
│   ├── agents/                    # All autonomous agents (ADK & CrewAI)
│   │   ├── orchestrator.py        # Root MigrationOrchestrator coordinating pipeline
│   │   ├── repo_analyzer.py       # Whole-repo AST parser & 5-action manifest planner
│   │   ├── translator_agent.py    # Java to Python rule-based / LLM translator
│   │   ├── frontend_translator.py # Thymeleaf to Jinja2 HTML template converter
│   │   ├── config_translator.py   # Maven pom.xml & application.properties transformer
│   │   ├── fixer_loop.py          # Compiler-driven reflection & self-correction loop
│   │   ├── crewai_agents.py       # CrewAI CodeQualityAuditor & Security Reviewer
│   │   ├── evaluator.py           # BehavioralEvaluator (API schema & DOM parity)
│   │   ├── guardrails.py          # Prompt injection, path traversal & write boundary defense
│   │   └── adk_eval_runner.py     # Repeatable ADK evaluation test suite runner
│   │
│   ├── state/                     # Shared context & state management (Req 1)
│   │   └── state_manager.py       # Thread-safe StateManager & CodeShiftState container
│   │
│   ├── tools/                     # Model Context Protocol (MCP) Tools (Req 2)
│   │   ├── mcp_tools.py           # 4 MCP tools: verifier, AST parser, DB lookup, calculator
│   │   ├── mcp_client.py          # Unified client interface for MCP tool invocation
│   │   └── verifier_tool.py       # Deterministic py_compile syntax validator
│   │
│   ├── models/                    # Structured output schemas (Req 3)
│   │   └── pydantic_models.py     # Pydantic v2 models for JSON, Markdown & Table reports
│   │
│   ├── a2a/                       # Agent-to-Agent protocol communication (Req 6 & 7)
│   │   └── a2a_protocol.py        # A2A/1.0 protocol envelopes, performatives & message bus
│   │
│   ├── callbacks/                 # Task monitoring & lifecycle callbacks (Req 5 & 8)
│   │   └── monitor.py             # CodeShiftCallbackMonitor logging to execution_trace.jsonl
│   │
│   ├── observability/             # Observability & tracing (Req 9)
│   │   └── tracer.py              # Langfuse & OpenTelemetry provenance tracing
│   │
│   ├── evaluation/                # Performance, runtime & cost estimation (Req 10)
│   │   └── performance_evaluator.py # Wall-clock speedup, token counter & multi-model costs
│   │
│   ├── web/                       # Web Dashboard & MCP Server (Req 11)
│   │   ├── dashboard.py           # Dynamic FastAPI Web Dashboard & Code Inspector
│   │   └── mcp_server.py          # MCP JSON-RPC 2.0 tool execution server
│   │
│   └── cli.py                     # Single-command developer CLI tool
│
├── docs/                          # Guides and coursework documentation
│   ├── HANDBOOK.md                # This comprehensive handbook
│   ├── MIDTERM_EVALUATION_GUIDE.md# Professor viva presentation script & questions
│   └── DEPLOYMENT_GUIDE.md        # Step-by-step cloud hosting instructions
│
└── output/                        # Generated Python project & verification artifacts
    ├── migration_report.json      # Structured Pydantic JSON report
    ├── MIGRATION_REPORT.md        # Formatted Markdown report
    ├── execution_trace.jsonl      # Callback lifecycle logs
    ├── langfuse_traces.json       # Observability traces
    └── *.py                       # Converted Python classes & templates
```

---

## 3. 🤖 All Agents: Names, Frameworks & Responsibilities

There are **9 autonomous agents** operating collaboratively across Google ADK and CrewAI:

| # | Agent Name | Framework | Source File | Core Responsibility |
|---|---|---|---|---|
| **1** | **`RepoAnalyzer`** | Google ADK (`LlmAgent`) | [`src/agents/repo_analyzer.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/repo_analyzer.py) | Scans the input Java repository ASTs using `javalang`, categorizes every file into the 5-action manifest (`TRANSLATE`, `TRANSFORM`, `DROP`, `COPY`, `GENERATE`), and calculates dependency topological DAG order. |
| **2** | **`TranslatorAgent`** | Google ADK (`LlmAgent`) | [`src/agents/translator_agent.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/translator_agent.py) | Translates Spring Boot Java classes (Controllers, Services, Models, Repositories) into idiomatic Python (FastAPI routers, Pydantic dataclasses, SQLModel entities). |
| **3** | **`FrontendTranslator`** | Google ADK (`LlmAgent`) | [`src/agents/frontend_translator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/frontend_translator.py) | Translates Thymeleaf HTML templates to Python Jinja2 templates, converting tags like `th:text`, `th:each`, `th:field`, `th:if`, and `th:href`. |
| **4** | **`ConfigTranslator`** | Google ADK (`LlmAgent`) | [`src/agents/config_translator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/config_translator.py) | Transforms Maven `pom.xml` dependencies into equivalent Python `requirements.txt` packages and Spring `application.properties` into Python environment configs. |
| **5** | **`FixerLoopPipeline`** | Google ADK (`LoopAgent`) | [`src/agents/fixer_loop.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/fixer_loop.py) | Implements an autonomous self-correction reflection loop: executes deterministic syntax compilation; if errors are caught, feeds the compiler error message back to the translator to regenerate fixed code (capped at 3 iterations). |
| **6** | **`ParallelAgent`** | Google ADK (`ParallelAgent`) | [`src/agents/orchestrator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/orchestrator.py) | Coordinates concurrent execution workers across backend classes and frontend templates, yielding a **1.85x speedup** over sequential execution. |
| **7** | **`CodeQualityAuditor`** | CrewAI (`Agent`) | [`src/agents/crewai_agents.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/crewai_agents.py) | Audits candidate Python code dispatched by Google ADK via the A2A protocol. Checks code quality, type hints, security flaws, and assigns a quality score (0–100%). |
| **8** | **`SecurityReviewer`** | CrewAI (`Agent`) | [`src/agents/crewai_agents.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/crewai_agents.py) | Secondary security and toxicity auditor validating prompt safety, toxic language, and preventing jailbreak attacks. |
| **9** | **`BehavioralEvaluator`** | Google ADK (`ParallelAgent`) | [`src/agents/evaluator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/evaluator.py) | Evaluator-Optimizer agent running golden-master behavioral checks: diffs API JSON schemas and renders Jinja2 HTML templates in parallel to guarantee zero functional regression. |

---

## 4. 💡 How the System Works in Simple Terms

Think of CodeShift like an **automated software engineering agency**:

1. **Step 1 - The Architect Inspects the Blueprint (`RepoAnalyzer`)**:
   Instead of blindly translating line by line, the analyzer inspects the whole Java project. It identifies build scripts (`mvnw` $\rightarrow$ drop), configuration (`pom.xml` $\rightarrow$ transform), HTML views (Thymeleaf $\rightarrow$ translate), and Java classes. It determines which classes depend on which, ensuring models are created before controllers.

2. **Step 2 - The Central Whiteboard (`StateManager`)**:
   All agents write to and read from a shared thread-safe state container. Intermediate outputs from one agent (like AST features) become inputs to the next agent (the translator).

3. **Step 3 - Parallel Assembly Line (`ParallelAgent`)**:
   Backend models and frontend HTML views are translated simultaneously by specialized workers, saving considerable time.

4. **Step 4 - Cross-Department Quality Handoff (`A2A Protocol`)**:
   The Google-ADK translator finishes a draft and hands it off across frameworks to the **CrewAI Code Quality Auditor** using the standard `A2A/1.0` protocol envelope. CrewAI reviews the code, approves it, and returns an official approval record.

5. **Step 5 - Automated Compiler Testing (`FixerLoopPipeline`)**:
   The code is compiled using deterministic MCP verification tools. If a syntax mistake occurs, the error output is fed right back to the agent to fix its mistake, trying up to 3 times automatically.

6. **Step 6 - Golden Master Testing (`BehavioralEvaluator`)**:
   The evaluator calls the migrated API endpoints and renders the templates, confirming the Python code produces the exact same JSON and HTML structure as the original Java code.

7. **Step 7 - Transparent Reporting & Tracing**:
   Every lifecycle event is logged via callbacks into `output/execution_trace.jsonl`, and full provenance traces are sent to Langfuse.

---

## 5. 🏆 The 11 Minimum Requirements Criteria Matrix

| # | Minimum Requirement Criteria | Implementation in CodeShift | Location in Codebase |
|---|---|---|---|
| **1** | **Context Sharing & State Updates** | Central thread-safe `StateManager` and `CodeShiftState` storing AST manifests, intermediate translation attempts, verification status, and audit records. | [`src/state/state_manager.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/state/state_manager.py) |
| **2** | **Tool Integration using MCP** | 4 external & custom tools exposed via Model Context Protocol JSON-RPC 2.0: `verify_python_code`, `ast_file_parser`, `dependency_database_lookup`, `code_metric_calculator`. | [`src/tools/mcp_tools.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/tools/mcp_tools.py) |
| **3** | **Structured Output using Pydantic** | Outputs generated in 3 structured forms: Structured JSON (`migration_report.json`), Structured Markdown (`MIGRATION_REPORT.md`), and Console ASCII Table. | [`src/models/pydantic_models.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/models/pydantic_models.py) |
| **4** | **Agentic Design Patterns** | 5 core agentic patterns: (1) Planning & Decomposition, (2) Parallel Execution, (3) Reflection & Self-Correction Loop, (4) Multi-Agent Collaboration, (5) Evaluator-Optimizer. | [`src/agents/orchestrator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/orchestrator.py) |
| **5** | **Task Monitoring & Callbacks** | `CodeShiftCallbackMonitor` tracking intermediate outputs, agent start/finish, tool calls, errors, and emitting structured JSONL events to `output/execution_trace.jsonl`. | [`src/callbacks/monitor.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/callbacks/monitor.py) |
| **6** | **A2A Protocol Communication** | Standardized A2A interoperability envelope (`A2A/1.0`) with performatives (`REQUEST`, `INFORM`, `HANDOFF`) routing messages across the `A2AMessageBus`. | [`src/a2a/a2a_protocol.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/a2a/a2a_protocol.py) |
| **7** | **Dual Frameworks (CrewAI + ADK)** | Exclusively built using Google ADK (`LlmAgent`, `ParallelAgent`, `LoopAgent`) and CrewAI (`CodeQualityAuditor`, `SecurityReviewer`). No other frameworks. | [`src/agents/crewai_agents.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/crewai_agents.py) |
| **8** | **Secure the Agentic System** | Prompt Injection Defense regex, Tool Return Type-checking callback, Write Boundary Guardrail (`output/`), Drop File Access Restriction (`mvnw`), Iteration Cap (max 3). | [`src/agents/guardrails.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/guardrails.py) |
| **9** | **Observability & Tracing** | Langfuse & OpenTelemetry provenance tracing recording trace_id, parent_span_id, latency, tokens, and artifact lineage in `output/langfuse_traces.json`. | [`src/observability/tracer.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/observability/tracer.py) |
| **10** | **Performance, Cost & Runtime** | Wall-clock runtime, parallel speedup (1.85x), token consumption, and cost estimates across Gemini Flash, Pro, GPT-4o, and Claude. | [`src/evaluation/performance_evaluator.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/evaluation/performance_evaluator.py) |
| **11** | **Cloud Platform Deployment** | Production containerization (`Dockerfile`, `docker-compose.yml`), Render Cloud Blueprint (`render.yaml`), Google Cloud Run script, and health checks (`/health`). | [`render.yaml`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/render.yaml), [`Dockerfile`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/Dockerfile) |

---

## 6. 🚀 How to Run CodeShift (All Modes)

### Mode 1: Run the Complete Master Verification Suite
To execute the full migration and verify all 11 criteria in a single run:
```bash
python main.py
```
**Expected Outcome**: All 11 criteria will print `[PASS]` and conclude with:
```text
==================================================================
 [SUCCESS] ALL 11 MINIMUM REQUIREMENTS CRITERIA VERIFIED 100% SUCCESSFULLY!
==================================================================
```

### Mode 2: Run Developer CLI Tool
Migrate any Java repository with a single terminal command:
```bash
python src/cli.py sample_project
```
To run migration and immediately launch the web dashboard:
```bash
python src/cli.py sample_project --web
```

### Mode 3: Launch Interactive Web Dashboard
```bash
python src/web/dashboard.py
```
Open **`http://localhost:8080`** in your browser to:
- Inspect the live file-level migration diff.
- View side-by-side Java vs Python code in the interactive modal.
- Compare Thymeleaf UI vs Jinja2 UI rendered templates.
- Check live health status at [`http://localhost:8080/health`](http://localhost:8080/health).

### Mode 4: Run via Docker Container
```bash
docker-compose up --build -d
```
Access the containerized application at `http://localhost:8080`.

---

## 7. 🔒 Security Guardrails & Validation Callbacks

CodeShift enforces 4 active defensive guardrails ([`src/agents/guardrails.py`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/src/agents/guardrails.py)):

1. **Prompt Injection Defense (`validate_prompt_security`)**:
   Intercepts adversarial inputs containing instructions like `"ignore all previous instructions"`, `"system prompt override"`, or toxic commands, immediately raising a `PromptInjectionAttackError`.
2. **Tool Return Data Validation (`validate_tool_return_data`)**:
   Callbacks check the return values of tools (e.g., verifying `verifier_tool` does not return `None` or corrupt payloads) before allowing downstream agents to process them.
3. **Directory Traversal & Write Boundary Guardrail (`validate_file_write_path`)**:
   Ensures translated code can **only** be written within the designated `output/` directory, blocking path traversal attacks like `../../windows/system32`.
4. **Drop File Access Restriction (`validate_translator_file_access`)**:
   Prevents the translator agents from consuming unnecessary files (such as `.class` binaries or wrapper scripts like `mvnw`).

---

## 8. 📊 Tracing, Observability & Auditing

- **Lifecycle Monitoring (`output/execution_trace.jsonl`)**:
  Every start, finish, error, state update, and guardrail check is recorded with millisecond precision and actor tags.
- **Langfuse / OpenTelemetry (`output/langfuse_traces.json`)**:
  Spans track parent-child relationships, token counts, latency, and full provenance linking each source Java file to its translated Python target.
- **Live Traces Endpoint**:
  Access active traces at any time via [`http://localhost:8080/api/traces`](http://localhost:8080/api/traces).

---

## 9. ☁️ Cloud Deployment & Containerization

CodeShift is 100% deployment-ready:
- **`Dockerfile`**: Minimal Python 3.12 slim container packaging all dependencies, source code, and Uvicorn server.
- **`docker-compose.yml`**: Port 8080 mapping with automatic container restart policy.
- **`render.yaml`**: Standard 1-click cloud blueprint for Render Web Services.
- **Health Check Endpoint (`/health`)**: Returns JSON payload confirming service health, active frameworks (`Google-ADK`, `CrewAI`), and `A2A/1.0` status.
- **Deployment Guide**: Comprehensive step-by-step instructions in [`docs/DEPLOYMENT_GUIDE.md`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/docs/DEPLOYMENT_GUIDE.md).
