# Snowflake Credit Risk Pipeline

## Overview

This project is an end-to-end data engineering and machine learning pipeline for credit risk modeling.

The pipeline currently runs locally using DuckDB as a lightweight warehouse. It is designed so the warehouse layer can later be migrated to Snowflake once Snowflake access is available.

The project demonstrates how raw credit application data can move through a structured data workflow:

```text
Synthetic Credit Data
→ Raw CSV
→ DuckDB Raw Table
→ Staging Table
→ Feature Table
→ PyTorch Model Training
→ Prediction Output Table
```

## Project Purpose

The purpose of this project is to build practical skills in data engineering and ML-adjacent pipeline development.

This project is designed to show:

* Python-based data generation and ingestion
* Local warehouse development with DuckDB
* Layered warehouse design
* SQL transformation workflows
* Feature engineering for machine learning
* PyTorch binary classification
* Writing prediction outputs back to the warehouse
* Reproducible end-to-end pipeline execution

## Current Architecture

The local MVP uses the following layers:

### 1. Raw Data

Synthetic credit application data is generated with Python and saved as a CSV file.

Output:

```text
data/raw/credit_applications.csv
```

### 2. Raw Warehouse Layer

The raw CSV is loaded into DuckDB.

Table:

```text
raw.credit_applications
```

### 3. Staging Layer

The staging layer standardizes column types and creates basic derived business fields.

Table:

```text
staging.stg_credit_applications
```

Example derived fields:

* `credit_score_band`
* `income_band`
* `high_dti_flag`
* `high_loan_to_income_flag`

### 4. Feature Layer

The feature layer creates model-ready columns for PyTorch training.

Table:

```text
features.credit_risk_features
```

Example feature fields:

* `loan_to_income_ratio`
* `credit_score_band_numeric`
* `income_band_numeric`
* `long_employment_flag`
* `target_defaulted`

### 5. Model Training

A PyTorch binary classification model is trained using the warehouse feature table.

Model task:

```text
Predict whether a credit applicant defaults.
```

### 6. Prediction Output

Model predictions are written back to DuckDB as a warehouse table.

Table:

```text
predictions.credit_risk_predictions
```

Prediction fields:

* `customer_id`
* `predicted_default_probability`
* `predicted_default_flag`
* `actual_defaulted`

### 7. Validation Checks

The pipeline includes a validation script that checks whether the expected warehouse tables exist and contain the correct number of records.

Validation script:

```text
scripts/validate_pipeline_outputs.py

## Tech Stack

* Python
* DuckDB
* SQL
* pandas
* NumPy
* scikit-learn
* PyTorch
* Git/GitHub

Planned future additions:

* Snowflake
* dbt
* Pipeline orchestration

## Project Structure

```text
snowflake-credit-risk-pipeline/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── data/
│   ├── DATA_SOURCE.md
│   └── raw/
│
├── warehouse/
│
├── scripts/
│   ├── create_sample_credit_data.py
│   ├── load_raw_to_duckdb.py
│   ├── create_staging_tables.py
│   ├── create_feature_tables.py
│   ├── write_predictions_to_duckdb.py
│   └── run_pipeline.py
│
└── models/
    └── train_pytorch_model.py
```

## How to Run the Project

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the full pipeline

```bash
python scripts/run_pipeline.py
```

This command runs the full local pipeline:

```text
Create sample data
→ Load raw data
→ Create staging table
→ Create feature table
→ Train PyTorch model
→ Write predictions
```

## Current Model Output

The initial PyTorch model trains successfully from the DuckDB feature table and produces evaluation metrics including:

* Accuracy
* Precision
* Recall
* ROC AUC

The current model is an MVP. The main goal is to demonstrate pipeline integration rather than maximize predictive performance.

## Current Status

Local MVP is in progress.

Completed:

* Project setup
* Local DuckDB warehouse
* Synthetic credit dataset generation
* Raw data ingestion
* Staging transformation
* Feature table creation
* PyTorch model training
* Prediction table output
* End-to-end pipeline runner

Planned next steps:

* Improve model training workflow
* Save and reuse preprocessing objects
* Add validation tests
* Add dbt transformation layer
* Migrate warehouse layer from DuckDB to Snowflake
* Add architecture diagram
* Add final portfolio write-up

## Notes

This project is for educational and portfolio purposes. It is not intended for production credit decisioning.
