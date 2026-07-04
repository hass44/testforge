# TestForge — An Agentic Test Generation System for Python

## One-line pitch

Point it at untested Python code; it writes a real, passing pytest suite, verifying its own work by running the tests and measuring coverage, and iterating until the tests pass and coverage clears a target.

## Why this project (and why it is not generic)

Most portfolio LLM projects are "chat with your PDFs / codebase" — retrieval plus a chat box. They are generic because the data is trivial, the task is solved, and anyone can build one. This project is different on three axes:

1. **Real, felt pain.** Low test coverage is a universal problem. Teams actively want AI that writes meaningful tests. This solves something people would actually use.
2. **Objectively verifiable.** Success is not vibes. A run either produces tests that pass and raise coverage, or it does not. This makes it genuinely agentic (generate → run → read failures/coverage → improve) rather than a single LLM call dressed up.
3. **Showcases agentic engineering, not just prompting.** Planning, tool use (run tests, read coverage, read tracebacks), and self-correction from execution feedback — the exact competencies that Applied-AI/agentic-AI roles screen for.

## What it demonstrates (mapped to the job market)

This single artifact exercises the entire Applied-AI/LLM production stack that job descriptions repeatedly ask for:

| Capability | Where it shows up in the project | JD demand it answers |
|---|---|---|
| LLM application | Core test-generation engine | GenAI / LLM experience |
| Agent orchestration + tool use | LangGraph state machine: generate → run → measure → decide → repair | LangGraph/agent frameworks, "stateful agent orchestration" |
| RAG (light) | Retrieving relevant source context for large modules | "RAG systems", retrieval |
| Backend API | FastAPI service wrapping the agent | "FastAPI/Flask, microservices" |
| Containerization | Dockerized service + sandboxed test execution | "Docker, Kubernetes" |
| CI/CD | GitHub Actions: lint, test, build image | "CI/CD, MLOps pipelines" |
| Cloud deploy | Deployed on a cloud free tier | "AWS/Azure/GCP" |
| Eval / observability + experiment tracking | MLflow-tracked coverage metrics, run logging, eval-as-experiment harness | "RAG evaluation metrics, agent tracing, MLflow/experiment tracking" |

The point: build one thing, close the whole recurring gap cluster at once, and have a single linkable URL that proves it.

## Scope — explicit boundaries

**In scope (v1):**
- Language: Python only.
- Test framework target: pytest only.
- Granularity: one module/file at a time.
- Success oracle: generated tests run, pass against current code, and raise line coverage of the target module above a threshold (or by a delta).
- The agent loop: generate tests → run in sandbox → on failure/low coverage, read the traceback and coverage report → revise → repeat up to N iterations.

**Out of scope (v1) — stated as non-goals:**
- Languages other than Python.
- Test frameworks other than pytest.
- Whole-repo or cross-module generation in one shot.
- Proving tests are *meaningful* beyond coverage (mutation testing) — this is a **stretch goal**, not v1.
- Guaranteeing correctness of the code under test (we test behavior as-is, not spec conformance).

## Definition of done (v1)

Given a Python file with little or no test coverage, the system:
1. Produces a `test_<module>.py` file.
2. All generated tests pass against the current code.
3. Line coverage of the target module rises above the configured threshold (e.g. 70%) or by a configured delta.
4. The suite includes at least some non-trivial edge-case tests (not only happy-path / not-None checks).
5. The whole thing is callable via a FastAPI endpoint, runs in Docker, is built/tested by CI, and is deployed to a reachable cloud URL.

## The distinctive stretch goal (do only if v1 is solid)

**Mutation testing to prove the tests actually catch bugs.** Coverage proves lines were executed; it does not prove the tests would fail if the code broke. Running a mutation-testing tool (e.g. `mutmut` / `cosmic-ray`) against the generated suite and reporting the mutation kill rate would prove the tests are *meaningful*, not coverage-padding. Almost no portfolio project does this. It is the single highest-signal differentiator available here — it turns "I generated tests" into "I generated tests and proved they catch real bugs." Reserve it for after v1 ships.

## What success looks like as a portfolio artifact

- A public GitHub repo with a README that leads with a before/after: "module at 12% coverage → 84% coverage, 9 passing tests, 6/8 mutants killed," with the exact commands to reproduce.
- A short demo (screen recording or deployed link) showing the agent taking an untested module and producing a passing, coverage-raising suite, including a visible self-correction (a test fails, the agent reads the traceback, fixes it).
- A clear architecture diagram of the agent loop and the production stack.
- A short writeup (blog/LinkedIn) of one genuinely hard part (e.g. sandboxing untrusted generated code, or how the agent recovers from a failing test).

## Honest risks and how the plan manages them

| Risk | Mitigation |
|---|---|
| Scope creep ("write *perfect* tests") | Hard, modest definition of done: pass + coverage delta + some edge cases. Mutation testing is explicitly a stretch, not v1. |
| Running LLM-generated code is unsafe | Execute all generated tests in a locked-down sandbox (subprocess in a resource-limited Docker container, no network, timeout). This is itself a strong thing to show. |
| LLM API cost during iteration | Cap agent iterations (e.g. 4). Cache. Develop against a small model, demo against a stronger one. |
| Collides with thesis time | This is independent of the thesis (different domain, off-the-shelf models). Built in self-contained weekend chunks. Ships even if only v1. |
| "Another code agent" perception | The relevance (real pain), the verification loop, and especially mutation testing make it concretely useful and measurably honest, not a toy. |

## Relationship to other goals

- **Directly relevant to the KLA/Pavel agentic-AI lead** — this is a working, verifiable agentic system you can point to.
- **Thesis-adjacent but separate** — uses off-the-shelf models on a different task (test generation, not code generation comparison), so it does not touch thesis novelty.
- **Interview-ready** — every layer (sandboxing, the agent loop, self-correction, mutation testing) is a concrete story for "tell me about something hard you built."
