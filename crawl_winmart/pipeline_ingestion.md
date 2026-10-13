# Pipeline Ingestion — WinMart

> **Giả định:** Toàn bộ dữ liệu đầu vào đã có sẵn **dạng parquet**. `raw/fake_receipts.jsonl` đã được tách thành hai bảng **invoices** (1 dòng/hóa đơn) và **invoice_items** (1 dòng/dòng hàng) kèm các bảng liên quan (`categories`, `products`, `stores`, `raw_receipts`), lưu dạng **parquet**. Tài liệu này **chỉ thiết kế luồng từ đây trở đi**. Tên bảng trong tài liệu là **ví dụ tạm** (có thể đổi khi gen data), schema tương tự.

## 1. Trạng Thái Đầu Vào (đã có sẵn)

```
raw/  (local, đã có)
  categories.parquet       — 92 dòng (taxonomy WinMart, 20 L1 + 72 L2)
  products.parquet         — 3062 dòng (dedup theo item_no, join category_code 100%)
  raw_receipts.parquet     — N dòng (1 dòng = 1 JSON OCR gốc, để audit & replay)
  invoices.parquet         — N dòng (1 dòng = 1 hóa đơn: invoice_id, purchase_datetime, purchase_date, store_code, total_amount, ...)
  invoice_items.parquet    — N×avg 3.5 dòng (1 dòng = 1 dòng hàng: invoice_id, line_no, item_no, category_code, quantity, line_total, match_status)

→ Đã flatten, đã JOIN products để lấy item_no/category_code, đã tách purchase_date.
→ Tài liệu này coi như 5 file parquet trên đã sẵn sàng, không thiết kế lại bước gen.
```

Sau khi có parquet, toàn bộ được đẩy lên **MinIO `s3://lake/bronze/`** làm điểm bắt đầu cho pipeline incremental.

## 2. Tổng Quan Luồng

```
[Parquet có sẵn] ──────────────────────────────┐
  categories / products / invoices /            │
  invoice_items / raw_receipts (parquet)        │
                                               ├─→ MinIO Bronze (parquet, đã có)
[Ảnh hóa đơn mới] → OCR (Gemini Vision) ──→ MinIO Bronze (parquet, append theo purchase_date)
                                               │
                                               ├─→ Silver (MinIO + Iceberg, partitioned purchase_date)
                                               │     Airflow + Spark/dbt — hourly
                                               │
                                               ├─→ Gold (ClickHouse + Redis)
                                               │     Airflow — daily 02:00
                                               │
                                               └─→ Serving: Text-to-SQL / Forecast / Combo
                                                     FastAPI → Gold only (<30ms)
```

Ba lớp lưu trữ:

| Lớp | Vai trò | Lưu ở đâu | Format |
|-----|---------|-----------|--------|
| **Bronze** | Giữ nguyên như nguồn, để audit & replay. Parquet có sẵn coi như Bronze. | **MinIO** `s3://lake/bronze/` | `parquet` (`zstd`), partitioned `purchase_date` |
| **Silver** | Chuẩn hóa, dedup, JOIN, partition. Bảng lớn (~70M dòng). | **MinIO + Iceberg** `s3://lake/silver/` | `parquet` partitioned `purchase_date`, `zstd`, 128–256MB/file, Iceberg manifest/snapshot |
| **Gold** | Tổng hợp sẵn, AI chỉ đọc Gold. | **ClickHouse** `gold.*` + **Redis** | `MergeTree` + cache TTL 1h |

## 3. Công Nghệ Theo Đoạn Luồng

| Đoạn luồng | Công nghệ | Vai trò | Lưu trữ |
|------------|-----------|---------|---------|
| **OCR** — Ảnh JPG/PNG → JSON OCR | **Gemini Vision** (VLM, schema `ReceiptExtract`), `validator` (check `total_amount`, `ocr_confidence`), `SKU mapper` (`exact → normalized`) | Trích 1 ảnh thành 1 JSON OCR | Ghi MinIO `s3://lake/bronze/receipts/purchase_date=2026-10-12/004.parquet` (1 row = 1 JSON, `zstd`) |
| **Bronze** — Parquet có sẵn | **MinIO** (S3 API) | Đĩa rẻ cho file lớn (10GB), append = ghi thêm file vào partition ngày đó | `s3://lake/bronze/{categories,products,invoices,invoice_items,raw_receipts}/` |
| **Silver — Transform** | **Spark** (batch nặng: `read → dedup → explode → JOIN broadcast(products) → write`) | Xử lý 10GB → 70M dòng, không OOM | Ghi **MinIO + Iceberg** `s3://lake/silver/{invoices,invoice_items}/purchase_date=*/ *.parquet` |
| **Silver — Quản lý bảng** | **Iceberg** (table format) | Biến thư mục parquet thành bảng có transaction: `MERGE` 1 hóa đơn sửa chỉ ghi 1 file mới + manifest, `snapshot` rollback | `metadata.json` + `manifest` trên MinIO |
| **Silver — Query & dbt** | **Trino** (engine cho dbt) + **dbt** (quản lý SQL, `incremental`, `test`, `docs`) | `dbt run --select silver` sinh `MERGE INTO lake.silver.*`, Trino thực thi trên Iceberg; ad-hoc `SELECT * FROM silver WHERE purchase_date='...'` pushdown chỉ scan 1 file | Đọc Iceberg qua manifest, không kéo cả 70M về worker |
| **Gold — Tổng hợp** | **Spark SQL** `GROUP BY purchase_date, category_code` | Agg Silver 70M → Gold 1.8k dòng | `INSERT INTO ClickHouse gold.mart_*` |
| **Gold — Lưu & Cache** | **ClickHouse** (`MergeTree ORDER BY (purchase_date, category_code)`) + **Redis** (TTL 1h) | Gold nhỏ, cần <30ms, QPS cao | ClickHouse `gold.*` + Redis `GET mart_daily_sales:2026-01` |
| **Điều phối** | **Airflow** (DAG `hourly: bronze→silver`, `daily 02:00: silver→gold`, `weekly: OPTIMIZE`) | `S3KeySensor`, `spark_submit`, `dbt run`, `dbt test`, `OPTIMIZE` | — |
| **Serving** | **FastAPI** → Gold only | Text-to-SQL / Forecast / Combo không scan Silver | <30ms (ClickHouse) / <5ms (Redis hit) |

> **Khi nào cần Iceberg/Trino/dbt?** Dưới ~20M và chỉ append (không sửa OCR) thì **plain partitioned parquet** (`mode("append").partitionBy(...)`) + Spark/Python đã append được, chưa cần Iceberg/Trino/dbt. Trên 20M hoặc cần `MERGE/DELETE` khi sửa OCR thì mới cần.

## 4. Luồng Incremental — Ảnh Hóa Đơn Mới

```
Ảnh JPG/PNG (upload, ~1s/ảnh)
  → Gemini Vision → JSON OCR (invoice_id, purchase_datetime, store_code, items[])
  → validator (check total_amount, ocr_confidence) → SKU mapper (name → item_no)
  → MinIO: s3://lake/bronze/receipts/purchase_date=2026-10-12/005.parquet
       (1 row = 1 JSON OCR, zstd, append = thêm file)

Airflow hourly — bronze → silver (incremental, partition purchase_date):
  Spark/Trino đọc  s3://lake/bronze/receipts/purchase_date={{ds}}/*.parquet  (chỉ ngày {{ds}}, không đọc 10GB cũ)
    → explode items → JOIN products (broadcast 3062) → MERGE INTO lake.silver.invoice_items
  Ghi: s3://lake/silver/invoice_items/purchase_date=2026-10-12/00002.parquet (5MB) + Iceberg manifest  (<2s, không đụng 9.9GB cũ)

Airflow daily 02:00 — silver → gold:
  Spark đọc  s3://lake/silver/invoice_items/purchase_date={{ds}}/*.parquet
    → GROUP BY purchase_date, category_code → INSERT INTO ClickHouse gold.mart_daily_sales
  + FP-Growth batch → gold.mart_combo_rules (precompute, không chạy trong request)
```

## 5. Danh Mục Bảng (ví dụ tên, có thể đổi)

| Bảng (ví dụ) | Khóa | Cột chính | Dòng (20M) | Partition | Lưu |
|--------------|------|-----------|------------|-----------|-----|
| `categories` | `category_code PK` | `category_name, level (1/2), parent_code, root_code` | 92 | Không | MinIO Bronze → Silver (1 file) |
| `products` | `item_no PK` | `name, brand_name, category_code FK, category_name, final_price, uom_name` | 3062 | Không | MinIO Bronze → Silver (1 file) |
| `stores` | `store_code PK` | `store_name, region` | 7 | Không | MinIO Silver (seed) |
| `raw_receipts` | `invoice_id PK` | `extracted_json` (JSON gốc), `ocr_confidence` | N | `purchase_date` | MinIO Bronze (audit) |
| `invoices` | `invoice_id PK` | `purchase_datetime, purchase_date, store_code FK, cashier_id, total_discount, total_amount, item_count` | 20M | `purchase_date` | **MinIO + Iceberg** Silver |
| `invoice_items` | `(invoice_id, line_no) PK` | `item_no FK (NULL nếu unmatched), product_name_raw, quantity, unit_price, discount, line_total, match_status` | ~70M | `purchase_date` | **MinIO + Iceberg** Silver |
| `mart_daily_sales` | `(purchase_date, category_code)` | `total_qty, revenue, invoice_cnt` | ~1.8k | Không (ClickHouse) | **ClickHouse Gold** |
| `mart_combo_rules` | `(antecedent, consequent)` | `support, confidence, lift` | ~5k | Không | **ClickHouse Gold** |

- `match_status`: `exact` / `normalized` / `unmatched`.
- `purchase_date` (YYYY-MM-DD) là cột partition Silver, cũng là `ORDER BY` trong ClickHouse Gold.

## 6. Orchestration (Airflow)

```
DAG: ingestion  (hourly: Silver, daily: Gold, weekly: compact)

hourly_silver (mỗi giờ):
  S3KeySensor(s3://lake/bronze/receipts/purchase_date={{ds}}/*)
    → spark_submit — bronze/{{ds}} → silver/invoice_items/purchase_date={{ds}}/ (Spark, broadcast JOIN, Iceberg MERGE)
    → dbt run --select silver  (nếu dùng dbt-trino: incremental, unique_key=['invoice_id','line_no'], partition_by=['purchase_date'])
    → dbt test  (unique, not_null, relationships)

daily_gold (02:00):
  Iceberg snapshot sensor
    → spark_submit — GROUP BY purchase_date, category_code → INSERT INTO ClickHouse gold.mart_daily_sales
    → spark_submit — FP-Growth → gold.mart_combo_rules
    → redis_invalidate — DEL mart_daily_sales:*

weekly_compact (Chủ nhật 03:00):
  → Iceberg: CALL system.rewrite_data_files(table=>'silver.invoice_items', strategy=>'sort', sort_order=>'purchase_date')
  → ClickHouse: OPTIMIZE TABLE gold.mart_daily_sales FINAL
```

Dưới 5 model: bỏ `dbt`, dùng `PythonOperator` + `spark.sql()` trong Airflow là đủ gọn. Trino chỉ cần nếu muốn ad-hoc `SELECT * FROM silver` không qua ClickHouse.

## 7. Hiệu Năng (20M ≈ 70M dòng fact, 10GB)

| Thao tác | Silver (MinIO + Iceberg) | Gold (ClickHouse) |
|----------|--------------------------|-------------------|
| 1 ảnh mới → Silver | 1 file 50KB + manifest, **<2s** | — |
| 1000 ảnh/giờ (batch) | 1 file 5MB, **2–5s** | — |
| Build Gold daily (GROUP BY 1 partition ~100k dòng) | — | **<10s** |
| AI: `doanh thu tháng 1?` | — | **15–30ms** / **<5ms** (Redis hit) |
| Drill-down `SELECT * FROM invoice_items LIMIT 10` | **200–400ms** (Trino, 1 partition) | — |

> Nếu Silver là **1 file parquet 700MB không partition** thì append phải đọc/ghi lại cả file → **30–60s**. Partition là bắt buộc.

## 8. Query Mẫu (chỉ đọc Gold, không đọc Silver runtime)

```sql
-- Doanh thu theo ngày + category (Gold, <30ms)
SELECT purchase_date, category_code, revenue FROM gold.mart_daily_sales GROUP BY 1,2;

-- Combo đã precompute
SELECT antecedent, consequent, support, confidence FROM gold.mart_combo_rules WHERE antecedent = 'MENU01145' ORDER BY lift DESC LIMIT 10;

-- Sản phẩm rẻ nhất
SELECT item_no, name, final_price FROM products WHERE category_code = 'MENU01133' ORDER BY final_price LIMIT 5;
```
