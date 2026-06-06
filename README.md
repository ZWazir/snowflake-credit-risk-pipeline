# Cloud Credit Risk ML Pipeline with Snowflake, DuckDB, and PyTorch

## Overview

This project is an end-to-end credit risk machine learning pipeline that combines local development, cloud data warehousing, SQL transformation, and Python-based model training.

The pipeline was first developed locally using DuckDB and PyTorch to validate the data generation, transformation, feature engineering, and model training workflow. It was then migrated to Snowflake to simulate a production-style cloud data warehouse architecture with layered `RAW`, `STAGING`, `FEATURES`, and `ML_OUTPUTS` schemas.

The Snowflake implementation ingests synthetic credit application data, transforms it through warehouse layers, prepares machine-learning-ready features, trains a baseline model from Snowflake data, and writes prediction outputs back into Snowflake for downstream analysis.

The goal of the project is to demonstrate practical data engineering, analytics engineering, and machine learning workflow skills across:

* Local pipeline prototyping with DuckDB
* Cloud data warehousing with Snowflake
* SQL-based transformation layers
* Feature engineering for credit risk modeling
* PyTorch-based model development in the local MVP
* Python-based model training and scoring from Snowflake data
* Writing ML predictions back to a warehouse output layer
* Reproducible project organization and environment configuration

---

## Architecture

### Local DuckDB + PyTorch MVP

```text
Synthetic Credit Data
  ↓
DuckDB Raw Table
  ↓
DuckDB Staging Tables
  ↓
DuckDB Feature Tables
  ↓
PyTorch Model
  ↓
DuckDB Prediction Outputs
```

### Snowflake Cloud Pipeline

```text
CSV
  ↓
Snowflake Internal Stage
  ↓
RAW.CREDIT_APPLICATIONS
  ↓
STAGING.STG_CREDIT_APPLICATIONS
  ↓
FEATURES.CREDIT_RISK_FEATURES
  ↓
Python Logistic Regression Model
  ↓
ML_OUTPUTS.CREDIT_RISK_PREDICTIONS
```

The Snowflake implementation follows a layered data warehouse pattern:

| Layer      | Purpose                                            |
| ---------- | -------------------------------------------------- |
| RAW        | Stores source data loaded from CSV                 |
| STAGING    | Cleans, standardizes, and validates raw fields     |
| FEATURES   | Creates model-ready variables for machine learning |
| ML_OUTPUTS | Stores model predictions and probability scores    |

---

## Local MVP vs Snowflake Implementation

This project was first developed locally using DuckDB to validate the data model, transformation logic, and machine learning workflow. The local pipeline includes a PyTorch model to demonstrate neural network-based credit risk modeling in a lightweight development environment.

After the local MVP was working end-to-end, the pipeline was migrated to Snowflake to simulate a production-style cloud data warehouse architecture.

* **DuckDB version:** lightweight local prototype with PyTorch model training
* **Snowflake version:** cloud implementation with `RAW`, `STAGING`, `FEATURES`, and `ML_OUTPUTS` schemas
* **Machine learning workflow:** model-ready features are generated from SQL transformations and used for Python-based prediction workflows

This mirrors a realistic development workflow: prototype locally, validate logic, then migrate the data platform architecture to a cloud warehouse environment.

---

## Project Structure

```text
.
├── data/
│   └── raw/
│       └── credit_applications.csv
│
├── scripts/
│   ├── duckdb/
│   │   ├── create_sample_credit_data.py
│   │   ├── load_raw_to_duckdb.py
│   │   ├── create_staging_tables.py
│   │   ├── create_feature_tables.py
│   │   ├── write_predictions_to_duckdb.py
│   │   ├── validate_pipeline_outputs.py
│   │   └── run_pipeline.py
│   │
│   └── snowflake/
│       ├── test_snowflake_connection.py
│       ├── setup_snowflake_environment.py
│       ├── verify_snowflake_environment.py
│       ├── load_raw_credit_applications_to_snowflake.py
│       ├── create_staging_credit_applications.py
│       ├── create_feature_credit_risk_table.py
│       ├── train_credit_risk_model_from_snowflake.py
│       └── write_credit_risk_predictions_to_snowflake.py
│
├── models/
│   └── train_pytorch_model.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Tech Stack

* **Python**
* **Snowflake**
* **DuckDB**
* **SQL**
* **pandas**
* **scikit-learn**
* **PyTorch**
* **python-dotenv**
* **snowflake-connector-python**

---

## Dataset

The project uses a synthetic credit application dataset with the following fields:

| Column                  | Description                                               |
| ----------------------- | --------------------------------------------------------- |
| customer_id             | Unique customer identifier                                |
| annual_income           | Applicant annual income                                   |
| credit_score            | Applicant credit score                                    |
| loan_amount             | Requested loan amount                                     |
| debt_to_income_ratio    | Debt-to-income ratio                                      |
| employment_length_years | Applicant employment history                              |
| previous_defaults       | Prior default count                                       |
| defaulted               | Target variable indicating whether the customer defaulted |

---

## Snowflake Data Model

### RAW Layer

Table:

```text
CREDIT_RISK_DB.RAW.CREDIT_APPLICATIONS
```

The raw layer stores the source CSV data loaded into Snowflake.

### STAGING Layer

Table:

```text
CREDIT_RISK_DB.STAGING.STG_CREDIT_APPLICATIONS
```

The staging layer standardizes data types and adds business-friendly fields, including:

* `credit_score_band`
* `dti_band`
* `has_previous_default`
* `data_quality_issue_flag`
* `staged_at`

### FEATURES Layer

Table:

```text
CREDIT_RISK_DB.FEATURES.CREDIT_RISK_FEATURES
```

The features layer creates model-ready variables, including:

* `income_to_loan_ratio`
* `credit_score_band_encoded`
* `dti_band_encoded`
* `has_previous_default`

### ML Outputs Layer

Table:

```text
CREDIT_RISK_DB.ML_OUTPUTS.CREDIT_RISK_PREDICTIONS
```

The machine learning output layer stores:

* `customer_id`
* `predicted_default`
* `default_probability`
* `actual_defaulted`
* `model_name`
* `scored_at`

---

## Machine Learning Workflow

The project includes two machine learning workflows:

### Local PyTorch Model

The local DuckDB MVP uses a PyTorch model to train on engineered credit risk features and produce prediction outputs. This demonstrates how the pipeline can support neural network-based modeling in a local development environment.

### Snowflake-Based Scoring Workflow

The Snowflake implementation uses warehouse-generated feature tables as the source for Python model training and scoring. A baseline logistic regression model is trained from Snowflake feature data, then predictions are written back to Snowflake.

Features include:

* Annual income
* Credit score
* Loan amount
* Debt-to-income ratio
* Employment length
* Previous defaults
* Income-to-loan ratio
* Encoded credit score band
* Encoded DTI band

The model output includes:

* Binary default prediction
* Default probability score
* Actual default label
* Model name
* Scoring timestamp

---

## How to Run the DuckDB Local Pipeline

The DuckDB version provides a local end-to-end MVP of the pipeline before migrating the workflow to Snowflake.

Run the local pipeline from the project root:

```bash
python scripts/duckdb/run_pipeline.py
```

This runs the local workflow from data generation through validation, including PyTorch model training and local prediction output generation.

---

## How to Run the Snowflake Pipeline

### 1. Create a Snowflake Trial Account

This project can be run with a Snowflake trial account.

### 2. Create a `.env` File

Copy the example environment file:

```bash
cp .env.example .env
```

Fill in your Snowflake credentials:

```env
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=CREDIT_RISK_WH
SNOWFLAKE_DATABASE=CREDIT_RISK_DB
SNOWFLAKE_SCHEMA=RAW
```

Do not commit your `.env` file.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test the Snowflake Connection

```bash
python scripts/snowflake/test_snowflake_connection.py
```

### 5. Create the Snowflake Environment

```bash
python scripts/snowflake/setup_snowflake_environment.py
```

This creates or verifies:

* Warehouse: `CREDIT_RISK_WH`
* Database: `CREDIT_RISK_DB`
* Schemas: `RAW`, `STAGING`, `FEATURES`, `ML_OUTPUTS`

### 6. Load Raw Data into Snowflake

```bash
python scripts/snowflake/load_raw_credit_applications_to_snowflake.py
```

### 7. Create the Staging Table

```bash
python scripts/snowflake/create_staging_credit_applications.py
```

### 8. Create the Feature Table

```bash
python scripts/snowflake/create_feature_credit_risk_table.py
```

### 9. Train the Model from Snowflake Data

```bash
python scripts/snowflake/train_credit_risk_model_from_snowflake.py
```

### 10. Write Predictions Back to Snowflake

```bash
python scripts/snowflake/write_credit_risk_predictions_to_snowflake.py
```

---

## Snowflake Verification Queries

After running the Snowflake pipeline, the following SQL can be used to verify the output.

```sql
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE CREDIT_RISK_WH;
USE DATABASE CREDIT_RISK_DB;

SHOW SCHEMAS;

SELECT COUNT(*)
FROM RAW.CREDIT_APPLICATIONS;

SELECT COUNT(*)
FROM STAGING.STG_CREDIT_APPLICATIONS;

SELECT COUNT(*)
FROM FEATURES.CREDIT_RISK_FEATURES;

SELECT COUNT(*)
FROM ML_OUTPUTS.CREDIT_RISK_PREDICTIONS;
```

Preview prediction output:

```sql
SELECT *
FROM ML_OUTPUTS.CREDIT_RISK_PREDICTIONS
LIMIT 10;
```

---

## Skills Demonstrated

This project demonstrates:

* Building an end-to-end data pipeline
* Designing layered warehouse schemas
* Loading local CSV data into Snowflake
* Creating SQL transformation layers
* Performing feature engineering
* Training machine learning models from engineered features
* Building a PyTorch model in a local pipeline
* Training and scoring from Snowflake feature data
* Writing predictions back to a cloud data warehouse
* Managing environment variables securely
* Organizing local and cloud implementations in one repository
* Building a project suitable for analytics engineering, BI engineering, data engineering, and applied machine learning roles

---

## Future Improvements

Potential next steps include:

* Add dbt models for staging and feature transformations
* Add automated data quality tests
* Add a Snowflake task or scheduled orchestration layer
* Add model evaluation tracking
* Add Power BI or Tableau dashboard connected to Snowflake outputs
* Add GitHub Actions for basic validation
* Replace synthetic data with a larger public credit risk dataset
* Expand the Snowflake ML workflow to include PyTorch scoring outputs
* Compare multiple model types, such as logistic regression, random forest, gradient boosting, XGBoost, and neural networks

---

## Portfolio Summary

This project demonstrates how a local DuckDB and PyTorch-based credit risk machine learning pipeline can be migrated into a Snowflake cloud data warehouse architecture.

It includes raw ingestion, staging transformations, feature engineering, model training, and prediction output storage. The final Snowflake architecture supports a realistic analytics workflow where model outputs can be queried, validated, and connected to BI tools for business reporting.
