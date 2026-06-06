import os
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
import snowflake.connector

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


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
        schema="FEATURES",
    )


def load_features_from_snowflake():
    conn = get_connection()

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


def train_model():
    df = load_features_from_snowflake()

    print(f"Rows loaded from Snowflake: {len(df)}")
    print(f"Columns loaded: {list(df.columns)}")

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

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print("\nModel training complete.")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    train_model()