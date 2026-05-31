import duckdb
import numpy as np
import pandas as pd
import torch
import joblib
from torch import nn


DATABASE_PATH = "warehouse/credit_risk.duckdb"
MODEL_PATH = "models/credit_risk_model.pt"
SCALER_PATH = "models/credit_risk_scaler.joblib"


FEATURE_COLUMNS = [
    "annual_income",
    "credit_score",
    "loan_amount",
    "debt_to_income_ratio",
    "employment_length_years",
    "previous_defaults",
    "high_dti_flag",
    "high_loan_to_income_flag",
    "loan_to_income_ratio",
    "credit_score_band_numeric",
    "income_band_numeric",
    "long_employment_flag",
]


class CreditRiskModel(nn.Module):
    """
    Simple neural network for binary credit default classification.

    This architecture must match the model architecture used during training.
    """

    def __init__(self, input_size: int):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.network(x)


def load_feature_data() -> pd.DataFrame:
    """
    Load feature data from DuckDB.
    """

    connection = duckdb.connect(DATABASE_PATH)

    feature_data = connection.execute(
        """
        SELECT *
        FROM features.credit_risk_features;
        """
    ).fetchdf()

    connection.close()

    return feature_data


def create_predictions() -> pd.DataFrame:
    """
    Load the trained PyTorch model and generate predictions for all customers.
    """

    feature_data = load_feature_data()

    X = feature_data[FEATURE_COLUMNS]

    scaler = joblib.load(SCALER_PATH)
    X_scaled = scaler.transform(X)

    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

    model = CreditRiskModel(input_size=X_tensor.shape[1])
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()

    with torch.no_grad():
        predicted_default_probability = model(X_tensor).numpy().flatten()

    predictions = pd.DataFrame(
        {
            "customer_id": feature_data["customer_id"],
            "predicted_default_probability": predicted_default_probability,
            "predicted_default_flag": np.where(predicted_default_probability >= 0.5, 1, 0),
            "actual_defaulted": feature_data["target_defaulted"],
        }
    )

    return predictions


def write_predictions_to_duckdb() -> None:
    """
    Write model predictions back to DuckDB as a warehouse table.
    """

    predictions = create_predictions()

    connection = duckdb.connect(DATABASE_PATH)

    connection.execute("CREATE SCHEMA IF NOT EXISTS predictions;")

    connection.register("predictions_dataframe", predictions)

    connection.execute(
        """
        CREATE OR REPLACE TABLE predictions.credit_risk_predictions AS
        SELECT *
        FROM predictions_dataframe;
        """
    )

    row_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM predictions.credit_risk_predictions;
        """
    ).fetchone()[0]

    connection.close()

    print("Created predictions.credit_risk_predictions.")
    print(f"Rows created: {row_count}")


if __name__ == "__main__":
    write_predictions_to_duckdb()