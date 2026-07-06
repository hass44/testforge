from testforge.agent.generator import generate_pytest_suite
from testforge.analysis.analyzer import analyze_file


def main():
    target = "examples/calculator.py"

    print(f"Analyzing {target}...")
    metadata = analyze_file(target)

    with open(target, encoding="utf-8") as f:
        source_code = f.read()

    print("Generating tests via LLM...")
    try:
        test_code = generate_pytest_suite(source_code, metadata, file_path=target)
        print("\n=== Generated Test Suite ===")
        print(test_code)

        output_file = "tests/test_calculator_generated.py"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(test_code)
        print(f"\nSaved generated tests to {output_file}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
