# TestForge — Build Plan (weekend-by-weekend)

Designed to survive alongside the thesis. Each weekend is a self-contained, shippable increment. If you stop after Weekend 4, you still have a working, demoable, deployed project. Everything after is strengthening.

## Guiding rule
**Ship a working vertical slice early, then deepen.** Do not build all components to completion before connecting them. Get a crude end-to-end loop working in Weekend 2, then improve each piece. A working ugly thing beats a beautiful half-thing.

---

## Weekend 1 — Single-pass pipeline, no agent framework, no API
**Goal:** prove every piece works once, end to end — without a loop yet.
- Set up repo, `pyproject.toml`, ruff, the project's own test scaffold.
- Write `analysis/`: use `ast` to extract functions/classes/signatures from a target file.
- Write a single LLM call that, given a source file, returns a pytest test file.
- Write `tools/run_tests`: run the generated tests with `pytest` + `coverage.py` in a **subprocess** (sandbox hardening comes later), capture pass/fail + coverage.
- Wire a **single pass** in a plain script: analyze → generate → run → measure. Print pass/fail + coverage. No repair, no iteration yet — that is Weekend 2's job, and it is deliberately deferred so the loop is built *inside* the agent framework, not thrown away.
- **End of weekend:** `python run.py somefile.py` analyzes a file, generates a test file, runs it, and reports coverage. One pass, no self-correction. Ugly but real.

## Weekend 2 — Make it a LangGraph agent + FastAPI
**Goal:** real agent framework + an API. This is the JD-keyword weekend, and the weekend the iterate-loop is born.
- Build the agent as a **LangGraph `StateGraph`**. The graph state carries `{source, analysis, tests, coverage, traceback, iteration}`. Model your steps as nodes — `generate`, `run`, `measure`, `repair` — and the stopping/repair decision as a **conditional edge** (pass + coverage OK → `END`; else → `repair` → back to `run`), with the iteration cap as a guard on that edge.
- **Learning note (Rule 2/6):** the graph *wiring* is framework boilerplate, but the **node bodies are the learning core — you write them.** Each node is a plain function that takes state and returns state; that is where the generate prompt, the run-and-parse, the decision logic actually live. I scaffold the `StateGraph` skeleton and explain `add_node` / `add_conditional_edges`; you fill the nodes.
- Expose the tools (`run_tests`, `get_coverage`, `read_traceback`) as the operations the nodes call.
- Wrap it in FastAPI: `POST /generate`, `GET /runs/{id}`, async job execution.
- Store run artifacts (generated tests, logs, metrics) on disk keyed by run id.
- **End of weekend:** hit the API with a file, poll, get back a passing test suite + coverage numbers, produced by a stateful LangGraph loop that decides for itself when to stop.

## Weekend 3 — Sandbox + observability
**Goal:** production-mindedness signals.
- Move test execution into a locked-down **Docker** sandbox: no network, memory/CPU/wall-clock limits, ephemeral FS. (Fallback: `subprocess` + `resource` limits if Docker-in-the-loop is fiddly.)
- Add structured per-iteration logging (prompts, tool outputs, decisions) — your "agent tracing" story.
- Add **MLflow** run tracking: log each TestForge run as an MLflow run with params (model, coverage threshold, iteration cap) and metrics (start vs final coverage, #tests, #iterations, pass rate). The MLflow UI gives you a free per-run dashboard.
- **End of weekend:** untrusted generated code runs safely; every run produces a readable trace plus an MLflow-tracked record of its metrics.

## Weekend 4 — Containerize, CI/CD, deploy
**Goal:** close the MLOps/cloud gap; get a public URL.
- `Dockerfile` + `docker-compose.yml` for the whole service.
- GitHub Actions: lint (ruff), run the project's own tests, build the image. (Optionally push to a registry.)
- Deploy to a free tier (Fly.io / Render / Cloud Run — pick the least painful). Get a reachable URL.
- **End of weekend:** a live, deployed, containerized, CI-backed service. This is the minimum "complete" project. Everything below is differentiation.

## Weekend 5 — Eval harness + the README that sells it
**Goal:** credibility through numbers + a recruiter-legible front page.
- Build `eval/`: a fixed set of ~15–20 untested sample modules (varying difficulty). Run the agent across all as a single **MLflow experiment** — one MLflow run per module — then use the MLflow comparison UI to report aggregate stats: mean coverage achieved, mean iterations, success rate. This is the "MLOps pipeline / experiment tracking" keyword, and it turns the eval from a hand-rolled CSV into a reproducible, comparable record.
- Write the README to lead with results: a concrete before/after table + the exact reproduce commands + architecture diagram + the live URL.
- Record a 60–90s demo showing a real run, including a visible self-correction (test fails → agent reads traceback → fixes).
- **End of weekend:** the project *looks* as good as it is. This weekend is what makes it land in a 30-second recruiter skim.

## Weekend 6 (STRETCH) — Mutation testing, the differentiator
**Goal:** prove the tests are meaningful, not coverage-padding.
- Integrate `mutmut` or `cosmic-ray`: after generating a suite, mutate the source and measure the kill rate.
- Optionally feed surviving mutants back to the agent ("these bugs weren't caught — strengthen the tests"). This is a genuinely impressive second-order agent loop.
- Report mutation kill rate alongside coverage in the README and eval.
- **End of weekend:** you can say "my agent writes tests that catch X% of injected bugs," which almost no portfolio project can claim.

---

## What ships at each stopping point
- **After W2:** working agent + API (local). Demoable.
- **After W4:** deployed, containerized, CI/CD'd public service. *Genuinely complete; safe to put on the CV here.*
- **After W5:** credible (eval numbers) and legible (README/demo). *This is the target.*
- **After W6:** distinctive (mutation testing). *This is what makes it memorable.*

## Time-honesty note
At ~one weekend chunk per week alongside the thesis, this is roughly a 5–6 week project to the strong version (W5), 6–7 to the standout version (W6). If thesis crunch eats a weekend, the increments are independent enough to pause and resume without losing work. Protect W1–W4 (they produce the shippable core); W5–W6 are where you stop if time runs out, but they are also what separate it from generic, so reach them if you can.

## First concrete action (this week, ~1 hour)
Create the repo, set up `pyproject.toml` + ruff + an empty `tests/`, and write the `ast` analyzer that lists functions in a file. Smallest possible real start. Momentum beats planning.
