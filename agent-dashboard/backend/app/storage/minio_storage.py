"""Các hàm làm việc với MinIO theo giao thức S3-compatible."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.core.errors import IngestionError


def build_storage_client():
    """Khởi tạo S3 client từ cấu hình MinIO.

    Output:
        Boto3 client dùng cho object storage.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint_url,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        region_name=settings.minio_region,
    )


def ensure_bucket(bucket_name: str) -> None:
    """Tạo bucket khi chưa tồn tại.

    Input:
        bucket_name: bucket MinIO cần kiểm tra.
    """
    client = build_storage_client()
    try:
        client.head_bucket(Bucket=bucket_name)
    except ClientError as error:
        error_code = str(error.response.get("Error", {}).get("Code", ""))
        if error_code not in {"404", "NoSuchBucket"}:
            raise IngestionError(f"Không kiểm tra được MinIO bucket {bucket_name}: {error}") from error
        try:
            client.create_bucket(Bucket=bucket_name)
        except (BotoCoreError, ClientError) as create_error:
            raise IngestionError(f"Không tạo được MinIO bucket {bucket_name}: {create_error}") from create_error
    except BotoCoreError as error:
        raise IngestionError(f"Không kết nối được MinIO: {error}") from error


def build_receipt_object_key(fetch_date: date, extension: str) -> str:
    """Tạo object key ảnh theo fetch partition và UUID.

    Output:
        Key không chứa bucket, ví dụ 2026/09/20/<uuid>.jpg.
    """
    return f"{fetch_date.year}/{fetch_date.month:02d}/{fetch_date.day:02d}/{uuid4().hex}{extension}"


def build_storage_uri(bucket_name: str, object_key: str) -> str:
    """Tạo URI S3 để database lưu định danh object ổn định."""
    return f"s3://{bucket_name}/{object_key}"


def parse_storage_uri(storage_uri: str) -> tuple[str, str]:
    """Tách URI S3 thành bucket và object key.

    Raises:
        IngestionError: khi URI không đúng định dạng s3://bucket/key.
    """
    if not storage_uri.startswith("s3://"):
        raise IngestionError("image_uri phải có định dạng s3://bucket/object-key.")
    value = storage_uri.removeprefix("s3://")
    bucket_name, separator, object_key = value.partition("/")
    if not bucket_name or not separator or not object_key:
        raise IngestionError("image_uri phải có cả bucket và object key.")
    return bucket_name, object_key


def upload_receipt_image(content: bytes, extension: str, fetch_date: date) -> str:
    """Lưu bytes ảnh hóa đơn vào MinIO và trả URI S3.

    Input:
        content: bytes ảnh đã được API kiểm tra MIME type.
        extension: phần mở rộng đã chuẩn hóa.
        fetch_date: ngày chạy pipeline.
    Output:
        URI s3:// được ghi vào staging.receipt.image_uri.
    """
    ensure_bucket(settings.receipts_raw_bucket)
    object_key = build_receipt_object_key(fetch_date, extension)
    try:
        build_storage_client().put_object(Bucket=settings.receipts_raw_bucket, Key=object_key, Body=content)
    except (BotoCoreError, ClientError) as error:
        raise IngestionError(f"Không lưu được ảnh vào MinIO: {error}") from error
    return build_storage_uri(settings.receipts_raw_bucket, object_key)


def get_object_bytes(storage_uri: str) -> bytes:
    """Tải bytes object từ URI S3 để Gemini đọc ảnh.

    Output:
        Nội dung object bytes.
    """
    bucket_name, object_key = parse_storage_uri(storage_uri)
    try:
        response = build_storage_client().get_object(Bucket=bucket_name, Key=object_key)
        return response["Body"].read()
    except (BotoCoreError, ClientError) as error:
        raise IngestionError(f"Không tải được ảnh từ MinIO: {error}") from error


def create_presigned_read_url(storage_uri: str, expiration_seconds: int = 300) -> str:
    """Tạo URL xem ảnh ngắn hạn cho UI/debug.

    Output:
        Presigned GET URL, không ghi vào database.
    """
    bucket_name, object_key = parse_storage_uri(storage_uri)
    try:
        return build_storage_client().generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=expiration_seconds
        )
    except (BotoCoreError, ClientError) as error:
        raise IngestionError(f"Không tạo được URL ảnh tạm thời: {error}") from error
