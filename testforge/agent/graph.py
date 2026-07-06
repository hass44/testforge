"""
TestForge agent graph — the self-correcting test generation loop.

Graph structure:
    generate → run → decide ──(done)──► END
                       │
                       ├──(repair)──► repair → run → decide → ...
                       │
                       └──(regenerate)──► regenerate → run → decide → ...
"""
from pathlib import Path
from typing import Any

import structlog
from langgraph.graph import END, StateGraph

from testforge.agent.nodes import (
    decide,
    generate_node,
    regenerate_node,
    repair_node,
    run_node,
)
from testforge.agent.state import AgentState
from testforge.analysis.analyzer import analyze_file
from testforge.analysis.prompt_context import file_to_import_path
from testforge.observability.logging import AgentTimer, get_logger, new_run_id
from testforge.observability.tracking import track_run

log = get_logger("testforge.agent.graph")


def build_graph() -> StateGraph:
    """
    Construct the LangGraph StateGraph. Call .compile() on the result
    to get a runnable graph.
    """

    # 1. Create the graph with our state schema.
    #    StateGraph knows the shape of AgentState and will validate
    #    that nodes return dicts matching those fields.
    graph = StateGraph(AgentState)

    # 2. Register each node — a name + a function.
    #    The name is how we refer to it in edges.
    #    The function signature is: (state: AgentState) -> dict
    graph.add_node("generate", generate_node)
    graph.add_node("run", run_node)
    graph.add_node("repair", repair_node)
    graph.add_node("regenerate", regenerate_node)

    # 3. Set the entry point — which node runs first.
    graph.set_entry_point("generate")

    # 4. Add fixed edges — "after node X, always go to node Y."
    #    After generating tests (any mode), always run them.
    graph.add_edge("generate", "run")
    graph.add_edge("repair", "run")
    graph.add_edge("regenerate", "run")

    # 5. Add the conditional edge — the decision point.
    #    After "run", call the `decide` function.
    #    `decide` returns a string: "done", "repair", or "regenerate".
    #    The dict maps those strings to node names (or END).
    graph.add_conditional_edges(
        "run",
        decide,
        {
            "done": END,
            "repair": "repair",
            "regenerate": "regenerate",
        },
    )

    return graph


def compile_graph():
    """Build and compile the graph into a runnable."""
    return build_graph().compile()


def run_agent(
    file_path: str,
    max_iterations: int = 4,
    coverage_target: float = 80.0,
    project_root: str | None = None,
) -> dict[str, Any]:
    """
    Run the full TestForge agent on a Python file.

    This is the main entry point — it:
    1. Analyzes the file
    2. Prepares the initial state
    3. Runs the LangGraph agent loop
    4. Returns the final state with results

    project_root: if set, import path is computed relative to this dir.
                  Used by the API when files are in a temp directory.
    """
    run_id = new_run_id()
    structlog.contextvars.bind_contextvars(run_id=run_id)

    log.info("run_start", file_path=file_path, max_iterations=max_iterations,
             coverage_target=coverage_target)

    source_code = open(file_path, encoding="utf-8").read()
    metadata = analyze_file(file_path)
    import_path = file_to_import_path(file_path, project_root=project_root)

    initial_state: AgentState = {
        "source_code": source_code,
        "metadata": metadata,
        "import_path": import_path,
        "file_path": file_path,
        "project_root": project_root or str(Path.cwd()),
        "max_iterations": max_iterations,
        "coverage_target": coverage_target,
        "test_code": "",
        "test_result": {},
        "iteration": 0,
        "strategy": "generate",
        "history": [],
        "status": "running",
    }

    app = compile_graph()

    with AgentTimer() as timer:
        final_state = app.invoke(initial_state)

    result = final_state.get("test_result", {})
    if result.get("passed") and result.get("coverage_pct", 0) >= coverage_target:
        final_state["status"] = "passed"
    else:
        final_state["status"] = "failed"

    log.info("run_end",
             status=final_state["status"],
             total_iterations=final_state.get("iteration", 0),
             final_coverage=result.get("coverage_pct", 0),
             total_duration_s=timer.elapsed)

    track_run(
        run_id=run_id,
        file_path=file_path,
        final_state=final_state,
        max_iterations=max_iterations,
        coverage_target=coverage_target,
        total_duration_s=timer.elapsed,
    )

    structlog.contextvars.unbind_contextvars("run_id")
    return final_state
