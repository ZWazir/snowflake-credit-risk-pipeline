import duckdb


DATABASE_PATH = "warehouse/credit_risk.duckdb"


def create_credit_risk_features() -> None:
    """
    Create an ML-ready feature table from the staged credit applications data.

    The feature layer converts business-friendly fields into numeric model inputs
    that can later be used by a PyTorch classification model.
    """

    connection = duckdb.connect(DATABASE_PATH)

    connection.execute("CREATE SCHEMA IF NOT EXISTS features;")

    connection.execute(
        """
        CREATE OR REPLACE TABLE features.credit_risk_features AS
        SELECT
            customer_id,

            annual_income,
            credit_score,
            loan_amount,
            debt_to_income_ratio,
            employment_length_years,
            previous_defaults,
            high_dti_flag,
            high_loan_to_income_flag,

            loan_amount / NULLIF(annual_income, 0) AS loan_to_income_ratio,

            CASE
                WHEN credit_score_band = 'excellent' THEN 4
                WHEN credit_score_band = 'good' THEN 3
                WHEN credit_score_band = 'fair' THEN 2
                WHEN credit_score_band = 'poor' THEN 1
                ELSE 0
            END AS credit_score_band_numeric,

            CASE
                WHEN income_band = 'high_income' THEN 3
                WHEN income_band = 'middle_income' THEN 2
                WHEN income_band = 'lower_income' THEN 1
                ELSE 0
            END AS income_band_numeric,

            CASE
                WHEN employment_length_years >= 10 THEN 1
                ELSE 0
            END AS long_employment_flag,

            defaulted AS target_defaulted

        FROM staging.stg_credit_applications;
        """
    )

    row_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM features.credit_risk_features;
        """
    ).fetchone()[0]

    connection.close()

    print("Created features.credit_risk_features.")
    print(f"Rows created: {row_count}")


if __name__ == "__main__":
    create_credit_risk_features()