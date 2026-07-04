import json
from testforge.analysis.analyzer import analyze_file

def main():
    target = "examples/calculator.py"
    print(f"Analyzing {target}...")
    
    try:
        metadata = analyze_file(target)
        print("\nAnalysis Result:")
        print(json.dumps(metadata, indent=2))
    except Exception as e:
        print(f"\nError running analyzer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
