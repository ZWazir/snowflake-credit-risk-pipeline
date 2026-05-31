import subprocess
import sys


PIPELINE_STEPS = [
    ("Create sample credit data", "scripts/create_sample_credit_data.py"),
    ("Load raw data to DuckDB", "scripts/load_raw_to_duckdb.py"),
    ("Create staging tables", "scripts/create_staging_tables.py"),
    ("Create feature tables", "scripts/create_feature_tables.py"),
    ("Train PyTorch model", "models/train_pytorch_model.py"),
    ("Write predictions to DuckDB", "scripts/write_predictions_to_duckdb.py"),
    ("Validate pipeline outputs", "scripts/validate_pipeline_outputs.py"),
]


def run_step(step_name: str, script_path: str) -> None:
    """
    Run one pipeline step as a Python subprocess.
    """

    print("\n" + "=" * 80)
    print(f"Running step: {step_name}")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, script_path],
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Pipeline failed at step: {step_name}")

    print(f"Completed step: {step_name}")


def run_pipeline() -> None:
    """
    Run the full local credit risk pipeline from raw data generation
    through model prediction output.
    """

    for step_name, script_path in PIPELINE_STEPS:
        run_step(step_name, script_path)

    print("\n" + "=" * 80)
    print("Pipeline completed successfully.")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline()