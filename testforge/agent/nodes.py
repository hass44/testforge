import os
from typing import Any

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from testforge.agent.prompts import (
    SYSTEM_GENERATE,
    SYSTEM_REGENERATE,
    SYSTEM_REPAIR,
    build_generate_prompt,
    build_regenerate_prompt,
    build_repair_prompt,
)
from testforge.agent.state import AgentState
from testforge.analysis.prompt_context import build_context
from testforge.observability.logging import AgentTimer, get_logger
from testforge.sandbox import execute_tests

load_dotenv()

log = get_logger("testforge.agent")


def _call_llm(system: str, user: str) -> str:
    """Shared LLM call used by all nodes. Returns raw text, fences stripped."""
    import re

    model = os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-30B-A3B-Instruct")
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN not set — add it to your .env file")

    client = InferenceClient(token=token)

    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            max_tokens=4096,
        )
    except HfHubHTTPError as e:
        raise RuntimeError(
            f"HuggingFace API error for model {model!r}. "
            f"Try a different MODEL_NAME in .env.\n"
            f"Original error: {e}"
        ) from e

    raw = response.choices[0].message.content
    raw = raw.strip()
    raw = re.sub(r"^```(?:python)?\s*\n", "", raw)
    raw = re.sub(r"\n```\s*$", "", raw)
    return raw.strip()


# ── Node: generate ──────────────────────────────────────────────

def generate_node(state: AgentState) -> dict[str, Any]:
    """First iteration: generate tests from scratch."""
    test_targets = build_context(
        state["metadata"],
        mode="full_source",
        import_path=state["import_path"],
    )
    prompt = build_generate_prompt(test_targets, state["source_code"])

    log.info("llm_call_start", node="generate", iteration=state.get("iteration", 0))
    with AgentTimer() as timer:
        test_code = _call_llm(SYSTEM_GENERATE, prompt)
    log.info("llm_call_end", node="generate", duration_s=timer.elapsed,
             output_len=len(test_code))

    return {"test_code": test_code, "strategy": "generate"}


# ── Node: run ───────────────────────────────────────────────────

def run_node(state: AgentState) -> dict[str, Any]:
    """Run the current tests and measure coverage."""
    iteration = state.get("iteration", 0)
    log.info("test_run_start", iteration=iteration)

    with AgentTimer() as timer:
        result = execute_tests(
            test_code=state["test_code"],
            source_file=state["file_path"],
            source_code=state["source_code"],
            project_root=state.get("project_root"),
        )

    log.info("test_run_end",
             iteration=iteration,
             duration_s=timer.elapsed,
             passed=result["passed"],
             num_passed=result["num_passed"],
             num_failed=result["num_failed"],
             num_errors=result["num_errors"],
             coverage_pct=result["coverage_pct"])

    new_history = list(state.get("history", []))
    new_history.append({
        "iteration": iteration,
        "test_result": result,
    })

    return {
        "test_result": result,
        "iteration": iteration + 1,
        "history": new_history,
    }


# ── Node: repair ───────────────────────────────────────────────

def repair_node(state: AgentState) -> dict[str, Any]:
    """Fix tests based on failure feedback."""
    test_targets = build_context(
        state["metadata"],
        mode="full_source",
        import_path=state["import_path"],
    )
    prompt = build_repair_prompt(
        test_code=state["test_code"],
        test_result=state["test_result"],
        source_code=state["source_code"],
        test_targets=test_targets,
    )

    log.info("llm_call_start", node="repair", iteration=state.get("iteration", 0))
    with AgentTimer() as timer:
        test_code = _call_llm(SYSTEM_REPAIR, prompt)
    log.info("llm_call_end", node="repair", duration_s=timer.elapsed,
             output_len=len(test_code))

    return {"test_code": test_code, "strategy": "repair"}


# ── Node: regenerate ───────────────────────────────────────────

def regenerate_node(state: AgentState) -> dict[str, Any]:
    """Start fresh when the model is stuck."""
    test_targets = build_context(
        state["metadata"],
        mode="full_source",
        import_path=state["import_path"],
    )
    prompt = build_regenerate_prompt(
        test_result=state["test_result"],
        source_code=state["source_code"],
        test_targets=test_targets,
    )

    log.info("llm_call_start", node="regenerate", iteration=state.get("iteration", 0))
    with AgentTimer() as timer:
        test_code = _call_llm(SYSTEM_REGENERATE, prompt)
    log.info("llm_call_end", node="regenerate", duration_s=timer.elapsed,
             output_len=len(test_code))

    return {"test_code": test_code, "strategy": "regenerate"}


# ── Conditional edge: decide ────────────────────────────────────

def decide(state: AgentState) -> str:
    """
    Returns the name of the next node:
      "done"       → END
      "repair"     → repair_node
      "regenerate" → regenerate_node
    """
    result = state["test_result"]
    iteration = state["iteration"]
    max_iter = state.get("max_iterations", 4)
    target = state.get("coverage_target", 80.0)

    if result["passed"] and result["coverage_pct"] >= target:
        log.info("decide", decision="done", reason="target_met",
                 iteration=iteration, coverage_pct=result["coverage_pct"])
        return "done"

    if iteration >= max_iter:
        log.info("decide", decision="done", reason="max_iterations",
                 iteration=iteration, coverage_pct=result["coverage_pct"])
        return "done"

    if _is_stuck(state):
        log.info("decide", decision="regenerate", reason="stuck_detected",
                 iteration=iteration)
        return "regenerate"

    log.info("decide", decision="repair", iteration=iteration)
    return "repair"


def _is_stuck(state: AgentState) -> bool:
    """Detect if the model is repeating the same errors."""
    history = state.get("history", [])
    if len(history) < 2:
        return False

    current = history[-1]["test_result"]
    previous = history[-2]["test_result"]

    if not current.get("traceback") or not previous.get("traceback"):
        return False

    current_errors = _extract_error_signatures(current["traceback"])
    previous_errors = _extract_error_signatures(previous["traceback"])

    return current_errors == previous_errors and len(current_errors) > 0


def _extract_error_signatures(traceback: str) -> set[str]:
    """Pull error type + test name pairs from traceback text."""
    import re

    signatures = set()
    for match in re.finditer(r"FAILED\s+\S*::(\w+)\s*-\s*(\w+)", traceback):
        test_name, error_type = match.groups()
        signatures.add(f"{test_name}:{error_type}")

    for match in re.finditer(r"([\w.]+Error|[\w.]+Exception)", traceback):
        signatures.add(match.group(1))

    return signatures
