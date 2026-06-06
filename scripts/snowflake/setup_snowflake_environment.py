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
    )


def setup_snowflake_environment():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        statements = [
            """
            CREATE WAREHOUSE IF NOT EXISTS CREDIT_RISK_WH
            WITH
                WAREHOUSE_SIZE = 'XSMALL'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE;
            """,
            """
            CREATE DATABASE IF NOT EXISTS CREDIT_RISK_DB;
            """,
            """
            CREATE SCHEMA IF NOT EXISTS CREDIT_RISK_DB.RAW;
            """,
            """
            CREATE SCHEMA IF NOT EXISTS CREDIT_RISK_DB.STAGING;
            """,
            """
            CREATE SCHEMA IF NOT EXISTS CREDIT_RISK_DB.FEATURES;
            """,
            """
            CREATE SCHEMA IF NOT EXISTS CREDIT_RISK_DB.ML_OUTPUTS;
            """,
        ]

        for statement in statements:
            cursor.execute(statement)

        print("Snowflake environment created successfully.")
        print("Created or verified:")
        print("- Warehouse: CREDIT_RISK_WH")
        print("- Database: CREDIT_RISK_DB")
        print("- Schemas: RAW, STAGING, FEATURES, ML_OUTPUTS")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    setup_snowflake_environment()