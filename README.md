# TestForge

An agentic test generation system for Python. Takes untested code, generates a passing pytest suite, and self-corrects until tests pass and coverage clears a target.

## Evaluation Results

Evaluated across 10 Python modules of varying complexity (pure functions, classes with state, data structures, recursive algorithms):

| Metric | Value |
|--------|-------|
| Success rate | 75% (6/8 completed runs) |
| Mean coverage on passing runs | 100% |
| First-try pass rate | 50% (no repair needed) |
| Self-correction rate | 25% (repair/regenerate recovered) |
| Mean iterations to pass | 1.8 |

| Difficulty | Passed | Mean Coverage |
|------------|--------|---------------|
| Easy | 1/2 | 100% |
| Medium | 3/4 | 75% |
| Hard | 2/4 | 50% |

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
```

The agent follows a **generate → run → decide** loop built as a LangGraph `StateGraph`:

1. **Generate** — LLM produces a pytest suite from AST-extracted metadata and source code
2. **Run** — executes tests in a sandboxed environment, measures coverage
3. **Decide** — if tests pass and coverage meets the target, stop. Otherwise:
   - **Repair** — feed failure tracebacks back to the LLM for targeted fixes
   - **Regenerate** — if stuck (same errors repeating), start fresh with a different approach

## Features

- **AST-based code analysis** — extracts functions, classes, signatures, async detection, raises
- **Self-correcting agent loop** — 3-mode adaptive strategy with stuck detection
- **Provider-agnostic LLM** — works with Gemini, OpenAI, HuggingFace, and more via litellm
- **Sandboxed execution** — Docker (network/memory/CPU isolation) or subprocess fallback
- **Structured observability** — per-iteration traces with structlog, run-level correlation via context vars
- **MLflow tracking** — params and metrics logged per run for experiment comparison
- **FastAPI service** — async job API with file upload support
- **Mutation testing** — verifies test quality by injecting bugs and measuring kill rate via mutmut
- **CI/CD** — GitHub Actions (lint + test), Docker containerization, Render deployment

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

# Start the API server
uvicorn testforge.api.app:app --reload
```

### Supported LLM providers

Set `MODEL_NAME` in `.env` with the litellm prefix:

```env
MODEL_NAME=gemini/gemini-2.5-flash       # Google
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

# Poll for results
curl http://localhost:8000/runs/{run_id}

# Interactive docs
open http://localhost:8000/docs
```

## Mutation testing

After generating tests, verify their quality by running mutation testing:

```bash
python run.py examples/calculator.py --mutate
```

This injects small bugs (mutants) into the source code and checks whether the generated tests catch them. A high kill rate means the tests are robust.

## Run the evaluation

```bash
python -m eval.run_eval
```

Runs the agent across 10 sample modules and reports aggregate stats (success rate, coverage, iterations). Each run is logged to MLflow.

## Tech stack

| Component | Technology |
|-----------|-----------|
| Agent orchestration | LangGraph StateGraph |
| LLM interface | litellm (multi-provider) |
| API | FastAPI |
| Test execution | pytest + coverage.py |
| Sandbox | Docker / subprocess |
| Mutation testing | mutmut |
| Observability | structlog (traces), MLflow (metrics) |
| CI/CD | GitHub Actions, Docker, Render |

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
