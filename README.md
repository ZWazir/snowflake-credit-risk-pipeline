# Snowflake Credit Risk Pipeline

## Overview

This project is an end-to-end data engineering and machine learning pipeline built with Snowflake, dbt, Python, and PyTorch.

The project simulates a credit risk workflow where raw borrower or loan data is loaded into Snowflake, transformed through a warehouse modeling process, converted into ML-ready feature tables, used to train a PyTorch classification model, and written back to Snowflake as prediction outputs.

## Project Goals

The goal of this project is to demonstrate practical skills in:

- Cloud data warehousing with Snowflake
- Python-based data ingestion
- SQL transformation workflows
- dbt data modeling
- Feature engineering for machine learning
- PyTorch model training
- Writing model predictions back to the warehouse
- Portfolio-ready documentation and reproducible project structure

## Planned Architecture

Raw Data → Python Load Script → Snowflake RAW Schema → dbt Models → Feature Table → PyTorch Model → Prediction Table in Snowflake

## Tech Stack

- Python
- Snowflake
- dbt
- SQL
- PyTorch
- pandas
- scikit-learn

## Project Status

In progress.

Current phase: local project setup and dataset selection.