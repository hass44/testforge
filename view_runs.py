"""View MLflow experiment results from the command line."""
import mlflow

experiment = mlflow.get_experiment_by_name("testforge-runs")
if experiment is None:
    print("No runs yet. Run the agent first:")
    print("  python run.py examples/calculator.py")
    raise SystemExit(1)

runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["start_time DESC"],
)

if runs.empty:
    print("No runs recorded yet.")
    raise SystemExit(0)

print("=" * 70)
print("TESTFORGE — MLflow Experiment Results")
print("=" * 70)

for _, row in runs.iterrows():
    success = "PASS" if row.get("metrics.success", 0) == 1.0 else "FAIL"
    print(f"\n  Run:        {row.get('tags.run_id', 'n/a')}")
    print(f"  File:       {row.get('params.file_path', 'n/a')}")
    print(f"  Model:      {row.get('params.model_name', 'n/a')}")
    print(f"  Coverage:   {row.get('metrics.final_coverage', 0):.1f}%")
    print(f"  Iterations: {int(row.get('metrics.iterations_used', 0))}")
    print(f"  Passed:     {int(row.get('metrics.num_passed', 0))}")
    print(f"  Failed:     {int(row.get('metrics.num_failed', 0))}")
    print(f"  Duration:   {row.get('metrics.total_duration_s', 0):.1f}s")
    print(f"  Status:     {success}")
    print("-" * 40)

print(f"\nTotal runs: {len(runs)}")
