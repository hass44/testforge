"""
TestForge W1 — single-pass pipeline.
Analyze a Python file, generate tests, run them, report results.
No repair loop yet (that's W2 / LangGraph).
"""
import sys
from pathlib import Path

from testforge.analysis.analyzer import analyze_file
from testforge.agent.generator import generate_pytest_suite
from testforge.tools.run_tests import run_tests


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <path-to-python-file>")
        sys.exit(1)

    target = sys.argv[1]
    if not Path(target).exists():
        print(f"File not found: {target}")
        sys.exit(1)

    source_code = Path(target).read_text(encoding="utf-8")

    # 1. ANALYZE
    print(f"[1/3] Analyzing {target}...")
    metadata = analyze_file(target)
    num_targets = len(metadata["functions"]) + sum(
        len(c["methods"]) for c in metadata["classes"]
    )
    print(f"      Found {num_targets} test targets.")

    # 2. GENERATE
    print("[2/3] Generating tests via LLM...")
    test_code = generate_pytest_suite(source_code, metadata, file_path=target)
    print(f"      Generated {test_code.count('def test_')} test functions.")

    # 3. RUN + MEASURE
    print("[3/3] Running tests + measuring coverage...")
    result = run_tests(test_code, target)

    # Report
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"  Tests passed:    {result['num_passed']}")
    print(f"  Tests failed:    {result['num_failed']}")
    print(f"  Errors:          {result['num_errors']}")
    print(f"  Coverage:        {result['coverage_pct']}%")

    if result["uncovered_lines"]:
        print(f"  Uncovered lines: {result['uncovered_lines']}")

    if result["traceback"]:
        print(f"\n--- Failures ---\n{result['traceback']}")

    status = "PASS" if result["passed"] else "FAIL"
    print(f"\n  Status: {status}")

    # Save the generated tests if they passed
    if result["passed"]:
        out_name = f"test_{Path(target).stem}.py"
        out_path = Path("tests") / out_name
        out_path.write_text(test_code, encoding="utf-8")
        print(f"\n  Saved passing tests to: {out_path}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
