# Kiến Trúc Pipeline Ingestion — Hệ Thống Phân Tích Hóa Đơn WinMart

> **Phạm vi:** Tài liệu này mô tả **kiến trúc ingestion** từ điểm đã có sẵn parquet. Giả định `raw/*.parquet` và `receipts.jsonl → invoices/invoice_items.parquet` đã được gen (tiền xử lý, streaming, không thuộc luồng incremental này). Từ đây thiết kế **luồng append từ ảnh hóa đơn → Silver → Gold → Serving**, kèm **công nghệ dùng ở từng đoạn**, **cách lưu trữ** và **chiến lược incremental**. Tên bảng là **ví dụ** (có thể đổi khi gen data), schema tương tự.

---

## 1. Tổng Quan Kiến Trúc

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NGUỒN CÓ SẴN (tiền xử lý)                        │
│  raw/categories.parquet (92)  raw/products.parquet (3062)               │
│  raw/fake_receipts.jsonl (20M) ──streaming──► dataset_for_ai/*.parquet  │
│       1 dòng = 1 JSON OCR ──► invoices (20M) + invoice_items (70M)      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │  (đã có sẵn, không thiết kế lại)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ẢNH HÓA ĐƠN MỚI ──► OCR (Gemini Vision) ──► MinIO Bronze (json)        │
│                              append hourly                               │
│  Bronze ──► Silver (MinIO + Iceberg, partitioned) ──► Gold (ClickHouse) │
│               ▲ Airflow + Spark/dbt              ▲ Airflow daily        │
│                                                                     │    │
│  Serving: Text-to-SQL / Forecast / Combo ──► Gold only (<30ms)      │    │
│              FastAPI + Redis cache                                   │    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Ba lớp lưu trữ:**

| Lớp | Vai Trò | Lưu Ở Đâu | Format |
|---|---|---|---|
| **Bronze (Raw)** | Giữ nguyên như nguồn, để audit & replay | **MinIO** `s3://lake/bronze/` | `jsonl.gz` (OCR) + `parquet` (batch gen) |
| **Silver** | Chuẩn hóa, JOIN, dedup, partition | **MinIO + Iceberg** `s3://lake/silver/` | **Parquet partitioned by `purchase_date`**, `zstd`, file 128–256MB |
| **Gold** | Agg sẵn cho AI, query <50ms | **ClickHouse** `gold.*` + **Redis** | `MergeTree` + cache TTL 1h |

---

## 2. Công Nghệ Và Vai Trò

| Công Nghệ | Vai Trò Trong Pipeline | Không Làm Gì |
|---|---|---|
| **MinIO** | Object storage rẻ — đĩa cho mọi file (thay `crawl_winmart/raw/` local). Lưu `jsonl.gz`, `parquet`, `Iceberg metadata`. | Không transform, không query |
| **Apache Iceberg** | Table format trên MinIO — biến thư mục parquet rời rạc thành **bảng có transaction**. Cho `INSERT 1 file 50KB` không đụng 700M cũ, `MERGE/DELETE` khi sửa OCR, `snapshot` rollback, `partition` theo `purchase_date`. | Không lưu data, chỉ `metadata.json + manifest` |
| **Apache Spark** | **Batch ETL** — transform nặng `Bronze 18G → Silver 70M` (dedup 6068→3062, JOIN `fact × dim`, normalize). Chạy 1 lần/ngày, 5–10 phút. | Không serve AI (startup 10–20s, chậm cho <100ms) |
| **Trino** | **Interactive query** — đọc Iceberg/MinIO bằng SQL như Postgres. Dùng cho `dbt run`, ad-hoc `SELECT * FROM silver WHERE purchase_date='2026-10-12'`, drill-down hiếm. Pushdown chỉ scan 1 partition. | Không làm ETL nặng tốt bằng Spark |
| **dbt** | **Quản lý SQL** — viết `models/silver/invoice_items.sql` thay vì `spark_job.py`. Tự `incremental` (`WHERE purchase_date > max`), tự `test` (`unique, not_null`), tự `docs` lineage. | Không schedule, không lưu data. Dưới 5 model có thể bỏ, dùng Spark SQL thuần. |
| **ClickHouse** | **OLAP cho Gold** — bảng nhỏ `mart_daily_sales` (1.8k dòng) cần **<20–30ms, QPS cao**. Columnar, `MergeTree`, nén 10×. | Không lưu Raw/Silver (18G raw để trong CH đắt) |
| **Redis** | **Cache nóng** — `GET mart_daily_sales:2026-01` TTL 1h. Text-to-SQL hit 80% → **<5ms**. | Không lưu fact |
| **Apache Airflow** | **Scheduler** — gọi `dbt run` theo giờ/ngày, `OPTIMIZE` weekly, alert khi fail. | Không transform |

---

## 3. Lưu Trữ Chi Tiết

### 3.1. Bronze — MinIO `s3://lake/bronze/`

```
s3://lake/bronze/
├── categories/
│   └── categories.parquet              (92 dòng, 1 file)
├── products/
│   └── products.parquet                (3062 dòng, 1 file)
├── receipts/
│   ├── purchase_date=2026-10-12/
│   │   ├── batch_001.jsonl.gz          (ảnh OCR batch, append = thêm file)
│   │   └── batch_002.jsonl.gz
│   └── purchase_date=2026-10-11/
│       └── batch_001.jsonl.gz
└── raw_receipts/
    └── raw_receipts.parquet            (1 dòng = 1 JSON OCR gốc, để audit)
```

- **Ghi:** `PUT s3://lake/bronze/receipts/purchase_date=2026-10-12/004.json` — mỗi ảnh 1 file nhỏ, không ghi đè.
- **Đọc:** Spark/Trino `read_json("s3://lake/bronze/receipts/purchase_date=2026-10-12/*.json")`.

### 3.2. Silver — MinIO + Iceberg `s3://lake/silver/` (partitioned)

```
s3://lake/silver/
├── categories/                         (dim, không partition, 1 file)
│   └── data/00001.parquet
│   └── metadata/metadata.json
├── products/                           (dim, không partition, 1 file)
│   └── data/00001.parquet
├── invoices/                           (fact, partitioned)
│   ├── purchase_date=2026-10-12/
│   │   └── data/00001.parquet  (30k hóa đơn, ~5MB, zstd)
│   ├── purchase_date=2026-10-11/
│   │   └── data/00001.parquet
│   └── metadata/  (Iceberg: metadata.json, manifest, snapshot)
└── invoice_items/                      (fact, partitioned, 70M dòng)
    ├── purchase_date=2026-10-12/
    │   └── data/00001.parquet  (100k dòng, ~8MB)
    └── metadata/
```

- **Partition:** `purchase_date` (YYYY-MM-DD). Mỗi ngày 1 thư mục, chứa 1–2 file 128–256MB. Query `WHERE purchase_date='2026-10-12'` chỉ scan 1 thư mục (pushdown).
- **Compression:** `zstd` (tốt hơn `snappy` 20% cho số liệu, nén 5–8×).
- **Iceberg:** Mỗi `INSERT` ghi 1 file parquet mới + cập nhật `manifest` (không rewrite file cũ). Hỗ trợ `MERGE INTO` khi sửa hóa đơn OCR sai.

### 3.3. Gold — ClickHouse `gold.*` + Redis

```
ClickHouse (MergeTree):
  gold.mart_daily_sales      (purchase_date, category_code, total_qty, revenue, invoice_cnt)  ~1.8k dòng
  gold.mart_store_sales      (purchase_date, store_code, revenue, invoice_cnt)               ~15k dòng
  gold.mart_combo_rules      (antecedent, consequent, support, confidence, lift)              ~5k dòng
  gold.mart_forecast_features (purchase_date, category_code, lag_7, rolling_7, event_flag)   ~10k dòng

Redis:
  mart_daily_sales:2026-01  → JSON (TTL 1h)
  mart_combo: MENU01145     → JSON (TTL 1h)
```

- ClickHouse `MergeTree` với `ORDER BY (purchase_date, category_code)` — query theo ngày/category scan 1 granule.
- Redis cache 80% hit cho Text-to-SQL câu lặp (`doanh thu tháng 1?`).

---

## 4. Luồng Chi Tiết — Đoạn Nào Dùng Gì

### 4.1. Luồng Batch Có Sẵn (tiền xử lý, đã chạy)

| Đoạn | Input → Output | Công Nghệ | Lưu Trữ | Ghi Chú |
|---|---|---|---|---|
| **Gen** | `raw/categories.csv + raw/products.csv` → `raw/fake_receipts.jsonl` | **Python** `gen_fake_receipts.ipynb` (thuần `category_code`, 15 basket, 11 affinity, event động theo năm, `WRITE_CHUNK_SIZE=5000`, `APPEND_MODE`) | Local `raw/fake_receipts.jsonl` → upload `s3://lake/bronze/receipts/` | Streaming, không gom 20M vào RAM |
| **Export** | `raw/fake_receipts.jsonl` → `invoices + invoice_items` parquet | **Python** `export_parquet_for_ai.ipynb` (`ParquetWriter` streaming, mỗi 5000 hóa đơn = 1 row group, `zstd`) | `dataset_for_ai/*.parquet` hoặc `s3://lake/silver/` (nếu lên MinIO) | Streaming, không gom 70M dòng |

### 4.2. Luồng Incremental — Ảnh Hóa Đơn Mới

| Đoạn | Input → Output | Công Nghệ | Lưu Trữ | Tần Suất |
|---|---|---|---|---|
| **1. OCR** | `Ảnh JPG/PNG (upload)` → `JSON OCR` | **Gemini Vision** (VLM, structured output `ReceiptExtract`), `validator` (check `total_amount`, `ocr_confidence`), `SKU mapper` (`exact → normalized → fuzzy`) | `MinIO` `s3://lake/bronze/receipts/purchase_date=2026-10-12/004.json` | Mỗi ảnh (~1s) |
| **2. Bronze → Silver** | `s3://lake/bronze/receipts/purchase_date=2026-10-12/*.json` → `s3://lake/silver/invoices/` + `invoice_items/` | **Spark** (hoặc **Trino + dbt incremental** nếu model <5) — `spark.read.json → dedup → JOIN products → write` | **MinIO + Iceberg** `purchase_date=2026-10-12/00001.parquet` + manifest | **Hourly** (Airflow) |
| **3. Silver → Gold** | `s3://lake/silver/invoice_items/` → `gold.mart_daily_sales` | **Spark SQL** `GROUP BY purchase_date, category_code` → `INSERT INTO ClickHouse` | **ClickHouse** `gold.*` | **Daily 02:00** |
| **4. Combo** | `silver/invoice_items` (basket theo `invoice_id`) → `gold.mart_combo_rules` | **Spark** batch **FP-Growth** (`mlxtend`, precompute, không chạy trong request) | **ClickHouse** | **Daily** (sau Gold) |
| **5. Compact** | Nhiều file nhỏ 50KB → 1 file 128MB | **Iceberg** `CALL system.rewrite_data_files` + **ClickHouse** `OPTIMIZE` | MinIO + ClickHouse | **Weekly** |

### 4.3. Luồng Serving — AI Query (chỉ đọc Gold)

| Model | Query | Công Nghệ Đọc | Bảng Đọc | Latency |
|---|---|---|---|---|
| **Text-to-SQL** | `doanh thu tháng 1?` | **Redis** (hit) → **ClickHouse** (miss) | `gold.mart_daily_sales` | **<5ms / 15–30ms** |
| **Forecast** | `dự báo 30 ngày tới?` | **ClickHouse** `mart_daily_sales` + `mart_forecast_features` (Prophet/MA, batch precompute, không train trong request) | `gold.mart_*` | **40–70ms** |
| **Combo** | `mua mì thì mua gì kèm?` | **ClickHouse** `mart_combo_rules` (precompute) | `gold.mart_combo_rules` | **<20ms** |
| **Drill-down** (hiếm) | `SELECT * FROM invoice_items LIMIT 10` | **Trino** đọc Iceberg Silver | `s3://lake/silver/invoice_items/` | **200–400ms** |

> **Nguyên tắc:** AI **không bao giờ** `SELECT SUM(line_total) FROM invoice_items GROUP BY` trên 70M dòng runtime. Gold đã `GROUP BY` sẵn.

---

## 5. Bảng Silver — Schema Ví Dụ (có thể đổi tên)

> Tên bảng là **ví dụ minh họa**, gen data có thể đặt `dim_*/fact_*` — schema tương tự.

| Bảng | Khóa | Cột Chính | Dòng (20M) | Partition |
|---|---|---|---|---|
| `products` | `item_no PK` | `name, brand_name, category_code FK, category_name, final_price, uom_name` | 3062 | Không |
| `categories` | `category_code PK` | `category_name, level (1/2), parent_code, root_code` | 92 | Không |
| `invoices` | `invoice_id PK` | `purchase_datetime, purchase_date, store_code FK, cashier_id, total_discount, total_amount, item_count` | 20M | `purchase_date` |
| `invoice_items` | `(invoice_id, line_no) PK` | `item_no FK (NULL nếu unmatched), product_name_raw, quantity, unit_price, discount, line_total, match_status` | ~70M | `purchase_date` |

- `match_status`: `exact` / `normalized` / `unmatched`.
- Không lưu `brand/category` lặp trong fact → JOIN `products` khi query.
- `purchase_date` là cột partition (YYYY-MM-DD), cũng là `ORDER BY` trong ClickHouse Gold.

---

## 6. Orchestration (Airflow)

```
DAG: winmart_ingestion  (hourly: Silver, daily: Gold, weekly: compact)

hourly_silver:
  bronze_sensor (S3KeySensor: s3://lake/bronze/receipts/purchase_date={{ds}}/*)
    → spark_submit (Spark: bronze → silver incremental, partition purchase_date)
    → dbt run --select silver  (nếu dùng dbt-trino/spark, materialized='incremental', unique_key=['invoice_id','line_no'])
    → dbt test (unique, not_null, relationships)

daily_gold (02:00):
  silver_sensor (Iceberg snapshot)
    → spark_submit (GROUP BY → mart_daily_sales)
    → clickhouse_insert (INSERT INTO gold.mart_daily_sales)
    → spark_submit (FP-Growth → mart_combo_rules)
    → redis_invalidate (DEL mart_daily_sales:*)

weekly_compact (Sunday 03:00):
  → Iceberg: CALL system.rewrite_data_files(table=>'silver.invoice_items', strategy=>'sort', sort_order=>'purchase_date')
  → ClickHouse: OPTIMIZE TABLE gold.mart_daily_sales FINAL
```

- Dưới 5 model Silver/Gold: bỏ `dbt`, dùng `PythonOperator` + `spark.sql()` trong Airflow là đủ gọn.
- Trino chỉ cần nếu muốn ad-hoc `SELECT * FROM silver` không qua ClickHouse.

---

## 7. Hiệu Năng Với 20M (70M dòng fact)

| Thao Tác | MinIO + Iceberg (Silver) | ClickHouse (Gold) |
|---|---|---|
| 1 json mới (OCR) → Silver | 1 file 50KB + manifest, **<2s**, không đụng 700M cũ | — |
| 1000 json/giờ (batch) | 1 file 5MB, **2–5s** | — |
| Build Gold daily (GROUP BY 1 partition) | — | **<10s** (100k dòng) |
| AI: `doanh thu tháng 1?` | — | **15–30ms** (ClickHouse) / **<5ms** (Redis hit) |
| Drill-down `SELECT * FROM invoice_items LIMIT 10` | Trino 200–400ms (1 partition) | — |

> Nếu Silver là **1 file parquet 700MB không partition** thì append phải đọc/ghi lại cả file → **30–60s**. Partition là bắt buộc.

---

## 8. Query Mẫu (đọc Gold, không đọc Silver runtime)

```sql
-- Forecast: doanh thu theo ngày + category (Gold)
SELECT purchase_date, category_code, SUM(revenue) FROM gold.mart_daily_sales GROUP BY 1,2;

-- Combo: đã precompute
SELECT antecedent, consequent, support, confidence FROM gold.mart_combo_rules WHERE antecedent = 'MENU01145' ORDER BY lift DESC LIMIT 10;

-- Text-to-SQL: sản phẩm rẻ nhất (Gold/Silver nhỏ)
SELECT item_no, name, final_price FROM products WHERE category_code = 'MENU01133' ORDER BY final_price LIMIT 5;
```

---

## 9. Ghi Chú

- Parquet có sẵn là **điểm bắt đầu** của tài liệu này. Gen (`raw/fake_receipts.jsonl` → `dataset_for_ai/*.parquet`) đã streaming (`WRITE_CHUNK_SIZE=5000`, `ParquetWriter` mỗi 5000 hóa đơn = 1 row group, `zstd`) nên 20M không OOM — nhưng đó là **tiền xử lý**, không thuộc luồng incremental này.
- Tên bảng `products/categories/invoices/invoice_items` là ví dụ, có thể đổi thành `dim_*/fact_*` khi gen — schema và luồng không đổi.
- Thay `ClickHouse` bằng `Postgres` vẫn chạy được nếu Gold <10M dòng, nhưng ClickHouse nhanh hơn 3–4× cho Gold và QPS cao.
- Dưới ~5M hóa đơn có thể dùng **plain partitioned parquet** (không Iceberg) vẫn append được. Trên 20M hoặc cần `MERGE/DELETE` khi sửa OCR thì mới cần Iceberg.
