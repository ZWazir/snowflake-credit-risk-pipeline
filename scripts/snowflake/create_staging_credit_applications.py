import os
from pathlib import Path

from dotenv import load_dotenv
import snowflake.connector


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="STAGING",
    )


def create_staging_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE CREDIT_RISK_WH;")
        cursor.execute("USE DATABASE CREDIT_RISK_DB;")
        cursor.execute("USE SCHEMA STAGING;")

        cursor.execute("""
            CREATE OR REPLACE TABLE CREDIT_RISK_DB.STAGING.STG_CREDIT_APPLICATIONS AS
            SELECT
                "customer_id"::NUMBER(10, 0) AS customer_id,
                "annual_income"::NUMBER(12, 2) AS annual_income,
                "credit_score"::NUMBER(4, 0) AS credit_score,
                "loan_amount"::NUMBER(12, 2) AS loan_amount,
                "debt_to_income_ratio"::NUMBER(6, 3) AS debt_to_income_ratio,
                "employment_length_years"::NUMBER(4, 0) AS employment_length_years,
                "previous_defaults"::NUMBER(4, 0) AS previous_defaults,
                "defaulted"::NUMBER(1, 0) AS defaulted,

                CASE
                    WHEN "credit_score" < 580 THEN 'poor'
                    WHEN "credit_score" < 670 THEN 'fair'
                    WHEN "credit_score" < 740 THEN 'good'
                    WHEN "credit_score" < 800 THEN 'very_good'
                    ELSE 'excellent'
                END AS credit_score_band,

                CASE
                    WHEN "debt_to_income_ratio" >= 0.50 THEN 'high_dti'
                    WHEN "debt_to_income_ratio" >= 0.35 THEN 'medium_dti'
                    ELSE 'low_dti'
                END AS dti_band,

                CASE
                    WHEN "previous_defaults" > 0 THEN 1
                    ELSE 0
                END AS has_previous_default,

                CASE
                    WHEN "annual_income" <= 0 THEN 1
                    WHEN "credit_score" IS NULL THEN 1
                    WHEN "loan_amount" <= 0 THEN 1
                    WHEN "debt_to_income_ratio" < 0 THEN 1
                    ELSE 0
                END AS data_quality_issue_flag,

                CURRENT_TIMESTAMP() AS staged_at

            FROM CREDIT_RISK_DB.RAW.CREDIT_APPLICATIONS;
        """)

        cursor.execute("""
            SELECT COUNT(*)
            FROM CREDIT_RISK_DB.STAGING.STG_CREDIT_APPLICATIONS;
        """)
        row_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT *
            FROM CREDIT_RISK_DB.STAGING.STG_CREDIT_APPLICATIONS
            LIMIT 5;
        """)
        sample_rows = cursor.fetchall()

        print("Created staging table successfully.")
        print(f"Rows staged: {row_count}")
        print("\\nSample rows:")
        for row in sample_rows:
            print(row)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_staging_table()