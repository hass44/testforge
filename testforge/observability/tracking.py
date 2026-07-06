"""
MLflow tracking for TestForge agent runs.

Logs params (inputs) and metrics (outcomes) for each agent run,
enabling comparison across files, models, and prompt strategies.

Data stored locally in ./mlruns by default — no server required.
"""
import os
from typing import Any

import mlflow

from testforge.observability.logging import get_logger

log = get_logger("testforge.tracking")

EXPERIMENT_NAME = "testforge-runs"


def _ensure_experiment() -> str:
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        return mlflow.create_experiment(EXPERIMENT_NAME)
    return experiment.experiment_id


def track_run(
    run_id: str,
    file_path: str,
    final_state: dict[str, Any],
    max_iterations: int,
    coverage_target: float,
    total_duration_s: float,
) -> None:
    """Log a completed agent run to MLflow."""
    experiment_id = _ensure_experiment()
    result = final_state.get("test_result", {})

    with mlflow.start_run(experiment_id=experiment_id, run_name=run_id):
        mlflow.set_tag("run_id", run_id)

        mlflow.log_params({
            "file_path": file_path,
            "model_name": os.getenv("MODEL_NAME", "unknown"),
            "max_iterations": max_iterations,
            "coverage_target": coverage_target,
        })

        mlflow.log_metrics({
            "final_coverage": result.get("coverage_pct", 0.0),
            "iterations_used": final_state.get("iteration", 0),
            "num_passed": result.get("num_passed", 0),
            "num_failed": result.get("num_failed", 0),
            "num_errors": result.get("num_errors", 0),
            "success": 1.0 if final_state.get("status") == "passed" else 0.0,
            "total_duration_s": total_duration_s,
        })

    log.info("mlflow_logged", mlflow_experiment=EXPERIMENT_NAME, run_id=run_id)
