"""
TestForge — agentic test generation pipeline.
Uses LangGraph to run a self-correcting generate → run → repair loop.
"""
import sys
from pathlib import Path

from testforge.agent.graph import run_agent


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <path-to-python-file> [coverage-target] [max-iterations]")
        sys.exit(1)

    target = sys.argv[1]
    if not Path(target).exists():
        print(f"File not found: {target}")
        sys.exit(1)

    coverage_target = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
    max_iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    print(f"TestForge: generating tests for {target}")
    print(f"  Coverage target: {coverage_target}%")
    print(f"  Max iterations:  {max_iterations}")
    print()

    final_state = run_agent(
        file_path=target,
        max_iterations=max_iterations,
        coverage_target=coverage_target,
    )

    result = final_state["test_result"]
    iteration = final_state["iteration"]
    strategy = final_state["strategy"]

    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"  Iterations used: {iteration}")
    print(f"  Final strategy:  {strategy}")
    print(f"  Tests passed:    {result.get('num_passed', 0)}")
    print(f"  Tests failed:    {result.get('num_failed', 0)}")
    print(f"  Errors:          {result.get('num_errors', 0)}")
    print(f"  Coverage:        {result.get('coverage_pct', 0)}%")

    if result.get("uncovered_lines"):
        print(f"  Uncovered lines: {result['uncovered_lines']}")

    if result.get("traceback"):
        print(f"\n--- Failures ---\n{result['traceback']}")

    status = final_state["status"]
    print(f"\n  Status: {status.upper()}")

    if status == "passed":
        out_name = f"test_{Path(target).stem}.py"
        out_path = Path("tests") / out_name
        out_path.write_text(final_state["test_code"], encoding="utf-8")
        print(f"  Saved passing tests to: {out_path}")

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
