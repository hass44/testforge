"""
TestForge — agentic test generation pipeline.
Uses LangGraph to run a self-correcting generate → run → repair loop.
"""

import sys
from pathlib import Path

from testforge.agent.graph import run_agent


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <file> [coverage] [iters]")
        sys.exit(1)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    target = args[0] if args else None
    if not target or not Path(target).exists():
        print(f"File not found: {target}")
        sys.exit(1)

    coverage_target = float(args[1]) if len(args) > 1 else 80.0
    max_iterations = int(args[2]) if len(args) > 2 else 4

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

        if "--mutate" in flags:
            _run_mutation(final_state["test_code"], target)

    return 0 if status == "passed" else 1


def _run_mutation(test_code: str, source_file: str) -> None:
    from testforge.tools.mutation import run_mutation_tests

    print("\n" + "=" * 50)
    print("MUTATION TESTING")
    print("=" * 50)
    mut = run_mutation_tests(
        test_code=test_code,
        source_file=source_file,
    )
    if mut.get("error"):
        print(f"  Error: {mut['error']}")
        return
    print(f"  Mutants killed:    {mut['killed']}")
    print(f"  Mutants survived:  {mut['survived']}")
    print(f"  Total mutants:     {mut['total']}")
    print(f"  Kill rate:         {mut['kill_rate']}%")
    if mut["survivors"]:
        print("\n  Surviving mutants:")
        for s in mut["survivors"]:
            print(f"    - {s}")


if __name__ == "__main__":
    sys.exit(main())
