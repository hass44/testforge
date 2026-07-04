# TestForge — Architecture

## High-level flow

```
User / API request
   │  (Python source file or module path)
   ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI service                                         │
│   - POST /generate  { source_code | file }               │
│   - GET  /runs/{id}  (status, results, artifacts)        │
└───────────────┬─────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│  Agent Orchestrator (LangGraph StateGraph)               │
│                                                          │
│   nodes operate on shared state:                         │
│   { source, analysis, tests, coverage, traceback, iter } │
│                                                          │
│   1. ANALYZE   parse source, extract functions/classes,  │
│                signatures, docstrings, branches          │
│   2. CONTEXT   (RAG-light) for large modules, retrieve   │
│                only the relevant code chunks             │
│   3. GENERATE  LLM writes a pytest test file (node)      │
│   4. RUN       execute tests in sandbox (tool)           │
│   5. MEASURE   read pass/fail + coverage report (tool)   │
│   6. DECIDE    conditional edge: pass & coverage OK?      │
│                ──► END   else ──► REPAIR                  │
│   7. REPAIR    LLM revises tests  ──► edge back to RUN    │
│                (iteration cap guards the edge)            │
└───────────────┬─────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│  Sandboxed Execution Environment                         │
│   - resource-limited Docker container / subprocess       │
│   - no network, CPU + memory + wall-clock limits         │
│   - returns: stdout, stderr, exit code, coverage XML/JSON │
└─────────────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│  Eval + Observability                                    │
│   - per-run log (each iteration, prompts, tool outputs)  │
│   - metrics: final coverage, #tests, #iterations, pass%  │
│   - STRETCH: mutation testing → mutant kill rate         │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. FastAPI service
Thin API layer. Two core endpoints: submit a generation job, poll its status/results. Async job handling (a job runs the agent loop, which takes time). Keep it stateless where possible; store run artifacts (generated tests, logs, metrics) keyed by run id.

### 2. Agent orchestrator
The brain. Implemented as a **LangGraph `StateGraph`** to demonstrate the stateful-agent-orchestration fluency the JDs ask for. LangGraph is chosen over LangChain's legacy agent abstractions because TestForge's loop *is* a cyclic state machine (generate → run → measure → decide → repair → back to run), which maps directly onto LangGraph nodes and conditional edges. Responsibilities:
- Static analysis of the target (Python `ast` module): enumerate functions/classes, signatures, branches, raise points, so the prompt is grounded in real structure rather than the raw blob.
- Prompt construction for test generation (a node).
- The iterate loop expressed as graph edges, with a hard iteration cap as an edge guard.
- Decision logic on the stopping condition (pass + coverage threshold) expressed as a conditional edge.

Graph state is a typed dict carrying `{source, analysis, tests, coverage, traceback, iteration}` between nodes. The node bodies hold the real logic; LangGraph supplies only the wiring and the loop control.

### 3. Tools (what makes it a real agent)
The agent calls tools, it does not just emit text:
- `run_tests(test_code, source)` → executes in the sandbox, returns structured results.
- `get_coverage()` → returns line coverage + which lines are uncovered.
- `read_traceback()` → structured failure info for the repair step.
- (stretch) `run_mutation(suite, source)` → mutant kill rate.

### 4. Sandbox
Security-critical and a strong thing to show. Generated code is untrusted. Run it in a constrained Docker container (or at minimum a subprocess with `resource` limits): no network, memory cap, CPU cap, wall-clock timeout, ephemeral filesystem. The README should call this out explicitly — sandboxing untrusted LLM-generated code is exactly the kind of production-mindedness that separates a serious project from a notebook.

### 5. Eval + observability
- Structured logging of every iteration: the prompt, the generated tests, the tool outputs, the decision. This is your "agent tracing" story (a literal JD bullet from DHL).
- Run-level metrics tracked in **MLflow**: each TestForge run is logged as an MLflow run with params (model, coverage threshold, iteration cap) and metrics (starting vs final coverage, test count, iterations used, pass rate). The MLflow UI gives a per-run dashboard for free.
- An eval harness built as an **MLflow experiment**: run the agent across a fixed set of sample modules — one MLflow run per module — and use MLflow's comparison view to report aggregate stats (mean coverage achieved, mean iterations, success rate). This turns "it works on my one demo file" into "here are tracked, reproducible results across 20 modules," which is far more credible and supplies the experiment-tracking / MLOps keyword. (Scope note: MLflow is used for experiment tracking and metrics only — not model registry or serving, which TestForge does not need.)

## Model strategy
- Develop and debug against a small/cheap model (fast, cheap iteration).
- Demo and report final numbers against a stronger model (e.g. a capable code model via API or a local 7B).
- Make the model swappable via config — also a nice thing to show (provider-agnostic design).

## Tech stack (explicit, mapped to JD keywords)
- **Language:** Python.
- **LLM orchestration:** LangGraph (stateful agent graph).
- **API:** FastAPI.
- **Static analysis:** `ast`, `coverage.py`, `pytest`.
- **Sandbox:** Docker (resource-limited), or `subprocess` + `resource` limits as a fallback.
- **Containerization:** Docker.
- **CI/CD:** GitHub Actions (lint with ruff, run the project's own tests, build the image).
- **Cloud:** deploy to a free tier (Fly.io, Render, GCP Cloud Run, or AWS — pick the simplest).
- **Eval / experiment tracking:** `MLflow` (experiment per eval, run per module) + `coverage.py`; stretch `mutmut`/`cosmic-ray`.
- **Observability:** structured logs (stdlib logging or `structlog`) for per-iteration traces; `MLflow` for run-level params/metrics. (Optional: LangSmith or MLflow tracing for richer LangGraph span capture.)

## Repo structure
```
testforge/
├── README.md                  # leads with before/after results + reproduce steps
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEMO.md
├── testforge/
│   ├── api/                   # FastAPI app
│   ├── agent/                 # LangGraph graph, nodes, prompts, state
│   ├── tools/                 # run_tests, coverage, traceback, (mutation)
│   ├── sandbox/               # sandboxed execution
│   ├── analysis/              # ast-based source analysis
│   └── eval/                  # eval harness + sample modules
├── tests/                     # the project's OWN tests (yes, dogfood it)
├── examples/                  # sample untested modules + generated results
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
└── pyproject.toml
```

Note: the project should have its own real test suite (dogfooding). A test-generation tool with no tests of its own is a bad look; a well-tested one reinforces the whole theme.
