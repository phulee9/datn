# Agent Dashboard

Backend cho đồ án **Agent Dashboard**: ingestion dữ liệu lịch sử Dunnhumby, pipeline hóa đơn Gemini Vision và Forecast CatBoost.

Không thuộc scope thư mục này: frontend, Orchestrator, SQL Agent, Combo Agent.

## Kiến trúc

```
Client (upload / forecast)
  -> FastAPI
  -> MinIO (receipts-raw, dunnhumby-raw)
  -> PostgreSQL staging -> silver -> gold (dbt)
  -> Airflow -> dbt build -> CatBoost train
  -> Forecast API (gold.v_forecast_input / gold.mart_daily_sales)
```

### Tầng lưu trữ

- `staging`: landing raw (`staging.product`, `staging.transaction`, `staging.receipt`, `staging.receipt_item`).
- `silver`: canonical (`silver.dim_store`, `silver.dim_product`, `silver.dim_product_alias`, `silver.fact_receipt`, `silver.fact_receipt_item`).
- `gold`: mart vật lý (`gold.mart_daily_sales`, `gold.mart_forecast_features`) và view mỏng `gold.v_forecast_input`.
- `forecast_training_runs` ở `public`: metadata vận hành cho Airflow retrain.
- Không có `dim_date`.
- Toàn bộ bảng dữ liệu staging/silver/gold có `dih_fetch_day`, `dih_fetch_month`, `dih_fetch_year` (`SMALLINT`).

### Luồng chính

1. **Seed Dunnhumby**: `product.csv` + `transaction_data.csv` -> `staging.*`.
2. **dbt**: `staging` -> `silver` -> `gold`.
3. **Upload hóa đơn**: `POST /api/receipts/upload` -> hash `SHA-256` -> MinIO `receipts-raw/YYYY/MM/DD/<uuid>.ext` -> `staging.receipt: pending`.
4. **Gemini background worker**: tải ảnh từ MinIO -> Gemini structured `ReceiptExtract` -> validator + SKU mapper -> `staging.receipt` + `staging.receipt_item` thành `confirmed` / `needs_review` / `error`.
5. **Airflow trigger**: khi `staging.receipt.status = confirmed`, FastAPI trigger `receipt_transform_dag` -> `dbt build`.
6. **Forecast**: `gold.v_forecast_input` đã có `lag_1/7/14`, `rolling_mean/std_7`, `weekday/is_weekend` -> CatBoost native categorical `store_id/sku/category` -> `artifacts/forecast/global_model.joblib`.

## Cấu trúc thư mục

```text
agent-dashboard/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   ├── scripts/seed_dunnhumby.py
│   ├── tests/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── api/
│       ├── agents/forecast_agent.py
│       ├── core/errors.py
│       ├── db/
│       ├── ingestion/
│       ├── storage/minio_storage.py
│       └── pipeline/airflow_trigger.py
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dags/
│       ├── receipt_transform_dag.py
│       └── forecast_train_dag.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── profiles.yml.example
│   ├── macros/
│   └── models/
│       ├── staging/
│       ├── silver/
│       └── gold/
├── data/raw/dunnhumby/
└── artifacts/forecast/
```

## Yêu cầu môi trường

- WSL2 + Docker CLI / Docker Desktop
- Conda env `datn` hoặc `agent-dashboard`
- Python 3.11
- File Dunnhumby `product.csv`, `transaction_data.csv`

## Cấu hình

Copy env mẫu:

```bash
cp backend/.env.example backend/.env
```

Các biến chính trong `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://app:password@localhost:5432/agent_dashboard
READONLY_DATABASE_URL=postgresql+asyncpg://app:password@localhost:5432/agent_dashboard
GEMINI_API_KEY=
MINIO_ENDPOINT_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
AIRFLOW_API_URL=http://localhost:8080/api/v1
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
SEED_BASE_DATE=2024-10-11
SEED_TOP_STORES=15
SEED_TOP_SKUS=150
FORECAST_MINIMUM_HISTORY_DAYS=14
```

`dbt/profiles.yml` đọc cùng biến DB qua `DBT_POSTGRES_*`.

## Chạy local (WSL2 + Conda)

### 1. Tạo env Conda

```bash
conda create -n agent-dashboard python=3.11 -y
conda activate agent-dashboard
pip install -r backend/requirements.txt
```

### 2. Chuẩn bị dữ liệu raw

```bash
mkdir -p data/raw/dunnhumby
# đặt product.csv và transaction_data.csv vào data/raw/dunnhumby/
```

### 3. Khởi động stack

```bash
docker compose up -d --build
```

Dịch vụ:

- `postgres:5432`
- `minio:9000` (API), `9001` (console)
- `api:8000`
- `airflow-webserver:8080`
- `airflow-scheduler`

Kiểm tra nhanh:

```bash
curl http://localhost:8000/health
curl http://localhost:9000/minio/health/live
curl http://localhost:8080/health
```

MinIO console: `http://localhost:9001` (`minioadmin` / `minioadmin`).
Airflow UI: `http://localhost:8080` (`airflow` / `airflow`).

### 4. Migration

Đây là thay đổi breaking so với `0001_initial`. Với DB dev hiện có, chạy clean reset:

```bash
docker compose exec api alembic downgrade base
docker compose exec api alembic upgrade head
```

Hoặc local không qua container:

```bash
cd backend
alembic upgrade head
```

Tạo DB `airflow` nếu chưa có (dùng cho metadata Airflow):

```bash
docker compose exec postgres psql -U app -d agent_dashboard -c "CREATE DATABASE airflow;"
```

### 5. Seed Dunnhumby vào staging

```bash
docker compose exec api python scripts/seed_dunnhumby.py
```

Hoặc:

```bash
curl -X POST http://localhost:8000/api/internal/seed/dunnhumby
# yêu cầu ALLOW_SEED_API=true
```

Seed nạp toàn bộ `staging.product` và toàn bộ `staging.transaction`. Top 15 store / 150 SKU chỉ áp dụng ở dbt silver.

### 6. dbt build

```bash
docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt build --profiles-dir /opt/airflow/dbt --vars '{seed_base_date: 2024-10-11, top_stores: 15, top_skus: 150}'"
```

Hoặc local:

```bash
cd dbt
dbt build --profiles-dir . --vars '{seed_base_date: 2024-10-11, top_stores: 15, top_skus: 150}'
```

Kết quả:

- `silver.dim_store`
- `silver.dim_product`
- `silver.fact_receipt`
- `silver.fact_receipt_item`
- `gold.mart_daily_sales`
- `gold.mart_forecast_features`
- `gold.v_forecast_input`

### 7. Forecast

Train CatBoost từ gold feature mart:

```bash
curl -X POST http://localhost:8000/api/forecast/train
```

Dự báo:

```bash
curl "http://localhost:8000/api/forecast?sku=<sku>&store_id=<id>&horizon_days=7"
```

## API chính

- `POST /api/receipts/upload` (multipart `files`, chống trùng `SHA-256`, trả 409 nếu ảnh đã tồn tại)
- `GET /api/receipts`
- `GET /api/receipts/{id}`
- `PATCH /api/receipts/{id}`
- `POST /api/forecast/train`
- `GET /api/forecast`
- `POST /api/internal/seed/dunnhumby`
- `GET /health`

## MinIO

- Bucket `receipts-raw`: `s3://receipts-raw/YYYY/MM/DD/<uuid>.ext`
- Bucket `dunnhumby-raw` (optional): dùng khi deploy.
- Database chỉ lưu `image_uri` dạng `s3://...`.

## DBeaver

- Host: `localhost`
- Port: `5432`
- Database: `agent_dashboard`
- User: `app`
- Password: `password`

Kiểm tra schema:

```sql
select schemaname, tablename from pg_tables
where schemaname in ('staging','silver','gold')
order by schemaname, tablename;

select * from gold.mart_daily_sales limit 20;
select * from gold.v_forecast_input limit 20;
```

## Ghi chú Dunnhumby date

`DAY` trong `transaction_data.csv` là ngày tương đối.

```text
receipt_date = SEED_BASE_DATE + DAY - 1
```

Ngày fake nằm trong dbt `silver.fact_receipt`, không nằm trong `dim_date`.

## Kiểm thử

```bash
cd backend
python -m py_compile app/config.py app/db/models.py app/db/repository.py app/ingestion/seed_dunnhumby.py app/ingestion/service.py app/api/schemas.py app/api/routes.py app/agents/forecast_agent.py app/storage/minio_storage.py app/pipeline/airflow_trigger.py
PYTHONPATH=. python -m pytest tests -q
```

## Airflow

- `receipt_transform_dag`: `schedule=None`, được FastAPI trigger khi có `staging.receipt` mới `confirmed`.
- `forecast_train_dag`: `schedule=[gold.v_forecast_input]`, gọi `POST /api/forecast/train`.

Trigger thủ công:

```bash
docker compose exec airflow-scheduler airflow dags trigger receipt_transform_dag
docker compose exec airflow-scheduler airflow dags trigger forecast_train_dag
```
