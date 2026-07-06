"""
FastAPI service for TestForge.

POST /generate   — submit a test generation job (returns run_id immediately)
GET  /runs/{id}  — poll job status and results
GET  /health     — health check
"""
import asyncio
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from testforge.agent.graph import run_agent
from testforge.api.store import complete_run, create_run, fail_run, get_run

app = FastAPI(
    title="TestForge",
    description=(
        "Agentic test generation for Python"
    ),
    version="0.1.0",
)


# ── Request / response models ──────────────────────────────────

class GenerateRequest(BaseModel):
    source_code: str = Field(
        ..., description="Python source code to test"
    )
    file_name: str = Field(
        default="module.py", description="Source filename"
    )
    coverage_target: float = Field(default=80.0, ge=0, le=100)
    max_iterations: int = Field(default=4, ge=1, le=10)


class GenerateResponse(BaseModel):
    run_id: str


class RunStatus(BaseModel):
    run_id: str
    status: str
    file_path: str
    result: dict[str, Any] | None = None
    error_msg: str | None = None


# ── Background task runner ──────────────────────────────────────

async def _run_agent_background(
    run_id: str,
    file_path: str,
    project_root: str,
    coverage_target: float,
    max_iterations: int,
) -> None:
    """Run the agent in a thread (it's sync/blocking) and update the store."""
    try:
        final_state = await asyncio.to_thread(
            run_agent,
            file_path=file_path,
            max_iterations=max_iterations,
            coverage_target=coverage_target,
            project_root=project_root,
        )
        complete_run(run_id, final_state)
    except Exception as e:
        fail_run(run_id, str(e))


# ── Endpoints ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_from_json(req: GenerateRequest):
    """
    Submit source code as JSON. The agent runs in the background.
    Returns a run_id to poll with GET /runs/{run_id}.
    """
    tmp_dir = tempfile.mkdtemp(prefix="testforge_")
    file_path = Path(tmp_dir) / req.file_name
    file_path.write_text(req.source_code, encoding="utf-8")

    run_id = create_run(str(file_path))

    asyncio.create_task(
        _run_agent_background(
            run_id=run_id,
            file_path=str(file_path),
            project_root=tmp_dir,
            coverage_target=req.coverage_target,
            max_iterations=req.max_iterations,
        )
    )

    return GenerateResponse(run_id=run_id)


@app.post("/generate/upload", response_model=GenerateResponse)
async def generate_from_upload(
    file: UploadFile = File(...),
    coverage_target: float = 80.0,
    max_iterations: int = 4,
):
    """
    Upload a Python file. The agent runs in the background.
    Returns a run_id to poll with GET /runs/{run_id}.
    """
    content = await file.read()
    source_code = content.decode("utf-8")

    tmp_dir = tempfile.mkdtemp(prefix="testforge_")
    file_name = file.filename or "module.py"
    file_path = Path(tmp_dir) / file_name
    file_path.write_text(source_code, encoding="utf-8")

    run_id = create_run(str(file_path))

    asyncio.create_task(
        _run_agent_background(
            run_id=run_id,
            file_path=str(file_path),
            project_root=tmp_dir,
            coverage_target=coverage_target,
            max_iterations=max_iterations,
        )
    )

    return GenerateResponse(run_id=run_id)


@app.get("/runs/{run_id}", response_model=RunStatus)
def get_run_status(run_id: str):
    """Poll the status of a generation run."""
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")
    return RunStatus(
        run_id=run_id,
        status=run["status"],
        file_path=run["file_path"],
        result=run.get("result"),
        error_msg=run.get("error_msg"),
    )
