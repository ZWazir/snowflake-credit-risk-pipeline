import duckdb
import numpy as np
import pandas as pd
import torch
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn


DATABASE_PATH = "warehouse/credit_risk.duckdb"
MODEL_OUTPUT_PATH = "models/credit_risk_model.pt"
SCALER_OUTPUT_PATH = "models/credit_risk_scaler.joblib"


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

TARGET_COLUMN = "target_defaulted"


class CreditRiskModel(nn.Module):
    """
    Simple neural network for binary credit default classification.
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
    Load ML-ready features from DuckDB.
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


def train_model() -> None:
    """
    Train a PyTorch binary classification model using warehouse features.
    """

    torch.manual_seed(42)
    np.random.seed(42)

    feature_data = load_feature_data()

    X = feature_data[FEATURE_COLUMNS]
    y = feature_data[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    joblib.dump(scaler, SCALER_OUTPUT_PATH)
    print(f"Saved scaler to: {SCALER_OUTPUT_PATH}")

    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train.values.reshape(-1, 1), dtype=torch.float32)

    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)

    model = CreditRiskModel(input_size=X_train_tensor.shape[1])

    loss_function = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    number_of_epochs = 100

    for epoch in range(number_of_epochs):
        model.train()

        predictions = model(X_train_tensor)

        loss = loss_function(predictions, y_train_tensor)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch + 1}/{number_of_epochs}, Loss: {loss.item():.4f}")

    model.eval()

    with torch.no_grad():
        test_probabilities = model(X_test_tensor).numpy().flatten()

    test_predictions = (test_probabilities >= 0.5).astype(int)

    accuracy = accuracy_score(y_test, test_predictions)
    precision = precision_score(y_test, test_predictions, zero_division=0)
    recall = recall_score(y_test, test_predictions, zero_division=0)
    roc_auc = roc_auc_score(y_test, test_probabilities)

    print("\nModel Evaluation")
    print("----------------")
    print(f"Accuracy:  {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"ROC AUC:   {roc_auc:.3f}")

    torch.save(model.state_dict(), MODEL_OUTPUT_PATH)

    print(f"\nSaved model to: {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":
    train_model()