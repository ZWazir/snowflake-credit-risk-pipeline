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
    )


def verify_environment():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        checks = [
            "SELECT CURRENT_ROLE();",
            "SELECT CURRENT_WAREHOUSE();",
            "SHOW WAREHOUSES LIKE 'CREDIT_RISK_WH';",
            "SHOW DATABASES LIKE 'CREDIT_RISK_DB';",
            "SHOW SCHEMAS IN DATABASE CREDIT_RISK_DB;",
        ]

        for check in checks:
            print(f"\nRunning: {check}")
            cursor.execute(check)

            rows = cursor.fetchall()
            for row in rows:
                print(row)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    verify_environment()