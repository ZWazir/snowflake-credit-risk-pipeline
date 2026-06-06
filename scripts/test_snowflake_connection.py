import os
from pathlib import Path

from dotenv import load_dotenv
import snowflake.connector


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def test_snowflake_connection():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    )

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT CURRENT_VERSION();")
        result = cursor.fetchone()

        print("Successfully connected to Snowflake.")
        print(f"Snowflake version: {result[0]}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    test_snowflake_connection()