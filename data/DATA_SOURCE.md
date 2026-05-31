# Data Source

## Dataset

This project uses a credit risk dataset for building an end-to-end Snowflake, dbt, and PyTorch pipeline.

Initial development will use a small credit risk dataset so the focus stays on pipeline architecture, warehouse modeling, feature engineering, and model integration rather than large-file processing.

## Intended Use

The dataset will be used to simulate a credit risk data workflow:

1. Load raw credit applicant data into Snowflake.
2. Transform raw data into cleaned staging models.
3. Build intermediate business logic models.
4. Create analytical marts and ML-ready feature tables.
5. Train a PyTorch binary classification model.
6. Write model predictions back to Snowflake.

## Target Variable

The target variable represents whether an applicant is considered good or bad credit risk, depending on the dataset encoding.

## Notes

This project is for educational and portfolio purposes. It is not intended for production credit decisioning.