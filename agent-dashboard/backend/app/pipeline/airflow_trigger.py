"""Trigger Airflow DAG khi receipt đạt confirmed."""

from __future__ import annotations

from datetime import date

import httpx

from app.config import settings


def build_confirmed_receipt_payload(receipt_id: int, fetch_date: date, source_type: str) -> dict:
    """Tạo conf payload gửi Airflow khi receipt được xác nhận."""
    return {
        "receipt_id": receipt_id,
        "source_type": source_type,
        "fetch_year": fetch_date.year,
        "fetch_month": fetch_date.month,
        "fetch_day": fetch_date.day,
    }


def trigger_receipt_transform_dag(receipt_id: int, fetch_date: date, source_type: str) -> tuple[bool, str]:
    """Gọi Airflow REST API để trigger receipt_transform_dag.

    Input:
        receipt_id: id staging.receipt vừa confirmed.
        fetch_date: fetch partition chứa thay đổi.
        source_type: gemini_upload hoặc dunnhumby.
    Output:
        Tuple (triggered, message). Failure không chặn ingestion transaction.
    """
    payload = build_confirmed_receipt_payload(receipt_id, fetch_date, source_type)
    api_url = settings.airflow_api_url.rstrip("/")
    url = f"{api_url}/dags/{settings.airflow_transform_dag_id}/dagRuns"
    try:
        response = httpx.post(
            url,
            json={"conf": payload},
            auth=(settings.airflow_username, settings.airflow_password) if settings.airflow_username else None,
            timeout=8.0,
        )
        if response.status_code in {200, 201, 409}:
            return True, f"Airflow DAG {settings.airflow_transform_dag_id} đã được trigger cho receipt {receipt_id}."
        body = response.text[:400]
        return False, f"Airflow trả {response.status_code}: {body}."
    except Exception as error:
        return False, f"Không gọi được Airflow trigger: {error}."
