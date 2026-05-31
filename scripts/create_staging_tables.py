import duckdb


DATABASE_PATH = "warehouse/credit_risk.duckdb"


def create_staging_credit_applications() -> None:
    """
    Create a cleaned staging table from the raw credit applications table.

    The staging layer standardizes column types, creates derived fields,
    and prepares the data for downstream feature engineering and modeling.
    """

    connection = duckdb.connect(DATABASE_PATH)

    connection.execute("CREATE SCHEMA IF NOT EXISTS staging;")

    connection.execute(
        """
        CREATE OR REPLACE TABLE staging.stg_credit_applications AS
        SELECT
            CAST(customer_id AS INTEGER) AS customer_id,
            CAST(annual_income AS DOUBLE) AS annual_income,
            CAST(credit_score AS INTEGER) AS credit_score,
            CAST(loan_amount AS DOUBLE) AS loan_amount,
            CAST(debt_to_income_ratio AS DOUBLE) AS debt_to_income_ratio,
            CAST(employment_length_years AS INTEGER) AS employment_length_years,
            CAST(previous_defaults AS INTEGER) AS previous_defaults,
            CAST(defaulted AS INTEGER) AS defaulted,

            CASE
                WHEN credit_score >= 740 THEN 'excellent'
                WHEN credit_score >= 670 THEN 'good'
                WHEN credit_score >= 580 THEN 'fair'
                ELSE 'poor'
            END AS credit_score_band,

            CASE
                WHEN annual_income >= 100000 THEN 'high_income'
                WHEN annual_income >= 60000 THEN 'middle_income'
                ELSE 'lower_income'
            END AS income_band,

            CASE
                WHEN debt_to_income_ratio >= 0.45 THEN 1
                ELSE 0
            END AS high_dti_flag,

            CASE
                WHEN loan_amount / NULLIF(annual_income, 0) >= 0.5 THEN 1
                ELSE 0
            END AS high_loan_to_income_flag

        FROM raw.credit_applications;
        """
    )

    row_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM staging.stg_credit_applications;
        """
    ).fetchone()[0]

    connection.close()

    print("Created staging.stg_credit_applications.")
    print(f"Rows created: {row_count}")


if __name__ == "__main__":
    create_staging_credit_applications()