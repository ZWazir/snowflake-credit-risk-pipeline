import duckdb


DATABASE_PATH = "warehouse/credit_risk.duckdb"
RAW_DATA_PATH = "data/raw/credit_applications.csv"


def load_credit_applications_to_duckdb() -> None:
    """
    Load raw credit application data from CSV into a DuckDB raw table.
    """

    connection = duckdb.connect(DATABASE_PATH)

    connection.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    connection.execute(
        """
        CREATE OR REPLACE TABLE raw.credit_applications AS
        SELECT *
        FROM read_csv_auto(?);
        """,
        [RAW_DATA_PATH],
    )

    row_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM raw.credit_applications;
        """
    ).fetchone()[0]

    connection.close()

    print("Loaded raw.credit_applications into DuckDB.")
    print(f"Rows loaded: {row_count}")


if __name__ == "__main__":
    load_credit_applications_to_duckdb()