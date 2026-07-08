# TestForge

An agentic test generation system for Python. Takes untested code, generates a passing pytest suite, and self-corrects until tests pass and coverage clears a target — then optionally verifies test quality via mutation testing.

## How it works

```
source file → AST analysis → generate tests → run pytest + coverage
                                                        │
                                         ┌──────────────┤
                                         │              │
                                  repair (feedback)  regenerate (fresh)
                                         │              │
                                         └──── run ◄────┘
                                                │
                                         pass + coverage ≥ target → done
                                                │
                                         [optional] mutation testing
```

The agent follows a **generate → run → decide** loop built as a LangGraph `StateGraph`:

1. **Analyze** — AST-based extraction of functions, classes, signatures, decorators, and raised exceptions from the target file
2. **Generate** — LLM produces a pytest suite from the extracted metadata and source code
3. **Run** — executes tests in a sandboxed environment (Docker or subprocess), measures line coverage
4. **Decide** — if tests pass and coverage meets the target, stop. Otherwise:
   - **Repair** — feed failure tracebacks back to the LLM for targeted fixes
   - **Regenerate** — if stuck (same errors repeating), start fresh with a different approach
5. **Mutate** (optional) — inject bugs into the source via mutmut to verify generated tests actually catch regressions

## Features

- **AST-based code analysis** — extracts functions, classes, signatures, decorators, async detection, raised exceptions
- **Self-correcting agent loop** — 3-mode adaptive strategy (generate / repair / regenerate) with stuck detection
- **Provider-agnostic LLM** — works with Gemini, OpenAI, HuggingFace, and 100+ providers via litellm
- **Sandboxed execution** — Docker (network/memory/CPU isolation) or subprocess fallback
- **Mutation testing** — verifies test quality by injecting bugs and measuring kill rate via mutmut
- **Structured observability** — per-iteration JSON traces with structlog, run-level correlation via context vars
- **MLflow experiment tracking** — params and metrics logged per run for experiment comparison
- **FastAPI service** — async job API with JSON and file upload endpoints
- **Evaluation harness** — automated benchmarking across 16 Python modules at 3 difficulty tiers
- **CI/CD** — GitHub Actions (lint + test), Docker containerization, Render deployment

## Evaluation Results

Evaluated across 16 Python modules of varying complexity — pure functions, classes with state, data structures, recursive algorithms, and real-world code from production ML projects:

| Metric | Value |
|--------|-------|
| Eval modules | 16 (4 easy, 6 medium, 6 hard) |
| Mean coverage on passing runs | 100% |
| Self-correction rate | 25% (repair/regenerate recovered failing runs) |
| Mean iterations to pass | 1.8 |

| Difficulty | Sample types |
|------------|-------------|
| Easy | Pure functions, string manipulation, AST filters, code extraction |
| Medium | Stateful classes (stack, cache, validator), statistical metrics, structural analysis |
| Hard | Linked lists, matrix ops, rate limiters, JSON flattening, transformer FLOPs, sandbox systems |

Eval modules include code extracted from real projects: AST validity filtering, pass@k computation, phi-correlation metrics, bracket/indentation analysis, transformer FLOP budgets, and agent sandboxes.

### Mutation testing

Generated tests verified via mutation testing (mutmut). Example on `calculator.py`:

```
  Mutants killed:    13
  Mutants survived:  1
  Total mutants:     14
  Kill rate:         92.9%
```

## Quick start

```bash
git clone https://github.com/hass44/testforge.git
cd testforge
pip install -e .

# Configure your LLM provider (see .env.example)
cp .env.example .env
# Edit .env with your API key

# Generate tests for a Python file
python run.py examples/calculator.py

# Generate tests + run mutation testing
python run.py examples/calculator.py --mutate

# Start the API server
uvicorn testforge.api.app:app --reload
```

### Supported LLM providers

Set `MODEL_NAME` in `.env` with the litellm prefix:

```env
MODEL_NAME=gemini/gemini-2.5-flash       # Google (free tier available)
MODEL_NAME=gpt-4o                        # OpenAI
MODEL_NAME=huggingface/Qwen/Qwen3-Coder  # HuggingFace
# See litellm docs for 100+ supported providers
```

## API

```bash
# Submit a test generation job
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"source_code": "def add(a, b): return a + b"}'

# Upload a Python file directly
curl -X POST http://localhost:8000/generate/upload \
  -F "file=@mymodule.py"

# Poll for results
curl http://localhost:8000/runs/{run_id}

# Interactive docs
open http://localhost:8000/docs
```

## Run the evaluation

```bash
python -m eval.run_eval
```

Runs the agent across 16 sample modules and reports aggregate stats (success rate, coverage, iterations, duration). Each run is logged to MLflow.

## Tech stack

| Component | Technology |
|-----------|-----------|
| Agent orchestration | LangGraph StateGraph |
| LLM interface | litellm (multi-provider) |
| Code analysis | ast (stdlib) |
| API | FastAPI |
| Test execution | pytest + coverage.py |
| Sandbox | Docker / subprocess |
| Mutation testing | mutmut |
| Observability | structlog (JSON traces), MLflow (experiment tracking) |
| CI/CD | GitHub Actions, Docker, Render |

## Project structure

```
testforge/
├── agent/          # LangGraph state machine (nodes, graph, state)
├── analyzer/       # AST-based code analysis
├── tools/          # pytest runner, coverage, mutation testing
├── prompts/        # LLM prompt templates
├── sandbox/        # Docker and subprocess execution
├── api/            # FastAPI service + job store
├── observability/  # structlog + MLflow integration
eval/
├── run_eval.py     # Evaluation harness
├── samples/        # 16 benchmark modules (easy/medium/hard)
examples/           # Sample target files
tests/              # Unit tests
```

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
