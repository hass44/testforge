SYSTEM_GENERATE = (
    "You are an expert Python developer specializing in writing unit tests. "
    "Your task is to write a pytest suite for the provided code.\n"
    "CRITICAL: Output ONLY valid, executable Python code. "
    "Do NOT wrap your code in markdown code blocks like ```python. "
    "Do NOT write any intro text, outro text, or explanations."
)

SYSTEM_REPAIR = (
    "You are an expert Python developer fixing a test suite. "
    "You will receive the current tests, their failures, and uncovered lines. "
    "Return a COMPLETE corrected test file.\n"
    "CRITICAL: Output ONLY valid, executable Python code. "
    "Do NOT wrap your code in markdown code blocks like ```python. "
    "Do NOT write any intro text, outro text, or explanations."
)

SYSTEM_REGENERATE = (
    "You are an expert Python developer writing a test suite from scratch. "
    "Previous attempts failed — take a completely different approach. "
    "Return a COMPLETE test file.\n"
    "CRITICAL: Output ONLY valid, executable Python code. "
    "Do NOT wrap your code in markdown code blocks like ```python. "
    "Do NOT write any intro text, outro text, or explanations."
)


def build_generate_prompt(test_targets: str, source_code: str) -> str:
    return (
        f"{test_targets}\n\n"
        f"# Source code under test\n"
        f"```python\n{source_code}\n```\n\n"
        f"Write a comprehensive pytest suite covering all targets above, "
        f"including edge cases and error paths."
    )


def build_repair_prompt(
    test_code: str,
    test_result: dict,
    source_code: str,
    test_targets: str,
) -> str:
    sections = []

    sections.append(f"## Test targets and import path\n{test_targets}")

    sections.append(f"## Current test code\n```python\n{test_code}\n```")

    sections.append(
        f"## Test results\n"
        f"Passed: {test_result['num_passed']}, "
        f"Failed: {test_result['num_failed']}, "
        f"Errors: {test_result['num_errors']}, "
        f"Coverage: {test_result['coverage_pct']}%"
    )

    if test_result.get("traceback"):
        sections.append(f"## Failures\n```\n{test_result['traceback']}\n```")

    if test_result.get("uncovered_lines"):
        lines = ", ".join(str(ln) for ln in test_result["uncovered_lines"])
        sections.append(
            f"## Uncovered lines\nNot exercised: [{lines}]"
        )

    sections.append(f"## Original source code\n```python\n{source_code}\n```")

    sections.append(
        "Fix all test failures first, then add tests for any uncovered lines. "
        "Keep the import path exactly as shown in the test targets section. "
        "Return the COMPLETE test file."
    )

    return "\n\n".join(sections)


def build_regenerate_prompt(
    test_result: dict,
    source_code: str,
    test_targets: str,
) -> str:
    sections = []

    sections.append(
        "Previous attempts to generate tests failed repeatedly. "
        "Take a completely different approach."
    )

    if test_result.get("traceback"):
        sections.append(
            f"## Errors from previous attempt (avoid these)\n"
            f"```\n{test_result['traceback']}\n```"
        )

    sections.append(f"## Source code under test\n```python\n{source_code}\n```")
    sections.append(f"## Test targets\n{test_targets}")

    sections.append(
        "Write a COMPLETE pytest suite from scratch using a different strategy. "
        "Cover all targets including edge cases and error paths."
    )

    return "\n\n".join(sections)
