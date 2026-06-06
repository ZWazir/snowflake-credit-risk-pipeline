import os
from pathlib import Path

from dotenv import load_dotenv
import snowflake.connector


BASE_DIR = Path(__file__).resolve().parents[1]
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
        schema="FEATURES",
    )


def create_feature_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE CREDIT_RISK_WH;")
        cursor.execute("USE DATABASE CREDIT_RISK_DB;")
        cursor.execute("USE SCHEMA FEATURES;")

        cursor.execute("""
            CREATE OR REPLACE TABLE CREDIT_RISK_DB.FEATURES.CREDIT_RISK_FEATURES AS
            SELECT
                customer_id,
                annual_income,
                credit_score,
                loan_amount,
                debt_to_income_ratio,
                employment_length_years,
                previous_defaults,
                has_previous_default,

                CASE
                    WHEN loan_amount = 0 THEN NULL
                    ELSE annual_income / loan_amount
                END AS income_to_loan_ratio,

                CASE
                    WHEN credit_score_band = 'poor' THEN 1
                    WHEN credit_score_band = 'fair' THEN 2
                    WHEN credit_score_band = 'good' THEN 3
                    WHEN credit_score_band = 'very_good' THEN 4
                    WHEN credit_score_band = 'excellent' THEN 5
                    ELSE NULL
                END AS credit_score_band_encoded,

                CASE
                    WHEN dti_band = 'low_dti' THEN 1
                    WHEN dti_band = 'medium_dti' THEN 2
                    WHEN dti_band = 'high_dti' THEN 3
                    ELSE NULL
                END AS dti_band_encoded,

                defaulted,
                CURRENT_TIMESTAMP() AS feature_created_at

            FROM CREDIT_RISK_DB.STAGING.STG_CREDIT_APPLICATIONS
            WHERE data_quality_issue_flag = 0;
        """)

        cursor.execute("""
            SELECT COUNT(*)
            FROM CREDIT_RISK_DB.FEATURES.CREDIT_RISK_FEATURES;
        """)
        row_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT *
            FROM CREDIT_RISK_DB.FEATURES.CREDIT_RISK_FEATURES
            LIMIT 5;
        """)
        sample_rows = cursor.fetchall()

        print("Created feature table successfully.")
        print(f"Rows in feature table: {row_count}")
        print("\\nSample rows:")
        for row in sample_rows:
            print(row)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_feature_table()  