import os
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
import snowflake.connector

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def get_connection(schema="FEATURES"):
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=schema,
    )


def load_features_from_snowflake():
    conn = get_connection(schema="FEATURES")

    query = """
        SELECT
            customer_id,
            annual_income,
            credit_score,
            loan_amount,
            debt_to_income_ratio,
            employment_length_years,
            previous_defaults,
            has_previous_default,
            income_to_loan_ratio,
            credit_score_band_encoded,
            dti_band_encoded,
            defaulted
        FROM CREDIT_RISK_DB.FEATURES.CREDIT_RISK_FEATURES;
    """

    try:
        df = pd.read_sql(query, conn)
        return df

    finally:
        conn.close()


def train_model_and_generate_predictions(df):
    feature_columns = [
        "ANNUAL_INCOME",
        "CREDIT_SCORE",
        "LOAN_AMOUNT",
        "DEBT_TO_INCOME_RATIO",
        "EMPLOYMENT_LENGTH_YEARS",
        "PREVIOUS_DEFAULTS",
        "HAS_PREVIOUS_DEFAULT",
        "INCOME_TO_LOAN_RATIO",
        "CREDIT_SCORE_BAND_ENCODED",
        "DTI_BAND_ENCODED",
    ]

    target_column = "DEFAULTED"

    X = df[feature_columns]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    prediction_df = df[["CUSTOMER_ID"]].copy()
    prediction_df["PREDICTED_DEFAULT"] = model.predict(X)
    prediction_df["DEFAULT_PROBABILITY"] = model.predict_proba(X)[:, 1]
    prediction_df["ACTUAL_DEFAULTED"] = y
    prediction_df["MODEL_NAME"] = "logistic_regression_baseline"

    return prediction_df


def write_predictions_to_snowflake(prediction_df):
    conn = get_connection(schema="ML_OUTPUTS")
    cursor = conn.cursor()

    try:
        cursor.execute("USE WAREHOUSE CREDIT_RISK_WH;")
        cursor.execute("USE DATABASE CREDIT_RISK_DB;")
        cursor.execute("USE SCHEMA ML_OUTPUTS;")

        cursor.execute("""
            CREATE OR REPLACE TABLE CREDIT_RISK_DB.ML_OUTPUTS.CREDIT_RISK_PREDICTIONS (
                customer_id NUMBER(10, 0),
                predicted_default NUMBER(1, 0),
                default_probability FLOAT,
                actual_defaulted NUMBER(1, 0),
                model_name STRING,
                scored_at TIMESTAMP
            );
        """)

        rows = [
            (
                int(row["CUSTOMER_ID"]),
                int(row["PREDICTED_DEFAULT"]),
                float(row["DEFAULT_PROBABILITY"]),
                int(row["ACTUAL_DEFAULTED"]),
                str(row["MODEL_NAME"]),
            )
            for _, row in prediction_df.iterrows()
        ]

        insert_sql = """
            INSERT INTO CREDIT_RISK_DB.ML_OUTPUTS.CREDIT_RISK_PREDICTIONS (
                customer_id,
                predicted_default,
                default_probability,
                actual_defaulted,
                model_name,
                scored_at
            )
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP());
        """

        cursor.executemany(insert_sql, rows)

        cursor.execute("""
            SELECT COUNT(*)
            FROM CREDIT_RISK_DB.ML_OUTPUTS.CREDIT_RISK_PREDICTIONS;
        """)
        row_count = cursor.fetchone()[0]

        print("Predictions written to Snowflake.")
        print(f"Rows written: {row_count}")

        cursor.execute("""
            SELECT *
            FROM CREDIT_RISK_DB.ML_OUTPUTS.CREDIT_RISK_PREDICTIONS
            LIMIT 5;
        """)

        print("\nSample prediction rows:")
        for row in cursor.fetchall():
            print(row)

    finally:
        cursor.close()
        conn.close()


def main():
    df = load_features_from_snowflake()
    print(f"Rows loaded from Snowflake: {len(df)}")

    prediction_df = train_model_and_generate_predictions(df)
    print(f"Predictions generated: {len(prediction_df)}")

    write_predictions_to_snowflake(prediction_df)


if __name__ == "__main__":
    main()