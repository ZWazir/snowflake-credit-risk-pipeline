import os
import numpy as np
import pandas as pd


def create_sample_credit_data(output_path: str = "data/raw/credit_applications.csv") -> None:
    """
    Create a synthetic credit risk dataset for local pipeline development.

    This dataset is intentionally simple. Its purpose is to test the ingestion,
    warehouse, transformation, and modeling workflow before using a larger
    real-world dataset.
    """

    np.random.seed(42)

    number_of_records = 1000

    customer_ids = np.arange(1, number_of_records + 1)

    annual_income = np.random.normal(loc=75000, scale=25000, size=number_of_records)
    annual_income = np.clip(annual_income, 25000, 200000)

    credit_score = np.random.normal(loc=680, scale=75, size=number_of_records)
    credit_score = np.clip(credit_score, 300, 850)

    loan_amount = np.random.normal(loc=18000, scale=9000, size=number_of_records)
    loan_amount = np.clip(loan_amount, 1000, 60000)

    debt_to_income_ratio = np.random.normal(loc=0.32, scale=0.15, size=number_of_records)
    debt_to_income_ratio = np.clip(debt_to_income_ratio, 0.02, 0.95)

    employment_length_years = np.random.randint(0, 31, size=number_of_records)

    previous_defaults = np.random.binomial(n=1, p=0.12, size=number_of_records)

    default_probability = (
        0.35 * (credit_score < 620)
        + 0.25 * (debt_to_income_ratio > 0.45)
        + 0.20 * previous_defaults
        + 0.10 * (annual_income < 50000)
        + 0.10 * (loan_amount > 30000)
    )

    default_probability = np.clip(default_probability, 0, 0.95)

    defaulted = np.random.binomial(n=1, p=default_probability)

    credit_data = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "annual_income": annual_income.round(2),
            "credit_score": credit_score.round(0).astype(int),
            "loan_amount": loan_amount.round(2),
            "debt_to_income_ratio": debt_to_income_ratio.round(3),
            "employment_length_years": employment_length_years,
            "previous_defaults": previous_defaults,
            "defaulted": defaulted,
        }
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    credit_data.to_csv(output_path, index=False)

    print(f"Created sample credit dataset at: {output_path}")
    print(f"Rows created: {len(credit_data)}")
    print("Default rate:", round(credit_data["defaulted"].mean(), 3))


if __name__ == "__main__":
    create_sample_credit_data()