import duckdb


DATABASE_PATH = "warehouse/credit_risk.duckdb"
EXPECTED_ROW_COUNT = 1000


TABLE_CHECKS = [
    ("raw", "credit_applications", "customer_id"),
    ("staging", "stg_credit_applications", "customer_id"),
    ("features", "credit_risk_features", "customer_id"),
    ("predictions", "credit_risk_predictions", "customer_id"),
]


def table_exists(connection: duckdb.DuckDBPyConnection, schema_name: str, table_name: str) -> bool:
    """
    Check whether a table exists in DuckDB.
    """

    result = connection.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = ?
          AND table_name = ?;
        """,
        [schema_name, table_name],
    ).fetchone()[0]

    return result == 1


def validate_table(
    connection: duckdb.DuckDBPyConnection,
    schema_name: str,
    table_name: str,
    unique_key: str,
) -> None:
    """
    Validate that a table exists, has the expected row count,
    and has no duplicate unique keys.
    """

    full_table_name = f"{schema_name}.{table_name}"

    if not table_exists(connection, schema_name, table_name):
        raise ValueError(f"Missing table: {full_table_name}")

    row_count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {full_table_name};
        """
    ).fetchone()[0]

    unique_key_count = connection.execute(
        f"""
        SELECT COUNT(DISTINCT {unique_key})
        FROM {full_table_name};
        """
    ).fetchone()[0]

    duplicate_count = row_count - unique_key_count

    if row_count != EXPECTED_ROW_COUNT:
        raise ValueError(
            f"{full_table_name} failed row count check. "
            f"Expected {EXPECTED_ROW_COUNT}, found {row_count}."
        )

    if duplicate_count != 0:
        raise ValueError(
            f"{full_table_name} failed duplicate key check. "
            f"Found {duplicate_count} duplicate {unique_key} values."
        )

    print(f"PASSED: {full_table_name}")
    print(f"  Row count: {row_count}")
    print(f"  Unique {unique_key}: {unique_key_count}")


def validate_prediction_outputs(connection: duckdb.DuckDBPyConnection) -> None:
    """
    Validate prediction-specific fields.
    """

    result = connection.execute(
        """
        SELECT
            COUNT(*) AS row_count,
            SUM(
                CASE
                    WHEN predicted_default_probability < 0
                      OR predicted_default_probability > 1
                    THEN 1
                    ELSE 0
                END
            ) AS invalid_probability_count,
            SUM(
                CASE
                    WHEN predicted_default_flag NOT IN (0, 1)
                    THEN 1
                    ELSE 0
                END
            ) AS invalid_flag_count
        FROM predictions.credit_risk_predictions;
        """
    ).fetchone()

    row_count = result[0]
    invalid_probability_count = result[1]
    invalid_flag_count = result[2]

    if row_count != EXPECTED_ROW_COUNT:
        raise ValueError(
            f"predictions.credit_risk_predictions failed row count check. "
            f"Expected {EXPECTED_ROW_COUNT}, found {row_count}."
        )

    if invalid_probability_count != 0:
        raise ValueError(
            "predictions.credit_risk_predictions has probabilities outside [0, 1]."
        )

    if invalid_flag_count != 0:
        raise ValueError(
            "predictions.credit_risk_predictions has prediction flags outside {0, 1}."
        )

    print("PASSED: predictions.credit_risk_predictions prediction checks")
    print(f"  Invalid probabilities: {invalid_probability_count}")
    print(f"  Invalid prediction flags: {invalid_flag_count}")


def run_validation_checks() -> None:
    """
    Run all pipeline validation checks.
    """

    connection = duckdb.connect(DATABASE_PATH)

    for schema_name, table_name, unique_key in TABLE_CHECKS:
        validate_table(connection, schema_name, table_name, unique_key)

    validate_prediction_outputs(connection)

    connection.close()

    print("\nAll pipeline validation checks passed.")


if __name__ == "__main__":
    run_validation_checks()