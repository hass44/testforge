# TestForge

An agentic test generation system for Python. Takes untested code, generates a passing pytest suite, and iterates until tests pass and coverage clears a target.

## Features

- **AST-based code analysis** — extracts functions, classes, signatures, raises
- **Self-correcting agent loop** — generate, run, measure, decide, repair
- **3-mode adaptive strategy** — generate, repair, and regenerate with stuck detection
- **Sandboxed execution** — Docker isolation or subprocess fallback
- **Structured observability** — per-iteration traces with run-level correlation
- **MLflow tracking** — params and metrics logged per run
- **FastAPI service** — async job API with file upload support

## Quick start

```bash
git clone https://github.com/hass44/testforge.git
cd testforge
pip install -e .

# Set your HuggingFace token
echo "HF_TOKEN=your_token_here" > .env

# Generate tests for a Python file
python run.py examples/calculator.py

# Start the API server
uvicorn testforge.api.app:app --reload
```

## API

```bash
# Submit a test generation job
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"source_code": "def add(a, b): return a + b"}'

# Poll for results
curl http://localhost:8000/runs/{run_id}
```

## Architecture

```
analyze → generate → run → measure → decide
                                        │
                         ┌──────────────┤
                         │              │
                       repair      regenerate
                         │              │
                         └──── run ◄────┘
```

**Stack:** Python, LangGraph, FastAPI, pytest, coverage.py, structlog, MLflow, Docker

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
