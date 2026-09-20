"""Airflow DAG chạy dbt sau khi receipt staging được xác nhận."""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.datasets import Dataset

GOLD_FORECAST_INPUT = Dataset("postgres://agent_dashboard/gold/v_forecast_input")
DBT_COMMAND = "cd /opt/airflow/dbt && dbt build --profiles-dir /opt/airflow/dbt --vars '{seed_base_date: 2024-10-11, top_stores: 15, top_skus: 150}'"

with DAG(
    dag_id="receipt_transform_dag",
    start_date=datetime(2026, 9, 20),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["agent-dashboard", "dbt", "receipt"],
) as dag:
    transform_pipeline = BashOperator(
        task_id="transform_staging_to_gold",
        bash_command=DBT_COMMAND,
        outlets=[GOLD_FORECAST_INPUT],
    )
