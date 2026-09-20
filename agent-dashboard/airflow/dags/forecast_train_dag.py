"""Airflow DAG retrain CatBoost khi gold forecast input được cập nhật."""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.python import PythonOperator

GOLD_FORECAST_INPUT = Dataset("postgres://agent_dashboard/gold/v_forecast_input")


def call_forecast_train_endpoint() -> None:
    """Gọi API train explicit sau khi Airflow đã cập nhật gold marts."""
    import os
    import requests

    response = requests.post(os.environ["BACKEND_TRAIN_URL"], timeout=3600)
    response.raise_for_status()


with DAG(
    dag_id="forecast_train_dag",
    start_date=datetime(2026, 9, 20),
    schedule=[GOLD_FORECAST_INPUT],
    catchup=False,
    max_active_runs=1,
    tags=["agent-dashboard", "forecast", "catboost"],
) as dag:
    train_catboost = PythonOperator(task_id="train_catboost", python_callable=call_forecast_train_endpoint)
