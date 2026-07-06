"""
TestForge evaluation harness.

Runs the agent across all sample modules and reports aggregate stats.
Each run is logged to MLflow under the 'testforge-eval' experiment.
"""
import sys
import time
from pathlib import Path

from testforge.agent.graph import run_agent
from testforge.observability.logging import get_logger

log = get_logger("testforge.eval")

SAMPLES_DIR = Path(__file__).parent / "samples"

SAMPLES = [
    ("math_utils.py", "easy"),
    ("string_ops.py", "easy"),
    ("stack.py", "medium"),
    ("converter.py", "medium"),
    ("cache.py", "medium"),
    ("validator.py", "medium"),
    ("linked_list.py", "hard"),
    ("matrix.py", "hard"),
    ("rate_limiter.py", "hard"),
    ("json_flattener.py", "hard"),
]


def run_eval(
    max_iterations: int = 4,
    coverage_target: float = 80.0,
) -> list[dict]:
    results = []

    print("=" * 60)
    print("TESTFORGE EVALUATION")
    print(f"  Samples: {len(SAMPLES)}")
    print(f"  Coverage target: {coverage_target}%")
    print(f"  Max iterations: {max_iterations}")
    print("=" * 60)

    for filename, difficulty in SAMPLES:
        file_path = str(SAMPLES_DIR / filename)
        print(f"\n[{difficulty.upper()}] {filename}...", end=" ")
        sys.stdout.flush()

        start = time.perf_counter()
        try:
            final_state = run_agent(
                file_path=file_path,
                max_iterations=max_iterations,
                coverage_target=coverage_target,
            )
            elapsed = round(time.perf_counter() - start, 1)
            result = final_state.get("test_result", {})

            entry = {
                "file": filename,
                "difficulty": difficulty,
                "status": final_state.get("status", "unknown"),
                "coverage": result.get("coverage_pct", 0.0),
                "iterations": final_state.get("iteration", 0),
                "num_passed": result.get("num_passed", 0),
                "num_failed": result.get("num_failed", 0),
                "duration_s": elapsed,
            }
            print(
                f"{entry['status'].upper()} "
                f"cov={entry['coverage']}% "
                f"iter={entry['iterations']} "
                f"({elapsed}s)"
            )
        except Exception as e:
            elapsed = round(time.perf_counter() - start, 1)
            entry = {
                "file": filename,
                "difficulty": difficulty,
                "status": "error",
                "coverage": 0.0,
                "iterations": 0,
                "num_passed": 0,
                "num_failed": 0,
                "duration_s": elapsed,
                "error": str(e),
            }
            print(f"ERROR ({elapsed}s): {e}")

        results.append(entry)

    print_summary(results)
    return results


def print_summary(results: list[dict]) -> None:
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    coverages = [r["coverage"] for r in results]
    iterations = [r["iterations"] for r in results]
    durations = [r["duration_s"] for r in results]

    print(f"\n  Success rate:    {passed}/{total} "
          f"({100 * passed / total:.0f}%)")
    print(f"  Mean coverage:   {sum(coverages) / total:.1f}%")
    print(f"  Mean iterations: {sum(iterations) / total:.1f}")
    print(f"  Total time:      {sum(durations):.0f}s")

    print("\n  Per-file results:")
    print(f"  {'File':<25} {'Diff':<8} {'Status':<8} "
          f"{'Cov%':<8} {'Iter':<6} {'Time'}")
    print("  " + "-" * 65)
    for r in results:
        print(
            f"  {r['file']:<25} {r['difficulty']:<8} "
            f"{r['status']:<8} {r['coverage']:<8.1f} "
            f"{r['iterations']:<6} {r['duration_s']:.1f}s"
        )

    by_diff = {}
    for r in results:
        by_diff.setdefault(r["difficulty"], []).append(r)

    print("\n  By difficulty:")
    for diff in ["easy", "medium", "hard"]:
        group = by_diff.get(diff, [])
        if not group:
            continue
        g_passed = sum(1 for r in group if r["status"] == "passed")
        g_cov = sum(r["coverage"] for r in group) / len(group)
        print(f"    {diff:<8} {g_passed}/{len(group)} passed, "
              f"mean cov {g_cov:.1f}%")


if __name__ == "__main__":
    run_eval()
