import os
from pathlib import Path

from dotenv import load_dotenv
import snowflake.connector


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
CSV_PATH = BASE_DIR / "data" / "raw" / "credit_applications.csv"

load_dotenv(dotenv_path=ENV_PATH)


def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def load_raw_credit_applications():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE CREDIT_RISK_WH;")
        cursor.execute("USE DATABASE CREDIT_RISK_DB;")
        cursor.execute("USE SCHEMA RAW;")

        cursor.execute("""
            CREATE OR REPLACE FILE FORMAT CREDIT_RISK_DB.RAW.CSV_FORMAT
            TYPE = 'CSV'
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            PARSE_HEADER = TRUE
            NULL_IF = ('', 'NULL', 'null')
            EMPTY_FIELD_AS_NULL = TRUE;
        """)

        cursor.execute("""
            CREATE OR REPLACE STAGE CREDIT_RISK_DB.RAW.RAW_STAGE
            FILE_FORMAT = CREDIT_RISK_DB.RAW.CSV_FORMAT;
        """)

        cursor.execute("DROP TABLE IF EXISTS CREDIT_RISK_DB.RAW.CREDIT_APPLICATIONS;")

        cursor.execute(f"""
            PUT 'file://{CSV_PATH}'
            @CREDIT_RISK_DB.RAW.RAW_STAGE
            AUTO_COMPRESS = TRUE
            OVERWRITE = TRUE;
        """)

        cursor.execute("""
            CREATE OR REPLACE TABLE CREDIT_RISK_DB.RAW.CREDIT_APPLICATIONS
            USING TEMPLATE (
                SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                FROM TABLE(
                    INFER_SCHEMA(
                        LOCATION => '@CREDIT_RISK_DB.RAW.RAW_STAGE',
                        FILE_FORMAT => 'CREDIT_RISK_DB.RAW.CSV_FORMAT'
                    )
                )
            );
        """)

        cursor.execute("""
            COPY INTO CREDIT_RISK_DB.RAW.CREDIT_APPLICATIONS
            FROM @CREDIT_RISK_DB.RAW.RAW_STAGE
            FILE_FORMAT = CREDIT_RISK_DB.RAW.CSV_FORMAT
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
        """)

        cursor.execute("SELECT COUNT(*) FROM CREDIT_RISK_DB.RAW.CREDIT_APPLICATIONS;")
        row_count = cursor.fetchone()[0]

        print("Loaded raw credit applications into Snowflake.")
        print(f"Rows loaded: {row_count}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_raw_credit_applications()