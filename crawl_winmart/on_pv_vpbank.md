# SỔ TAY ÔN PHỎNG VẤN DATA ENGINEER – ONSITE VPBANK

> **Bản đọc và ôn trực tiếp, tiếng Việt.** Trọng tâm: (I) kiến thức nền Data Engineering; (II) sáu dự án trong CV; (III) hai JD Takumi Solutions và Alphaway cùng tuyển onsite VPBank; (IV) ngân hàng, tình huống vận hành, thiết kế hệ thống; (V) bộ câu hỏi–đáp án theo mức độ Junior/Middle.
>
> **Không có lịch học/lộ trình.** Mỗi mục được viết theo cấu trúc: **bản chất → ví dụ → lỗi hay gặp → câu hỏi phỏng vấn → cách trả lời**.
>
> **Lưu ý về tính xác thực:** Các chi tiết dự án bên dưới lấy từ CV/tài liệu và nội dung người ứng tuyển đã mô tả. Chúng không có nghĩa người ứng tuyển trực tiếp triển khai toàn bộ giải pháp của dự án. Trong phỏng vấn, chỉ dùng ngôi “em đã làm” cho những việc thực sự đã thực hiện; các giải pháp mở rộng, ví dụ minh họa được đánh dấu riêng. Không đưa mốc thời gian hay thành tích chưa được xác minh vào câu trả lời.

---

## MỤC LỤC

- [A. Đọc hai JD và định vị vị trí](#a-đọc-hai-jd-và-định-vị-vị-trí)
- [B. Kiến thức nền Data Engineering](#b-kiến-thức-nền-data-engineering)
  - [1. Bức tranh tổng thể](#1-bức-tranh-tổng-thể)
  - [2. ETL, ELT, incremental, CDC, idempotency](#2-etl-elt-incremental-cdc-idempotency)
  - [3. SQL từ cơ bản đến nâng cao](#3-sql-từ-cơ-bản-đến-nâng-cao)
  - [4. Oracle và SQL Performance Tuning](#4-oracle-và-sql-performance-tuning)
  - [5. RDBMS, Transaction và Data Modeling](#5-rdbms-transaction-và-data-modeling)
  - [6. ODS, DWH, Data Lake, Lakehouse](#6-ods-dwh-data-lake-lakehouse)
  - [7. Spark, Spark SQL, PySpark](#7-spark-spark-sql-pyspark)
  - [8. Apache Airflow](#8-apache-airflow)
  - [9. Python dành cho Data Engineer](#9-python-dành-cho-data-engineer)
  - [10. dbt](#10-dbt)
  - [11. Kafka và Streaming](#11-kafka-và-streaming)
  - [12. Data Quality, testing, monitoring](#12-data-quality-testing-monitoring)
  - [13. Trino, MinIO, Parquet, Iceberg](#13-trino-minio-parquet-iceberg)
  - [14. Docker, Kubernetes, OpenShift, Linux, Git, CI/CD](#14-docker-kubernetes-openshift-linux-git-cicd)
- [C. Giải thích sâu sáu dự án trong CV](#c-giải-thích-sâu-sáu-dự-án-trong-cv)
- [D. Kiến thức riêng theo hai JD VPBank](#d-kiến-thức-riêng-theo-hai-jd-vpbank)
- [E. Phỏng vấn giả lập: Câu hỏi và đáp án](#e-phỏng-vấn-giả-lập-câu-hỏi-và-đáp-án)
- [F. Bài SQL, Spark và thiết kế pipeline tự luyện](#f-bài-sql-spark-và-thiết-kế-pipeline-tự-luyện)
- [G. Thuật ngữ, bẫy phỏng vấn và nguồn tham khảo](#g-thuật-ngữ-bẫy-phỏng-vấn-và-nguồn-tham-khảo)

---

# A. ĐỌC HAI JD VÀ ĐỊNH VỊ VỊ TRÍ

## A1. Thông tin rút trực tiếp từ các JD đã gửi

| Nội dung | Takumi Solutions – Data Engineer | Alphaway – Data Engineer |
|---|---|---|
| Khách hàng | VPBank – Banking & Finance | Làm việc tại VPBank Tower |
| Địa điểm | 89 Láng Hạ, Hà Nội | 89 Láng Hạ, Hà Nội |
| Mức kinh nghiệm trong văn bản | Từ 2 năm; gọi Middle Level | Từ 3 năm |
| Ngân sách trong văn bản | Up to 30 triệu đồng/tháng, **không nói rõ net hay gross** | Thỏa thuận |
| Nhiệm vụ | Thiết kế/vận hành pipeline, ETL/ELT, DWH/Data Lake, batch/streaming, SQL tuning, quality, monitoring, tài liệu | Phân tích yêu cầu cùng nghiệp vụ, tham gia giải pháp tổng thể/chi tiết, chủ động nghiên cứu tối ưu |
| Bắt buộc/ưu tiên | Banking bắt buộc, SQL, Python/Java/Scala, DWH, Spark/Kafka/Airflow/Hadoop | Banking data model, Oracle/SQL Server/PostgreSQL/DB2/Redshift; DWH/Lakehouse/Data Product; Python/SQL/Spark; dbt/Kafka/ODI/Datastage/AWS |
| Điểm dễ hỏi nhất | Tự xử lý pipeline, SQL/ETL, batch/streaming và vận hành | Data Modeling, kiến trúc, DWH/Lakehouse, banking nghiệp vụ và phương án tối ưu |

**Không suy diễn:** Cùng địa điểm và cùng khách hàng không chứng minh hai vendor tuyển cùng team, cùng sản phẩm dữ liệu hay cùng người phỏng vấn. Kiến thức nền có thể dùng chung, nhưng nên hỏi từng bên stack thực tế và phạm vi nhiệm vụ.

## A2. Những gì người phỏng vấn cần nhìn thấy

Một kỹ sư được kỳ vọng ở cấp Junior/Middle cần vượt qua câu hỏi “em biết công nghệ X không?” bằng bốn lớp năng lực:

1. **Nền tảng:** Hiểu khái niệm, dữ liệu, kiến trúc và các giới hạn.
2. **Thực hành:** Biết viết SQL/Python/Spark, vận hành DAG, đọc log, kiểm thử.
3. **Debug & tối ưu:** Có phương pháp điều tra khi pipeline chậm, fail, sai dữ liệu hoặc OOM.
4. **Phối hợp:** Chuyển yêu cầu nghiệp vụ thành mapping, model, test case và runbook.

Cách trả lời mạnh: **Nêu mục đích → nêu cách làm → nêu rủi ro/trade-off → ví dụ thực tế bạn đã làm hoặc giả định được phân biệt rõ**.

# B. KIẾN THỨC NỀN DATA ENGINEERING

## 1. Bức tranh tổng thể

### 1.1. Data Engineer làm gì?

Data Engineer xây dựng và vận hành đường đi của dữ liệu từ các hệ thống nguồn đến kho dữ liệu và hệ thống khai thác. Các bước có thể là:

```text
Core Banking / CRM / SQL Server / Oracle / API / Excel / Kafka
                      |
                 INGESTION
               Python/CDC/JDBC
                      |
              RAW / LANDING
       MinIO / Object Storage / Staging
                      |
              TRANSFORMATION
           Spark SQL / SQL / dbt
                      |
              SILVER / CURATED
       chuẩn hóa, map key, kiểm tra dữ liệu
                      |
                 GOLD / MART
           Fact, Dimension, KPI
                      |
            BI / CRM / Analytics / ML

Airflow: điều phối | Monitoring: theo dõi | Data Quality: kiểm định
```

Một pipeline không nhất thiết phải có đủ tất cả tầng. Tên Raw, Bronze, Staging, Silver, Gold, Sharing là lựa chọn kiến trúc, phải làm rõ ý nghĩa trong dự án cụ thể.

### 1.2. DE / DA / DS / Architect

- **DE:** Data ingestion, ETL/ELT, lưu trữ, chất lượng, tối ưu, vận hành.
- **DA/BI:** SQL phân tích, số liệu kinh doanh, dashboard/KPI.
- **DS/ML Engineer:** Mô hình thống kê/ML, huấn luyện, serving và đánh giá tùy vai trò.
- **Data Architect:** Kiến trúc, chuẩn dữ liệu, governance, mô hình hóa, tiêu chuẩn tích hợp.

**Hỏi:** “Làm Data Engineer có cần hiểu nghiệp vụ không?” – **Có**. Nếu không hiểu định nghĩa “doanh số”, “ngày hạch toán”, “giao dịch hợp lệ”, có thể viết SQL đúng cú pháp nhưng báo cáo sai nghiệp vụ.

### 1.3. Batch / Micro-batch / Streaming

- **Batch:** Xử lý lô dữ liệu đã tích lũy (ví dụ báo cáo EOD).
- **Micro-batch:** Xử lý lô nhỏ định kỳ, tạo cảm giác gần thời gian thực; ví dụ một chế độ Structured Streaming.
- **Continuous/event streaming:** Xử lý dòng sự kiện trong khi dữ liệu phát sinh; vẫn cần checkpoint, semantics và xử lý sự kiện đến muộn.

Không phải mọi ngân hàng đều cần streaming cho báo cáo cuối ngày. Streaming tăng khả năng cập nhật nhanh nhưng làm phức tạp ordering, duplicate, state và recovery.

### 1.4. Data lifecycle và tiêu chí của pipeline tốt

**Correctness** (đúng), **Completeness** (đủ), **Freshness** (kịp thời), **Reliability** (ổn định), **Scalability** (mở rộng), **Observability** (quan sát được), **Security** (an toàn), **Cost efficiency** (chi phí hợp lý), **Maintainability** (dễ bảo trì).

**Câu hỏi:** “Đâu là điều quan trọng nhất trong pipeline ngân hàng?” – Không có một chỉ tiêu duy nhất; dữ liệu tài chính đặc biệt coi trọng chính xác, đối soát, lịch sử, truy vết, bảo mật và SLA. Không nên hy sinh đúng dữ liệu chỉ để job chạy nhanh.

---

## 2. ETL, ELT, incremental, CDC, idempotency

### 2.1. ETL vs ELT

- **ETL – Extract, Transform, Load:** Lấy dữ liệu, xử lý trước, ghi về đích. Ví dụ nguồn Excel → Python chuẩn hóa → PostgreSQL.
- **ELT – Extract, Load, Transform:** Đưa dữ liệu vào tầng đích/landing trước, sau đó dùng SQL/dbt/Spark để biến đổi tại nền tảng dữ liệu.
- Một hệ thống có thể dùng cả hai: Python làm parsing Excel, MinIO giữ raw, PostgreSQL Staging, dbt transform Silver.

**Hỏi “khi nào ETL, khi nào ELT?”** – Dựa trên engine xử lý, định dạng nguồn, chi phí tải, yêu cầu dữ liệu nhạy cảm, khả năng lưu raw, vận hành và kiểm thử.

### 2.2. Full Load, Incremental Load, CDC

**Full load:** Đọc/nạp toàn bộ dữ liệu. Dễ hiểu nhưng tốn thời gian/tài nguyên khi bảng rất lớn.

**Incremental:** Chỉ lấy phần mới/thay đổi. Các cách phổ biến: cột `updated_at`, sequence/incrementing ID, timestamp + tie-breaker, partition ngày, hoặc CDC.

**CDC (Change Data Capture):** Thu nhận INSERT/UPDATE/DELETE từ hệ nguồn; log-based CDC đọc log giao dịch khi hệ quản trị và connector hỗ trợ. CDC không đồng nghĩa Kafka: Kafka có thể là bus sự kiện vận chuyển dữ liệu CDC.

SQL minh họa lấy snapshot theo watermark:

```sql
SELECT transaction_id, customer_id, amount, updated_at
FROM source_transactions
WHERE updated_at > :last_committed_watermark
  AND updated_at <= :current_safe_watermark;
```

**Bẫy:** Nếu nhiều dòng có cùng timestamp, dấu `>` có thể bỏ sót bản ghi. Có thể dùng watermark cặp `(updated_at, unique_id)`, cửa sổ overlap + dedup, hoặc CDC tùy thiết kế. Dữ liệu đến muộn và hard delete cần giải pháp riêng.

### 2.3. Idempotency – chạy lại không tạo hiệu ứng sai

Giả sử tải dữ liệu ngày 25/10 đã ghi xong nhưng task fail trước khi lưu trạng thái. Retry bằng INSERT thuần có thể ghi trùng.

Các cơ chế thường dùng:

- **MERGE/UPSERT:** Cập nhật theo business/unique key.
- **Partition overwrite:** Ghi lại cả một partition nếu đáp ứng yêu cầu và có khả năng commit an toàn.
- **Transactional staging:** Ghi vào bảng tạm, validate, rồi swap/merge.
- **Deduplication:** Dùng `ROW_NUMBER` hoặc unique constraint theo khóa phù hợp.
- **Checkpoint/watermark commit:** Chỉ cập nhật mốc sau khi load và kiểm tra hoàn tất.

Ví dụ PostgreSQL:

```sql
INSERT INTO target_transactions(transaction_id, amount, updated_at)
VALUES ('T1', 100000, CURRENT_TIMESTAMP)
ON CONFLICT (transaction_id)
DO UPDATE SET
  amount = EXCLUDED.amount,
  updated_at = EXCLUDED.updated_at;
```

Điều kiện: `transaction_id` phải có unique constraint phù hợp. **Chỉ INSERT ON CONFLICT không thay thế kiểm tra đúng/sai nghiệp vụ**.

### 2.4. Late-arriving data, lookback, backfill

- **Late-arriving:** Dữ liệu phát sinh trước nhưng đến muộn hoặc bị sửa sau khi pipeline đã xử lý.
- **Lookback window:** Mỗi lần chạy đọc lại một khoảng thời gian gần đây để bắt cập nhật muộn, rồi MERGE/dedup.
- **Backfill:** Chạy dữ liệu lịch sử hoặc khoảng thời gian bị thiếu.
- **Data interval / business date:** Kỳ dữ liệu xử lý, khác thời điểm hệ thống đang chạy; khi backfill không được cứ dùng `datetime.now()`.

**Hỏi:** “Job ngày 26/10 lỗi, hôm sau chạy lại thế nào?” – Xác định kỳ dữ liệu, trạng thái target, checkpoint, tính idempotent, backfill kỳ lỗi và đối soát trước khi đóng sự cố.

### 2.5. Exactly-once khó ở đâu?

“Message được đọc một lần” khác “tác động lên database xuất hiện đúng một lần”. Có thể Kafka consumer ghi DB thành công nhưng chết trước khi commit offset, dẫn đến đọc lại. Dùng idempotent sink, unique key/transaction hoặc cơ chế bảo đảm xuyên hệ thống tùy connector.

### 2.6. Source-to-target mapping

Ví dụ:

| Nguồn | Đích | Rule | Test |
|---|---|---|---|
| `cust.cust_id` | `customer_id` | CAST/trim | NOT NULL, unique theo grain |
| `cust.full_name` | `customer_name` | TRIM, chuẩn Unicode | Không mất tên hợp lệ |
| `txn.txn_date` | `posting_date` | Chọn ngày theo business rule | Không sai kỳ báo cáo |
| `txn.amount` | `amount_vnd` | Đổi theo tỷ giá đúng ngày, nếu được yêu cầu | So sánh tổng/định lượng |

Một tài liệu mapping tốt chỉ ra nguồn, cột, kiểu dữ liệu, key, JOIN, filter, xử lý NULL, lịch sử, quy tắc nghiệp vụ, mẫu test và đầu ra.

**Q&A nhanh**

1. **ETL lỗi trước Load?** Khắc phục và chạy lại bước tương ứng; lưu raw/metadata để tái xử lý.
2. **ETL lỗi sau Load?** Kiểm tra ghi một phần, commit và idempotency trước retry.
3. **Incremental dùng created_at đủ không?** Không nếu cần bắt UPDATE/DELETE.
4. **Giữ Raw để làm gì?** Audit, reprocess, debug và lineage.
5. **Khi nào dùng CDC?** Khi cần đồng bộ thay đổi thường xuyên, có hỗ trợ nguồn và phù hợp SLA.
6. **Reconciliation là gì?** Đối soát đầu–cuối theo row count, key, tổng tiền, business rule, không chỉ nhìn trạng thái task.

---

## 3. SQL từ cơ bản đến nâng cao

### 3.1. Thứ tự logic SQL

Thứ tự logic khái quát: `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT/FETCH` (chi tiết có thể khác theo dialect và Window processing). Phân biệt `WHERE` lọc trước tổng hợp và `HAVING` lọc sau tổng hợp.

```sql
SELECT branch_id, SUM(amount) AS total_amount
FROM transactions
WHERE status = 'SUCCESS'
GROUP BY branch_id
HAVING SUM(amount) > 1000000
ORDER BY total_amount DESC;
```

### 3.2. JOIN và cardinality (số lượng bản ghi)

| JOIN | Kết quả |
|---|---|
| INNER | Chỉ dòng khớp |
| LEFT | Giữ tất cả dòng trái, bổ sung dòng khớp phải |
| RIGHT | Giữ tất cả dòng phải |
| FULL | Giữ cả hai phía |
| CROSS | Tích Descartes |
| SEMI | Giữ bản ghi trái có match |
| ANTI | Giữ bản ghi trái không match |

**Bẫy quan trọng nhất:** JOIN 1:N có thể nhân bản dòng của bảng trái. JOIN fact giao dịch với lịch sử địa chỉ khách hàng mà không lọc đúng phiên bản có thể nhân tổng tiền. Cần xác định **grain**, tính duy nhất của key và SCD effective-date.

```sql
-- Khách hàng chưa có giao dịch; kiểm tra txn_id không null theo schema
SELECT c.customer_id
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM transactions t
  WHERE t.customer_id = c.customer_id
);
```

### 3.3. NULL, COUNT, DISTINCT

- `NULL = NULL` không trả TRUE; kiểm tra `IS NULL`.
- `COUNT(*)` đếm dòng; `COUNT(col)` bỏ NULL.
- `COALESCE(x,0)` chỉ nên dùng khi nghiệp vụ cho phép coi NULL = 0.
- `NOT IN (subquery)` có thể gặp bẫy NULL; `NOT EXISTS` thường dễ kiểm soát hơn.
- `DISTINCT` có thể che vấn đề JOIN sai; không phải cách tối ưu thay cho kiểm tra cardinality.

### 3.4. Window Function

| Hàm | Đặc điểm |
|---|---|
| `ROW_NUMBER()` | Đánh số mỗi dòng, không đồng hạng |
| `RANK()` | Đồng hạng, nhảy số |
| `DENSE_RANK()` | Đồng hạng, không nhảy số |
| `LAG/LEAD` | Lấy giá trị hàng trước/sau |
| `SUM(...) OVER` | Tổng theo cửa sổ, giữ dòng chi tiết |
| `FIRST_VALUE/LAST_VALUE` | Giá trị đầu/cuối theo frame; chú ý mặc định frame |

```sql
-- Giao dịch mới nhất mỗi khách hàng, có tie-breaker xác định
WITH ranked AS (
 SELECT t.*,
        ROW_NUMBER() OVER (
          PARTITION BY customer_id
          ORDER BY transaction_time DESC, transaction_id DESC
        ) rn
 FROM transactions t
)
SELECT * FROM ranked WHERE rn = 1;
```

```sql
-- 3 giao dịch lớn nhất mỗi khách hàng
WITH x AS (
  SELECT t.*,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY amount DESC, transaction_id
         ) rn
  FROM transactions t
)
SELECT * FROM x WHERE rn <= 3;
```

**Phân biệt:** Nếu muốn lấy tất cả giao dịch đồng hạng top 3 giá trị, có thể cần `DENSE_RANK`, không phải `ROW_NUMBER`.

### 3.5. CTE vs Subquery vs Temp Table

- **CTE (`WITH`)**: Đặt tên tập kết quả logic giúp SQL dễ đọc; không bảo đảm luôn materialize hay nhanh hơn.
- **Subquery**: Truy vấn con nằm trong truy vấn chính.
- **Temp Table**: Lưu kết quả trung gian trong phạm vi tùy DB, có chi phí ghi/đọc và lợi ích tái sử dụng.
- **View**: Logic truy vấn được lưu, thường không lưu kết quả vật lý.
- **Materialized View/Table**: Lưu kết quả đã tính để tối ưu truy vấn lặp, cần refresh đúng.

### 3.6. GROUP BY vs Window

`GROUP BY` giảm số dòng theo nhóm; Window Function có thể giữ nguyên grain từng dòng.

```sql
-- Tổng theo khách, vẫn giữ từng giao dịch
SELECT transaction_id, customer_id, amount,
       SUM(amount) OVER (PARTITION BY customer_id) customer_total
FROM transactions;
```

### 3.7. DELETE/TRUNCATE/DROP

- `DELETE`: Xóa dòng theo điều kiện, transaction semantics tùy DB.
- `TRUNCATE`: Xóa nhanh toàn bảng theo cách DB hỗ trợ, thường DDL hoặc có hành vi transaction riêng.
- `DROP`: Xóa object.

Không khẳng định mọi DB hỗ trợ rollback TRUNCATE như nhau. Trong Oracle, DDL thường implicit commit.

### 3.8. Các bẫy SQL khi làm ngân hàng

- SUM số dư snapshot sau khi JOIN bảng giao dịch → nhân số dư.
- Đổi `LEFT JOIN` thành `INNER JOIN` → mất khách hàng không có giao dịch.
- Dùng `date(transaction_time)` trên cột partition/index → có thể cản pruning/access path.
- Chọn sai transaction date vs posting date → lệch số liệu kỳ.
- `FLOAT` cho tính tiền → có nguy cơ sai số; ưu tiên `DECIMAL` theo business rule.
- Dữ liệu giao dịch có reversal/cancelled → phải lọc theo nghiệp vụ.
- Đồng thời source thay đổi giữa hai lần kiểm tra → reconciliation cần cùng snapshot/cut-off.

### 3.9. Bài SQL truy vấn mẫu và đáp án

**Bài 1. Tìm khách hàng có tổng giao dịch thành công > 100 triệu:**

```sql
SELECT customer_id, SUM(amount) total_amount
FROM transactions
WHERE status = 'SUCCESS'
GROUP BY customer_id
HAVING SUM(amount) > 100000000;
```

**Bài 2. Tìm bản ghi trùng theo business key:**

```sql
SELECT transaction_id, COUNT(*) cnt
FROM staging_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;
```

**Bài 3. Phát hiện giao dịch có khách hàng không có trong dimension:**

```sql
SELECT f.transaction_id
FROM fact_transaction f
LEFT JOIN dim_customer d
  ON f.customer_key = d.customer_key
WHERE d.customer_key IS NULL;
```

**Bài 4. So sánh tổng tiền Source–Target theo ngày:**

```sql
WITH s AS (
 SELECT business_date, COUNT(*) cnt, SUM(amount) total
 FROM src_txn GROUP BY business_date
), t AS (
 SELECT business_date, COUNT(*) cnt, SUM(amount) total
 FROM tgt_txn GROUP BY business_date
)
SELECT COALESCE(s.business_date,t.business_date) business_date,
       s.cnt AS source_count, t.cnt AS target_count,
       s.total AS source_total, t.total AS target_total
FROM s FULL OUTER JOIN t ON s.business_date=t.business_date
WHERE COALESCE(s.cnt,-1) <> COALESCE(t.cnt,-1)
   OR COALESCE(s.total,0) <> COALESCE(t.total,0);
```

Trong production, đối soát tổng `DECIMAL`, cách xử lý NULL/không có dòng, loại giao dịch và cut-off phải thống nhất; truy vấn trên chỉ là minh họa.

**Bài 5. Top doanh số chi nhánh theo tháng:**

```sql
WITH monthly AS (
 SELECT DATE_TRUNC('month', transaction_date) AS month_start,
        branch_id, SUM(amount) revenue
 FROM transactions
 WHERE status='SUCCESS'
 GROUP BY DATE_TRUNC('month', transaction_date), branch_id
), ranked AS (
 SELECT monthly.*,
        DENSE_RANK() OVER(PARTITION BY month_start ORDER BY revenue DESC) rnk
 FROM monthly
)
SELECT * FROM ranked WHERE rnk <= 3;
```

Cú pháp `DATE_TRUNC` khác giữa PostgreSQL, Oracle, Spark SQL; trước phỏng vấn phải nói rõ dialect.

### 3.10. Phỏng vấn SQL: hỏi nhanh – trả lời chuẩn

1. **WHERE vs HAVING?** WHERE lọc trước aggregation; HAVING lọc nhóm sau GROUP BY.
2. **UNION vs UNION ALL?** UNION loại bản ghi trùng và có thể tốn chi phí; ALL giữ tất cả.
3. **INNER vs LEFT?** INNER bỏ dòng không match; LEFT giữ dòng bảng trái.
4. **EXISTS vs IN?** Cùng có thể diễn đạt membership; NULL và optimizer/dialect tạo khác biệt; không khẳng định một cái luôn nhanh hơn.
5. **CTE nhanh hơn subquery?** Không mặc định; xem plan.
6. **Index có luôn nhanh?** Không; có overhead write/storage và full scan có thể phù hợp.
7. **Sự khác nhau COUNT(*)/COUNT(col)?** COUNT(col) bỏ NULL.
8. **Vì sao DISTINCT nguy hiểm sau JOIN?** Có thể che join explosion hoặc xóa những dòng nghiệp vụ hợp lệ.
9. **ROW_NUMBER vs DENSE_RANK?** Một bản ghi mỗi thứ hạng so với có đồng hạng.
10. **Khi nào cần surrogate key?** Trong DWH/SCD để định danh từng phiên bản Dimension.
11. **SQL injection là gì?** Nhúng câu lệnh không mong muốn; dùng parameterized query, không nối chuỗi input.
12. **Isolation level có ảnh hưởng query?** Có; quyết định snapshot/visibility và một số anomaly đồng thời.

---

## 4. Oracle và SQL Performance Tuning

### 4.1. Optimizer và Execution Plan

Oracle CBO (Cost-Based Optimizer) ước lượng phương án thực thi dựa trên thống kê và chọn access path/join strategy. **Cost là ước lượng tương đối**, không phải mili-giây thực tế.

Thao tác cần hiểu:

| Operator | Ý nghĩa và lưu ý |
|---|---|
| `TABLE ACCESS FULL` | Đọc bảng; không phải mặc định xấu |
| `INDEX RANGE SCAN` | Quét khoảng giá trị index |
| `INDEX UNIQUE SCAN` | Tra cứu bằng khóa unique |
| `NESTED LOOPS` | Thường hiệu quả nếu outer nhỏ và inner truy cập tốt |
| `HASH JOIN` | Hữu ích với join tập dữ liệu lớn, cần bộ nhớ cho hash |
| `MERGE JOIN` | Kết hợp hai tập dữ liệu theo thứ tự đã sắp |
| `SORT ORDER BY` | Sắp xếp, có thể spill temp |
| `HASH GROUP BY` | Aggregation sử dụng hash |
| `TEMP TABLE TRANSFORMATION` | Kế hoạch có materialization trung gian |

```sql
EXPLAIN PLAN FOR
SELECT * FROM transactions
WHERE customer_id = :cust_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Muốn xem runtime plan/statistics khi có quyền và thống kê phù hợp:

```sql
SELECT * FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST')
);
```

Chú ý `DISPLAY_CURSOR(NULL, NULL, ...)` dùng cursor hiện hành theo ngữ cảnh session; khi dùng cần bảo đảm đúng SQL ID/cursor, quyền và thống kê đã được collect. Các thông số đáng biết: `E-Rows`, `A-Rows`, `Starts`, `Buffers`, `Reads`, `A-Time`, `TempSpc`.

### 4.2. Index – giải thích sâu

- **B-tree:** Phổ biến cho lọc/range theo khóa; composite index có thứ tự cột quan trọng.
- **Bitmap:** Phù hợp một số workload phân tích tương đối ít ghi và cột cardinality thấp, nhưng phải cẩn thận concurrent DML.
- **Function-based index:** Index theo biểu thức, ví dụ TRUNC(date), nếu đúng thiết kế.
- **Local/global index:** Liên quan partition table trong Oracle.

**Bẫy:** Composite `(customer_id, txn_date)` không có nghĩa mọi điều kiện chỉ lọc `txn_date` đều tận dụng tốt index theo cùng cách. Cần xem prefix, selectivity, optimizer và plan.

Ví dụ tránh áp dụng hàm lên cột ngày khi cần range scan:

```sql
-- Có thể khó dùng index thường trên transaction_date
WHERE TRUNC(transaction_date) = DATE '2026-10-26'

-- Điều kiện dạng range thường có lợi hơn cho index/pruning
WHERE transaction_date >= DATE '2026-10-26'
  AND transaction_date <  DATE '2026-10-27'
```

### 4.3. Join strategy và thống kê

**Hash Join vs Nested Loops:** Không chọn bằng cảm tính. Phụ thuộc số dòng, selectivity, index, I/O, memory, cách phân bố dữ liệu và join predicate. Nếu ước lượng E-Rows chênh lệch lớn A-Rows, rất có thể thống kê/cardinality estimation dẫn đến plan chưa phù hợp.

### 4.4. Tối ưu báo cáo chậm theo quy trình 7 bước

1. Lấy SQL/procedure, input parameter, volume, runtime baseline và SLA.
2. Xác định SQL ID/cursor, execution plan thực tế, các bước tiêu tốn CPU/I/O/Temp/Memory.
3. Kiểm tra partition, index, statistics, join cardinality, filter, implicit cast và function trên indexed columns.
4. Cô lập subquery hoặc phép JOIN/aggregation nặng; xem có scan lặp, join explosion, row-by-row logic.
5. Thử viết lại SQL, giảm cột/dòng sớm, sử dụng summary/temp table hoặc index khi hợp lý.
6. So sánh performance trước–sau trong điều kiện tương đương (cache, bind variables, volume, concurrency).
7. So sánh **đầu ra dữ liệu** trước–sau theo row count, key, số tổng, giá trị NULL, kỳ nghiệp vụ; ghi log thay đổi và test SIT/UAT khi cần.

### 4.5. PL/SQL: Procedure, Function, Package, Cursor, Exception

- **Procedure:** Chạy tác vụ, có thể có IN/OUT/IN OUT parameter.
- **Function:** Trả giá trị qua RETURN; dùng trong SQL có ràng buộc về hành vi phù hợp.
- **Package:** Gom các routine/type/constant liên quan, chia specification/body.
- **Cursor:** Duyệt tập kết quả; cần tránh row-by-row bất lợi khi có thể dùng set-based operations.
- **Exception:** Xử lý lỗi PL/SQL; cần log và raise đúng mức, không im lặng bỏ qua lỗi.
- **Commit/Rollback:** Xác định ranh giới transaction; không tùy tiện commit bên trong các procedure thuộc pipeline lớn nếu làm mất khả năng rollback logic tổng thể.

### 4.6. Temporary table và Materialization

Tạm lưu kết quả của một JOIN/aggregation nặng có thể hữu ích nếu bước sau dùng đi dùng lại hoặc optimizer được lợi từ chia nhỏ logic. Nhưng có overhead TEMP I/O, thống kê và synchronization. “Dùng bảng tạm giúp nhanh hơn” là giả thuyết phải benchmark.

### 4.7. Các ca hỏi đáp Oracle

1. **Full Table Scan luôn xấu?** Không, đọc tỷ lệ lớn của bảng có thể tối ưu hơn index.
2. **Index range scan mà query vẫn chậm?** Có thể nhiều rowid table lookups, join, sort, I/O hoặc thống kê lệch.
3. **Khi nào tạo index?** Khi mẫu truy vấn và dữ liệu cho thấy lợi ích lớn hơn overhead.
4. **Estimate Rows khác Actual Rows mạnh?** Xem thống kê và cardinality/selectivity, bind skew.
5. **SQL A và B logic giống nhau, làm sao chứng minh?** Reconciliation dữ liệu, test business edge cases, không chỉ so thời gian.
6. **Procedure compile không lỗi nhưng kết quả sai?** Compile chỉ bảo đảm cú pháp/phụ thuộc mức nhất định; cần logic test và đối soát.
7. **Báo cáo nhanh khi test nhưng chậm production?** Khác volume, concurrency, index/statistics, memory/caches, parameter distributions.
8. **Có nên tăng PGA ngay khi sort chậm?** Không trước khi phân tích plan, phân phối dữ liệu và tài nguyên.
9. **Index mới làm DML chậm?** Vì mỗi insert/update/delete có thể phải cập nhật index.
10. **SIT/UAT liên quan tuning ra sao?** Sau tối ưu phải bảo đảm đúng chức năng, định dạng và số liệu nghiệp vụ.

---
## 5. RDBMS, Transaction và Data Modeling

### 5.1. Relational Database: khái niệm cốt lõi

Một RDBMS quản lý dữ liệu dưới dạng các quan hệ (bảng), có schema, kiểu dữ liệu, constraint, transaction, index và cơ chế truy vấn SQL. Các hệ bạn ghi trong CV: Oracle, PostgreSQL, MySQL, SQL Server, ClickHouse, BigQuery — lưu ý **ClickHouse và BigQuery là hệ phân tích với kiến trúc khác RDBMS OLTP truyền thống**, không nên đánh đồng cách tối ưu.

- **PK (Primary Key):** Định danh duy nhất mỗi dòng theo constraint được DB thực thi.
- **FK (Foreign Key):** Ràng buộc quan hệ tham chiếu; một số hệ OLAP có semantics/khả năng enforce khác nhau.
- **Unique constraint:** Duy nhất theo nhóm cột, ngữ nghĩa NULL tùy DB.
- **Business Key:** Khóa định danh thực thể/giao dịch do nghiệp vụ định nghĩa.
- **Surrogate Key:** Khóa kỹ thuật do DWH gán, giúp quản lý SCD phiên bản.
- **Referential Integrity:** Không có quan hệ tham chiếu trái nguyên tắc đã định nghĩa.

### 5.2. ACID

- **Atomicity:** Transaction hoàn tất hoặc rollback theo ranh giới đã định.
- **Consistency:** Duy trì constraint/invariant hợp lệ.
- **Isolation:** Transaction đồng thời nhìn dữ liệu theo mức isolation được dùng.
- **Durability:** Commit bền vững theo bảo đảm hệ thống.

**Các hiện tượng:** Dirty Read, Non-repeatable Read, Phantom Read, Lost Update, Write Skew; phân biệt lý thuyết ANSI và hành vi thực tế theo DB/MVCC.

Ví dụ chuyển tiền: trừ tài khoản A, cộng B phải là transaction nghiệp vụ nhất quán. Trong DWH, các bước batch load và publication đôi khi cần cơ chế atomic staging/swap để dashboard không đọc dữ liệu nửa chừng.

### 5.3. Normalization: 1NF, 2NF, 3NF

- **1NF:** Cấu trúc thuộc tính nguyên tử theo thiết kế quan hệ, loại repeated groups.
- **2NF:** Ở 1NF, thuộc tính không khóa phụ thuộc đầy đủ vào toàn bộ khóa ứng viên, không chỉ một phần của composite key.
- **3NF:** Tránh phụ thuộc bắc cầu không cần thiết của thuộc tính không khóa thông qua thuộc tính khác.

**Denormalization** chấp nhận dư thừa để tăng tốc phân tích/truy vấn đọc: summary table, rộng hóa dimension, mart theo KPI. Không có quy tắc “cứ 3NF là tốt cho mọi DWH”.

### 5.4. OLTP vs OLAP

| OLTP | OLAP |
|---|---|
| Giao dịch online, đọc/ghi nhỏ, độ trễ thấp | Tổng hợp lịch sử, JOIN và scan nhiều dữ liệu |
| Nhiều thay đổi dữ liệu, transaction | Truy vấn phân tích đọc lớn, ETL batch |
| Thường chuẩn hóa cao | Thường Star Schema / columnar / preaggregate |
| Ví dụ Core Banking | DWH, BI, analytic warehouse |

**Vì sao không cho báo cáo nặng quét Core Banking?** Có thể tranh chấp CPU/I/O và ảnh hưởng giao dịch. Thực tế tùy ngân hàng, nhưng tách workload qua ODS/DWH/replica là mô hình thường gặp.

### 5.5. Fact/Dimension/Grain – phần hỏi nhiều

**Grain** là đơn vị chi tiết một dòng. Phải chốt grain trước khi thiết kế fact và JOIN.

- Fact transaction: 1 dòng = 1 giao dịch hợp lệ theo định nghĩa.
- Fact daily balance: 1 dòng = số dư 1 account tại 1 business_date.
- Fact monthly revenue: 1 dòng = một bộ `(month, branch, product)`.

Ví dụ Star Schema:

```text
      dim_customer       dim_date
             \             /
              fact_transaction
             /             \
       dim_branch       dim_product
```

Fact chứa các foreign keys và measure (`amount`, `transaction_count`); dimensions chứa thuộc tính thời gian, sản phẩm, phân khúc, chi nhánh. Grain không phù hợp dẫn đến duplicate count hoặc nhân tổng tiền.

### 5.6. Star vs Snowflake; Data Mart

- **Star Schema:** Fact trung tâm, Dimension ít chuẩn hóa, thân thiện BI.
- **Snowflake:** Các Dimension có thêm bảng chuẩn hóa liên quan, giảm dư thừa nhưng JOIN phức tạp hơn.
- **Data Mart:** Bộ dữ liệu con phục vụ nghiệp vụ cụ thể (Finance, Marketing, Risk, Sales).
- **Conformed Dimension:** Dimension dùng thống nhất giữa các fact/mart, giúp báo cáo nhất quán.

### 5.7. SCD (Slowly Changing Dimension)

- **Type 0:** Không thay đổi thuộc tính sau khi tạo.
- **Type 1:** Ghi đè thông tin, không giữ phiên bản cũ trong dimension.
- **Type 2:** Thêm dòng phiên bản với surrogate key, effective_from/effective_to và current_flag nếu thiết kế dùng.
- **Type 3:** Giữ một số thông tin lịch sử ở cột riêng, chỉ hỗ trợ lịch sử có giới hạn.

```text
customer_key | customer_id | segment  | valid_from | valid_to
101          | C001        | Standard | 2025-01-01 | 2026-06-30
205          | C001        | VIP      | 2026-07-01 | NULL
```

**Bẫy:** Fact tháng 04/2026 phải join phiên bản Standard, không join phiên bản VIP hiện hành nếu báo cáo yêu cầu phân tích **theo trạng thái tại thời điểm giao dịch**.

### 5.8. ODS vs Data Warehouse

- **ODS:** Tích hợp dữ liệu vận hành, thường gần hiện trạng, phục vụ truy vấn nghiệp vụ/đối soát và các luồng tiếp theo.
- **DWH:** Dữ liệu tổ chức để phân tích lịch sử, tính KPI, dimension/fact, hỗ trợ BI.

Không có một định nghĩa bắt buộc ODS phải có lưu lịch sử ngắn bao nhiêu, phụ thuộc thiết kế.

### 5.9. Banking Data Model: điểm phải hiểu

Các thực thể khái quát:

```text
CUSTOMER -- CUSTOMER_ACCOUNT -- ACCOUNT -- TRANSACTION
     |                                |            |
     +---- CUSTOMER_LOAN --- LOAN     +-- BALANCE  +-- CHANNEL
                      |                             |
                   COLLATERAL                   BRANCH/PRODUCT
```

Không phải mọi ngân hàng dùng đúng schema này. Quan hệ khách hàng–tài khoản có thể N:M (đồng sở hữu). Loan có lịch trả nợ và nhiều giao dịch giải ngân/thanh toán. Quan trọng là **business key, effective date, nguồn truth và quy tắc historization**.

### 5.10. Các câu phỏng vấn Data Modeling

1. **Grain quan trọng thế nào?** Quyết định PK/fact measure, tránh join duplication.
2. **Tại sao dùng surrogate key?** Tránh phụ thuộc natural key thay đổi và hỗ trợ SCD Type 2.
3. **Số dư là additive measure không?** Số dư snapshot không cộng qua thời gian tùy tiện; là semi-additive.
4. **Revenue và balance khác nhau?** Revenue flow trong kỳ; balance stock tại thời điểm.
5. **Nếu khách chuyển chi nhánh, báo cáo lịch sử thế nào?** Xác nhận muốn as-was hay as-is; SCD/history hoặc snapshot tương ứng.
6. **Data model phải chuẩn hóa hết không?** Không; OLTP và BI phục vụ mục đích khác.
7. **Tại sao có bridge table?** Mô hình N:M hoặc mối liên kết nhiều chiều cần quản lý rõ grain.
8. **Có thể dùng customer_id làm PK cho dim_customer SCD2?** Không nếu mỗi ID có nhiều phiên bản; dùng surrogate key hoặc khóa tổng hợp theo version.

---

## 6. ODS, DWH, Data Lake, Lakehouse

### 6.1. Các lớp dữ liệu

| Lớp | Mục đích | Kiểu dữ liệu thường thấy |
|---|---|---|
| Raw/Bronze | Giữ dữ liệu gốc, metadata, source lineage | CSV, JSON, Parquet, file gốc |
| Staging | Dữ liệu nạp vào khu vực trung gian, mapping gần nguồn | Tables gần source, typed columns |
| Silver/Curated | Làm sạch, chuẩn hóa, join, dedup, master mapping | Tables được kiểm định |
| Gold/Mart | Metrics/KPI/fact/dim đã tổng hợp phục vụ khai thác | Fact/dim, aggregates |
| Sharing/Serving | Cung cấp dữ liệu cho ứng dụng/hệ khác | Contract/API/tables |

**Nhớ:** Không thể khẳng định Raw luôn nằm trong MinIO hay Silver luôn là Postgres; đó là lựa chọn dự án. Trino/Spark/MinIO/DBT là các thành phần khác vai trò.

### 6.2. Data Lake vs Lakehouse

Data Lake là kho file đa dạng trên object/distributed storage. Lakehouse bổ sung table abstraction như Iceberg/Delta/Hudi, metadata, snapshot, schema evolution và hỗ trợ kiểm soát đọc/ghi nhất quán.

### 6.3. CSV / JSON / Parquet / ORC

| Format | Đặc trưng | Khi nào phù hợp |
|---|---|---|
| CSV | Văn bản đơn giản, ít schema, row-oriented | Trao đổi và import đơn giản |
| JSON | Cấu trúc nested, dễ mở rộng, lớn hơn | API/event/source semi-structured |
| Parquet | Columnar, nén, column pruning | Data Lake analytics/Spark/Trino |
| ORC | Columnar, indexing/statistics theo format | Một số Hadoop/Hive analytics |

Parquet thường hiệu quả khi chỉ đọc ít cột từ bảng rộng. Không phải mọi dataset nhỏ đều hưởng lợi đáng kể so với CSV.

### 6.4. Partitioning và Small Files

Partition giúp query engine bỏ qua vùng dữ liệu không cần đọc, ví dụ partition theo `business_date`. Nhưng partition quá nhỏ/ngày/giờ hoặc số lượng file quá nhiều làm tăng metadata overhead và chi phí planning. Dùng compaction/batching/lựa chọn partition cardinality hợp lý.

### 6.5. Schema Evolution

Khi nguồn thêm cột, đổi kiểu, đổi tên hoặc bỏ cột, cần xem tác động đến ingest, mapping, target schema, dữ liệu lịch sử, test và backward compatibility. Không nên auto add column mọi trường hợp mà thiếu kiểm soát.

### 6.6. Source of Truth / Golden Record / Master Data

“Single Source of Truth” là nguyên tắc xác định nơi dữ liệu chuẩn phục vụ từng mục đích. Master Data mapping giúp liên kết một đối tượng có nhiều ID ở các hệ khác nhau. Conflict resolution cần quy tắc ưu tiên nguồn, hợp nhất, versioning và kiểm tra.

---

## 7. Spark, Spark SQL, PySpark

### 7.1. Bản chất và kiến trúc

Apache Spark là distributed computing engine. Mô hình thường có **Driver**, **Executors**, **Cluster Manager** (YARN, Kubernetes, Standalone...) và storage bên ngoài.

- **Driver:** Tạo SparkSession, lập kế hoạch thực thi, điều phối.
- **Executor:** Chạy task, xử lý dữ liệu trong partitions, cache/shuffle.
- **Job:** Thực thi do action kích hoạt; một action có thể kích hoạt nhiều job tùy plan.
- **Stage:** Một nhóm task tổ chức theo dependency và ranh giới shuffle.
- **Task:** Đơn vị thực thi trên partition.

```text
Spark Driver
  |
  +-- Job --> Stage 1 --> Task 1, Task 2, Task 3...
             [shuffle boundary]
            Stage 2 --> Task 1, Task 2...
  |
Cluster Manager --> Executor A / Executor B / Executor C
```

### 7.2. Spark SQL vs PySpark

- **Spark SQL:** Module/query engine xử lý dữ liệu có cấu trúc bằng SQL và DataFrame/Dataset.
- **PySpark:** Python API để làm việc với Spark; có thể gọi `spark.sql()` hoặc sử dụng DataFrame API.

```sql
SELECT customer_id, SUM(amount) total
FROM transactions
GROUP BY customer_id;
```

```python
from pyspark.sql import functions as F
result = df.groupBy("customer_id").agg(F.sum("amount").alias("total"))
```

Với built-in operations, Spark SQL và PySpark DataFrame API thường được Catalyst tối ưu vào plan tương đương. Python UDF có thể mang overhead bổ sung và làm giảm một số khả năng tối ưu.

**Khi phỏng vấn:** Nếu kinh nghiệm trực tiếp chủ yếu Spark SQL, nói rõ; không nhận mình viết PySpark production khi chưa làm.

### 7.3. Catalyst Optimizer và Tungsten/AQE

- **Catalyst:** Phân tích và tối ưu logical/physical plan của SQL/DataFrame.
- **AQE (Adaptive Query Execution):** Dùng runtime statistics để điều chỉnh plan khi chạy; có thể coalesce shuffle partitions, chuyển join strategy, xử lý skew phù hợp.
- **Tungsten/codegen:** Hướng tối ưu CPU/memory execution của Spark; không phải “thay thế” Catalyst.

Công cụ xem plan:

```python
df.explain("formatted")
```

```sql
EXPLAIN FORMATTED
SELECT ...;
```

### 7.4. Lazy Evaluation; Transformation vs Action

```python
df2 = df.filter(F.col("amount") > 0)  # transformation
df3 = df2.groupBy("customer_id").count()  # transformation
df3.show()  # action
```

Spark xây execution plan và thường chưa tính toàn bộ transformation cho đến action. Ví dụ các action: `show`, `count`, `collect`, `write`.

### 7.5. Narrow / Wide / Shuffle

- **Narrow:** Đầu ra của một partition phụ thuộc ít partition đầu vào, ví dụ filter/select.
- **Wide:** Cần phân phối lại giữa partition, ví dụ `groupBy`, `distinct`, join theo chiến lược shuffle.
- **Shuffle:** Tốn network, disk I/O, serialization, memory, sort; là điểm quan trọng khi tối ưu Spark.

### 7.6. Join Strategy

- **Broadcast Hash Join:** Broadcast phía nhỏ để tránh shuffle lớn; rủi ro memory nếu broadcast quá lớn.
- **Sort Merge Join:** Hai phía phân phối và sắp xếp theo join key, có thể shuffle/sort lớn.
- **Shuffle Hash Join:** Tùy plan, shuffle rồi hash phía thích hợp.
- **Nested-loop/Cross Join:** Có thể cực đắt nếu dữ liệu lớn.

```sql
SELECT /*+ BROADCAST(d) */ f.*, d.category
FROM fact_transaction f
JOIN dim_product d ON f.product_id=d.product_id;
```

Hint không phải bảo đảm tuyệt đối; SQL optimizer có thể bỏ hint nếu không hỗ trợ trong ngữ cảnh.

### 7.7. Partition, repartition/coalesce, caching

- **Input partition:** Cách Spark chia nguồn đọc.
- **Shuffle partition:** Số partition sau shuffle, điều chỉnh được qua cấu hình/Adaptive Execution.
- **Output file partition:** Định hình số lượng file đích khi ghi.
- **`repartition(n)`** thường gây full shuffle, tăng/giảm phân bố.
- **`coalesce(n)`** thường giảm partition mà không full shuffle, có thể tạo skew.
- **`cache/persist`** hữu ích nếu tái sử dụng tập dữ liệu, nhưng chiếm memory/disk; phải `unpersist` khi không cần.

### 7.8. Data Skew: cách chẩn đoán và sửa

**Dấu hiệu:** Một vài task chạy rất lâu; shuffle read của các task chênh lệch mạnh; spill/OOM; stage có long tail.

**Nguyên nhân:** Key phổ biến (hot key), NULL tập trung, phân phối bản ghi lệch; JOIN có nặng một phía.

**Cách xử lý:** Kiểm tra Spark UI và phân phối key; broadcast table nhỏ; salting hot key khi thích hợp; filter trước JOIN; AQE skew optimization; thay đổi partition logic. Không tự động tăng partition là giải quyết được skew cùng key.

### 7.9. Spark OOM: Driver vs Executor

- **Driver OOM:** `collect()`/`toPandas()` hoặc metadata quá nhiều về Driver; driver memory thấp.
- **Executor OOM:** Partition lớn, join/hash/sort/broadcast/cache, Python worker overhead, data skew.
- **Shuffle spill:** Bước xử lý vượt memory phải spill disk, có thể chậm chưa chắc OOM.

**Quy trình:** Log/Spark UI → stage/task → phân phối dữ liệu → physical plan → chọn giải pháp giảm dữ liệu/shuffle/broadcast → chỉnh executor config khi thực sự cần → benchmark và quality check.

### 7.10. Ví dụ PySpark đọc Parquet, filter, aggregate, write

```python
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("bank_txn_etl").getOrCreate()

src = spark.read.parquet("s3a://lake/raw/transactions/")
result = (
    src.filter(F.col("status") == "SUCCESS")
       .withColumn("business_date", F.to_date("posting_time"))
       .groupBy("business_date", "branch_id")
       .agg(F.sum("amount").alias("total_amount"),
            F.count("*").alias("txn_count"))
)
result.write.mode("overwrite").partitionBy("business_date").parquet(
    "s3a://lake/gold/daily_branch_txns/"
)
```

Đây là **code minh họa**; chạy được hay không phụ thuộc S3A connector, credentials, Spark/Hadoop version, cấu hình storage và schema. `overwrite` phải cẩn thận vì có thể xóa phạm vi ngoài ý muốn; production cần chiến lược idempotent, atomic writes và commit phù hợp.

### 7.11. Câu hỏi Spark + đáp án

1. **Spark Driver khác Executor?** Driver lập kế hoạch/điều phối; Executor thực thi task.
2. **Stage sinh ra khi nào?** Phân chia theo dependency và shuffle boundaries trong plan.
3. **Why lazy evaluation?** Cho optimizer cơ hội tối ưu chuỗi thao tác trước khi thực thi.
4. **DataFrame vs RDD?** DataFrame có schema/optimizer SQL, RDD thấp mức trừu tượng.
5. **PySpark chậm hơn Spark SQL?** Built-in DataFrame và SQL thường tương đương; Python UDF/serialization có thể tạo khác biệt.
6. **Broadcast Join nên dùng khi nào?** Khi build side nhỏ và có đủ memory.
7. **Vì sao partition quá nhỏ làm chậm?** Scheduling/file overhead; quá lớn gây memory/skew.
8. **Cache dữ liệu mọi bước tốt không?** Không; gây memory pressure, nhiều dữ liệu dùng một lần không có lợi.
9. **AQE giải quyết hết skew?** Không, phụ thuộc loại operator và runtime plan.
10. **Spark job bị OOM?** Chẩn đoán Driver/Executor, stage, shuffle, skew trước khi tăng RAM.
11. **`collect()` nguy hiểm?** Đưa tất cả data về Driver, dễ OOM.
12. **Filter trước join luôn nhanh hơn?** Thường có lợi giảm dữ liệu, nhưng optimizer có thể tự pushdown; cần xem plan.
13. **Parquet nhanh hơn CSV ở mọi trường hợp?** Không, workload/size/schema quyết định.
14. **`repartition` khác `coalesce`?** Phân phối lại vs gộp bớt partition thường không shuffle toàn bộ.
15. **Nếu job nhanh nhưng output sai?** Kiểm tra transformation/JOIN/grain/data quality, không chỉ performance.

---

## 8. Apache Airflow

### 8.1. Vai trò

Airflow là **workflow orchestrator**, không phải distributed data processing engine. Nó lập lịch, xác định dependency, retry, lưu trạng thái và giám sát task. Spark làm công việc xử lý dữ liệu nặng; Airflow có thể gọi job Spark, SQL, API, dbt.

### 8.2. Các thành phần

| Khái niệm | Ý nghĩa |
|---|---|
| DAG | Directed Acyclic Graph mô tả workflow |
| DAG Run | Một lần thực hiện DAG cho một data interval/run |
| Task/Task Instance | Định nghĩa công việc / lần chạy cụ thể của task |
| Operator | Cách định nghĩa công việc cụ thể |
| Scheduler | Lập lịch và xác định công việc chạy |
| Executor | Cơ chế thực thi task |
| Worker | Tiến trình/nút thực thi khi executor yêu cầu |
| Connections | Kết nối, credentials tới hệ ngoài |
| Variables | Cấu hình mức Airflow |
| XCom | Giao tiếp metadata nhỏ giữa tasks, không dùng để chuyển Big Data |
| Pools | Giới hạn concurrency cho tài nguyên dùng chung |
| Retries/Timeouts | Chính sách chạy lại/giới hạn thời gian |
| Trigger Rules | Quy tắc khi nào task downstream được chạy |

### 8.3. DAG minh họa (Airflow 2.x)

```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task

@dag(
    dag_id="bank_daily_etl",
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
)
def banking_etl():
    @task
    def extract():
        print("Extract data for the DAG run data interval")

    @task
    def transform():
        print("Execute Spark/dbt transformation")

    @task
    def validate():
        print("Run data quality checks")

    extract() >> transform() >> validate()

banking_etl()
```

Trong production, nên xử lý logical date/data interval đúng cách, khai báo dependencies rõ ràng, connection/secrets phù hợp và lưu log có thể truy vết. Không ghi password vào code.

### 8.4. Data Interval và Catchup

- `schedule='@daily'` định kỳ ngày; một DAG Run thường xử lý một khoảng data interval, không phải mặc nhiên dữ liệu “ngay lúc code chạy”.
- `catchup=False` tránh tự động tạo mọi DAG Run lịch sử chưa chạy khi DAG được bật; không có nghĩa không thể chủ động backfill.
- Backfill cần business date, period boundaries và idempotency; lỗi thường gặp là dùng `datetime.now()` thay vì period của run.

### 8.5. Task fail: quy trình giải thích cho phỏng vấn

1. Định vị DAG Run và task thất bại.
2. Đọc log/stack trace và error code.
3. Phân loại lỗi hạ tầng/kết nối, dữ liệu, SQL, memory, permission, timeout.
4. Kiểm tra partial load/side effects và checkpoint.
5. Khắc phục nguyên nhân, không chỉ click retry.
6. Retry/backfill với idempotency.
7. Reconcile dữ liệu và ghi incident/runbook.

### 8.6. XCom, Variables, Connections, Secrets

- **XCom:** Truyền metadata nhỏ, path, số bản ghi; không phải dùng cho DataFrame lớn.
- **Variables:** Config chung, nhưng đừng lạm dụng làm credentials nếu có backend quản lý secrets chuyên dụng.
- **Connections:** Chi tiết truy cập hệ ngoài; phân quyền và secret backend phù hợp.

### 8.7. Retry vs Re-run vs Backfill

- Retry: Chạy lại **một task instance** theo cấu hình.
- Re-run/Clear: Cho phép chạy lại một hoặc nhóm task đã có run.
- Backfill: Chạy những data interval trước đó chưa được xử lý hoặc cần tính lại.

### 8.8. Airflow Questions

1. **DAG vs Task?** DAG mô tả quan hệ giữa các task.
2. **Scheduler khác Executor?** Scheduler xác định task đến lượt; Executor cung cấp cơ chế chạy.
3. **Airflow có xử lý Big Data thay Spark không?** Không phải vai trò chính; thường gọi Spark job.
4. **Tại sao DAG phải idempotent?** Để retry/backfill không làm sai dữ liệu.
5. **Task 3 fail, task 1–2 success, chạy lại toàn bộ?** Không mặc định; xác minh side effects, dependency và chỉ rerun cần thiết.
6. **Task Success nhưng báo cáo sai?** Data Quality Test độc lập.
7. **XCom có nên truyền 1 triệu dòng?** Không; dùng storage và truyền URI/batch ID.
8. **Concurrency cao có luôn tốt?** Không; có thể làm nghẽn DB/source.
9. **Pools dùng khi nào?** Giới hạn số task cùng truy cập hệ thống hữu hạn tài nguyên.
10. **Backfill sai ngày?** Xem data interval, timezone, manual run config và date filter.

---

## 9. Python dành cho Data Engineer

### 9.1. Cấu trúc dữ liệu và tính chất

- **list:** Có thứ tự, sửa được, cho phép trùng.
- **tuple:** Có thứ tự, immutable về container (phần tử mutable vẫn có thể thay đổi).
- **set:** Các phần tử hashable duy nhất, phù hợp membership.
- **dict:** Key-value, key hashable, giữ insertion order trong Python hiện đại.
- **Generator:** Tạo từng giá trị theo nhu cầu, không giữ mọi giá trị trong RAM.
- **Context manager:** Tự quản lý tài nguyên `with open()`, transaction/connection theo thư viện.

### 9.2. Memory optimization / đọc theo chunk

Không load CSV nhiều GB vào một DataFrame duy nhất nếu không đủ RAM.

```python
import pandas as pd
for batch in pd.read_csv("large.csv", chunksize=100_000):
    # validate/transform/load each batch
    print(len(batch))
```

Cần quản lý transaction/commit, batch ID, memory của các transformation, thậm chí `chunksize` cũng có thể chưa đủ nếu mỗi batch có nested JSON hoặc join quá lớn.

### 9.3. Exception handling và logging

```python
import logging
logger = logging.getLogger("etl")

def process(batch):
    try:
        checked = validate(batch)
        transformed = transform(checked)
        load(transformed)
    except ValueError:
        logger.exception("Input validation failed")
        raise  # fail task để xử lý đúng
    except ConnectionError:
        logger.exception("Temporary connectivity issue")
        raise  # để orchestration quyết định retry
```

**Không dùng `except Exception: pass`** vì có thể làm task Success dù data thiếu. Log tránh chứa thông tin cá nhân, secrets hoặc thông tin ngân hàng nhạy cảm.

### 9.4. OOP, decorator, async, threading/process

- **OOP:** Class/encapsulation hữu ích cho connectors, parsers, interfaces.
- **Decorator:** Bọc behavior như logging/retry/metrics.
- **Threading/asyncio:** Hữu ích cho workload I/O-bound trong điều kiện phù hợp.
- **Multiprocessing:** Có thể hữu ích cho CPU-bound và bỏ qua giới hạn GIL của CPython qua nhiều process; overhead IPC/memory đáng kể.
- **Không nhầm** Python multiprocessing với Spark distributed execution.

### 9.5. Excel parsing – đặc biệt liên quan GML

Các trường hợp: merged cells, multi-row headers, sheet không cố định, total/subtotal rows, đơn vị tiền tệ trong text, định dạng ngày tháng, ô chứa công thức, ô trống mang nghĩa lặp giá trị theo ngữ cảnh.

```python
from openpyxl import load_workbook
wb = load_workbook("misa.xlsx", data_only=True, read_only=False)
ws = wb.active
print(ws.merged_cells.ranges)
for row in ws.iter_rows(values_only=True):
    print(row)
```

**Bẫy:** `data_only=True` đọc cached formula result nếu Excel có lưu, không tự tính lại công thức. Với merged cells thường chỉ top-left chứa giá trị. Trước khi fill-down phải biết ý nghĩa ô gộp.

Quy trình parser phù hợp: identify template → detect header → extract table region → normalize columns/types → validate → stage; phân luồng lỗi/unrecognized template thay vì nạp sai âm thầm.

### 9.6. Kết nối DB, transaction, SQL injection

Sử dụng connection pooling khi phù hợp, prepared/parameterized SQL, batch insert, rollback khi lỗi, secret manager/env variables thay vì hardcode mật khẩu. Tránh nối trực tiếp input người dùng vào SQL.

### 9.7. Python Questions

1. **Generator khác List?** Lazy yield, giảm memory khi duyệt tuần tự.
2. **Pandas bị OOM?** Chunking, chọn cột, dtype, streaming parser, DB pushdown hoặc Spark tùy volume.
3. **`is` vs `==`?** Identity vs equality.
4. **Shallow vs deep copy?** Copy lớp ngoài vs clone nested objects (theo semantics đối tượng).
5. **Logging tốt có gì?** Context: job/run ID, source, period, processed count, failure reason; không log secrets.
6. **Retry tất cả exception tốt không?** Không; lỗi dữ liệu deterministic không nên retry vô hạn.
7. **Xử lý 20 format Excel?** Parser theo template/config, common normalized schema, test cases, source lineage.
8. **Multi-thread Python tăng tốc CPU-bound không?** Không mặc định do GIL trong CPython; tùy native libs/process.
9. **Unit test pipeline thế nào?** Dùng sample schema, empty/null/dup/date edge cases và assertion output.
10. **Decimal vs float với tiền?** Decimal được kiểm soát precision/rounding theo business rule.

---
## 10. dbt

### 10.1. dbt làm gì, không làm gì?

**dbt (data build tool)** quản lý SQL-based transformations, dependency, tests, tài liệu và môi trường build dữ liệu trong warehouse/lakehouse/DB thông qua adapter. dbt không mặc định đảm nhiệm crawler/API ingestion, mặc dù hệ sinh thái có công cụ liên quan.

Các khái niệm: **model**, `ref`, `source`, materialization, macro/Jinja, seed, snapshot, test, lineage, packages, targets/profiles.

### 10.2. Materializations

| Loại | Chức năng | Trade-off |
|---|---|---|
| View | Lưu định nghĩa SQL | Lúc query có thể tính lại, ít chi phí lưu |
| Table | Tạo dữ liệu vật lý | Nhanh khi đọc lặp, phải refresh/rebuild |
| Incremental | Xử lý tập dữ liệu thay đổi sau lần trước | Logic idempotent, late data, unique key phức tạp |
| Ephemeral | Inline SQL dưới dạng CTE khi compile | Giảm object nhưng truy vấn downstream có thể nặng |

### 10.3. `ref()` và `source()`

- `source('bank','transactions')`: Tham chiếu dữ liệu nguồn, có cấu hình metadata/freshness/test.
- `ref('stg_transactions')`: Tham chiếu model khác và tạo dependency DAG trong dbt.

### 10.4. Incremental model ví dụ

```sql
{{
  config(
    materialized='incremental',
    unique_key='transaction_id',
    incremental_strategy='merge'
  )
}}

SELECT transaction_id, customer_id, amount, updated_at
FROM {{ source('bank', 'transactions') }}

{% if is_incremental() %}
WHERE updated_at >= (
  SELECT COALESCE(MAX(updated_at), '1900-01-01') FROM {{ this }}
)
{% endif %}
```

**Cảnh báo:** Ví dụ giả định adapter hỗ trợ MERGE và kiểu ngày/timestamp tương thích. Cần bảo đảm unique key không NULL, không trùng source batch, và xử lý thay đổi/xóa, late data. `>= MAX` có thể đọc lại vài dòng để tránh mất khi timestamp bằng nhau, nhưng không giải quyết hết late arrivals.

### 10.5. dbt Test

```yaml
models:
  - name: dim_customer
    columns:
      - name: customer_id
        data_tests:
          - not_null
          - unique
```

Các kiểm tra thông dụng: `not_null`, `unique`, `accepted_values`, `relationships`; ngoài ra có thể viết singular/custom test để kiểm tra business logic và reconciliation.

### 10.6. dbt vs Airflow vs Spark

- **dbt:** Quản lý transformation models/tests/lineage.
- **Airflow:** Điều phối thứ tự và lịch chạy giữa các hệ thống.
- **Spark:** Distributed compute engine thực thi xử lý dữ liệu lớn.

Có thể dùng Airflow gọi `dbt run` hoặc job Spark; không nên dùng dbt thay hẳn scheduler trong mọi trường hợp.

### 10.7. dbt trong dự án Gimasys

Các view/procedure nặng được chuyển thành dbt model và lưu bảng vật lý để tránh lặp lại truy vấn nặng. Bạn cần trả lời: Tại sao chọn table thay view; refresh theo lịch nào; có full refresh/incremental không; logic SQL tương đương thế nào; kiểm thử dữ liệu bằng gì. Chỉ gọi `incremental` nếu thực tế có dùng loại đó.

### 10.8. dbt Questions

1. **View vs Table?** Tính lúc đọc so với vật lý hóa dữ liệu; đổi chi phí query lấy storage/refresh.
2. **dbt model vs pipeline?** Model là transformation unit; pipeline còn ingest, schedule, DQ, publish.
3. **`ref` để làm gì?** Dependency, tên quan hệ đúng môi trường, lineage.
4. **Incremental key sai?** Có thể duplicate hoặc overwrite sai.
5. **dbt schema change?** Cần kiểm tra adapter và `on_schema_change`, downstream tests/compatibility.
6. **Thay đổi logic lịch sử thì sao?** Có thể cần backfill/full-refresh có kiểm soát.
7. **dbt test fail?** Xác minh rule, nguồn lỗi, tạm dừng publish tùy severity, sửa và rerun.

---

## 11. Kafka và Streaming

### 11.1. Kafka để làm gì?

Kafka là distributed event streaming platform để gửi, lưu và đọc sự kiện. Ví dụ CDC cập nhật tài khoản từ hệ nguồn, producer/connector ghi event vào topic và downstream consumer cập nhật kho dữ liệu.

```text
Source DB + CDC Connector --> Kafka Topic(partition 0/1/2)
                                  |
                        Consumer Group / Stream Processing
                                  |
                        Staging / Lakehouse / DWH
```

### 11.2. Khái niệm bắt buộc

- **Producer:** Gửi events.
- **Topic:** Luồng logic.
- **Partition:** Đơn vị dữ liệu có thứ tự và hỗ trợ song song.
- **Broker:** Kafka server.
- **Consumer Group:** Nhóm consumer chia việc đọc partitions.
- **Offset:** Thứ tự của record trong partition.
- **Consumer Lag:** Khoảng cách tiến độ consumer so với đầu topic mới nhất.
- **Retention:** Chính sách giữ dữ liệu theo thời gian/kích thước, khác commit offset.
- **Replication Factor:** Mức nhân bản partition để tăng khả năng chịu lỗi.
- **Key:** Giúp partitioner điều phối events liên quan vào cùng partition nếu phù hợp.
- **Rebalance:** Consumer group phân lại partitions khi membership/topic thay đổi.

### 11.3. Ordering và Parallelism

Kafka giữ thứ tự **trong từng partition**, không bảo đảm thứ tự toàn cục giữa các partition. Nếu nghiệp vụ tài khoản cần đúng thứ tự thay đổi, cân nhắc dùng account_id làm key, theo dõi partitioning changes và state handling.

### 11.4. Delivery Semantics

- **At-most-once:** Có thể mất event nếu commit trước xử lý rồi gặp lỗi.
- **At-least-once:** Có thể xử lý trùng, ưu tiên không bỏ sót; idempotent sink.
- **Exactly-once effect:** Chỉ có nghĩa trong phạm vi source-processing-sink có cơ chế bảo đảm cụ thể; không chỉ bằng bật một option.

### 11.5. Lỗi consumer chết giữa chừng

Consumer đã ghi DB nhưng chết trước commit offset → có thể đọc lại event → dedup/upsert/transaction id. Không nên gắn trùng với “Kafka tự làm mất message”; xét thứ tự commit và retention.

### 11.6. Streaming window và late event

- **Event time:** Thời gian sự kiện thực phát sinh.
- **Processing time:** Thời gian hệ thống xử lý.
- **Watermark (streaming):** Ngưỡng chấp nhận late data để quản lý state/window, ý nghĩa cụ thể theo engine.
- **Tumbling window:** Các khoảng cố định không overlap.
- **Sliding window:** Các khoảng chồng lấn.
- **Stateful processing:** Lưu trạng thái qua nhiều events, cần checkpoint.

### 11.7. Kafka Questions

1. **Offset là gì?** Vị trí record trong partition.
2. **Lag tăng liên tục?** Consumer xử lý chậm hơn tốc độ đến hoặc bị nghẽn/lỗi.
3. **Tăng consumer quá số partition?** Consumer dư có thể không được giao partition.
4. **Kafka có thay Airflow?** Không cùng mục đích.
5. **Kafka có tự bảo đảm exactly-once đến PostgreSQL?** Không tự động; phải thiết kế sink/transaction/dedup.
6. **Tại sao partition key quan trọng?** Ordering theo entity và phân phối tải.
7. **Hot partition?** Một key/nhóm key gây tải lệch, consumer đó chậm.
8. **At-least-once xử lý duplicate?** Idempotency và unique business/event key.
9. **Replay event dùng gì?** Offset/retention và consumer logic, tránh ghi trùng khi phát lại.
10. **CDC khác event application?** CDC phản ánh thay đổi DB; domain event phản ánh hành động nghiệp vụ; có thể khác semantics.

---

## 12. Data Quality, testing, monitoring

### 12.1. Các chiều chất lượng

| Dimension | Câu hỏi | Kiểm tra ví dụ |
|---|---|---|
| Completeness | Có đủ dữ liệu không? | Row count, mandatory fields, periods |
| Uniqueness | Có bản ghi trùng trái rule? | Business key unique |
| Validity | Có đúng miền giá trị? | Currency code, status |
| Consistency | Có khớp giữa các tầng? | Source-target reconciliation |
| Accuracy | Có đúng thực tế/quy tắc? | Tổng tiền và nghiệp vụ kiểm chứng |
| Freshness | Có cập nhật đúng SLA? | Max business timestamp, SLA alert |
| Referential Integrity | FK/master mapping hợp lệ? | Orphan account/customer keys |

### 12.2. Data Reconciliation (đối soát)

Không chỉ so `COUNT(*)`, vì có thể có cùng số dòng nhưng giá trị khác. Cần nhiều tầng:

1. Row count theo kỳ/source/branch.
2. Unique key count, duplicate count.
3. Tổng `amount`, min/max business date, số giao dịch theo status.
4. Key-level missing/excess records.
5. Column-level mismatches theo business rules.
6. Sample/edge cases (negative amount, reversals, timezone, NULL).

Sử dụng cùng snapshot/cutoff khi nguồn liên tục thay đổi, nếu không đối soát có thể lệch vì đọc khác thời điểm.

### 12.3. SIT, UAT, Unit, Integration, Regression

- **Unit test:** Kiểm thử logic transform nhỏ.
- **Integration/SIT:** Kiểm tra các thành phần tích hợp hoạt động đúng.
- **UAT:** Người dùng nghiệp vụ xác nhận đáp ứng yêu cầu.
- **Regression:** Bảo đảm sửa đổi không làm hỏng chức năng trước đó.
- **Performance test:** Kiểm tra thời gian và tài nguyên theo tải.

Khi tối ưu SQL cũ: test performance **và** test kết quả; không chỉ “query chạy nhanh”.

### 12.4. Monitoring / Observability

Các metrics: job duration, success rate, task retries, data freshness, input/output row count, malformed rows, Spark shuffle read/write, spill, CPU/RAM, DB query latency, Kafka lag, cost per pipeline.

**Logs** giải thích sự kiện và lỗi; **metrics** định lượng; **traces/lineage** giúp lần theo đường đi hoặc phụ thuộc dữ liệu. Log cần có run_id, dataset, period, step, exception, không log secrets/PII.

### 12.5. SLA, SLO, Incident

- **SLA:** Cam kết mức dịch vụ/thời gian dữ liệu sẵn sàng.
- **SLO:** Mục tiêu đo chất lượng dịch vụ.
- **Incident:** Sự cố ảnh hưởng độ đúng, độ đủ hoặc sẵn sàng.
- **Runbook:** Quy trình kiểm tra, khôi phục, escalation.
- **RCA/Postmortem:** Phân tích root cause, action items để phòng ngừa.

### 12.6. Quality Questions

1. **DAG Success nhưng dữ liệu thiếu?** Thêm DQ tests và reconciliations, phân tích theo từng bước.
2. **1 triệu source vs 980k target?** Kiểm tra filter, join, rejected, dedup, CDC, partition; có thể là hợp lệ tùy mapping.
3. **Dữ liệu có row count đúng nhưng tổng tiền lệch?** Kiểm tra bản ghi sai giá trị, currency, rounding, negative/reversal, status.
4. **Source có duplicate event?** Thiết kế key, rules, idempotent load.
5. **Kiểm tra sau SQL tuning?** Diff row-level/aggregates, business edge cases, test SIT/UAT.
6. **Vì sao báo cáo ngày hôm qua đổi số?** Late transaction, posting adjustments, data backfill, rule/snapshot change.
7. **Khi nào chặn publish Gold?** Khi critical quality gate fail theo thỏa thuận.
8. **Data lineage có ích gì?** Truy ra nguồn và pipeline tạo chỉ số, biết ảnh hưởng khi schema/rule thay đổi.

---

## 13. Trino, MinIO, Parquet, Iceberg

### 13.1. Vai trò từng thành phần

- **MinIO:** Object Storage API tương thích S3 dùng lưu file raw/parquet/warehouse objects; không tự trở thành relational database.
- **Trino:** Distributed SQL query engine qua connector, có coordinator/worker; không phải storage vật lý chính.
- **Spark:** Engine xử lý/transform dữ liệu lớn.
- **Apache Iceberg:** Open table format quản lý metadata, snapshot, schema/partition evolution cho bảng trên object storage.
- **Nessie/catalog:** Quản lý metadata và có thể version catalog tùy kiến trúc, không phải file object storage.
- **Parquet:** Format file dạng cột nằm trong storage, Iceberg có thể tham chiếu đến Parquet data files.

### 13.2. Câu hỏi: Spark và Trino khác nhau?

Spark xử lý ETL, batch, streaming và các workload tính toán phân tán; Trino tập trung SQL interactive/federated query. Cả hai chạy SQL trong các ngữ cảnh khác nhau. Không khẳng định một công cụ luôn nhanh hơn công cụ còn lại.

### 13.3. Iceberg snapshots/schema evolution

Iceberg lưu metadata chỉ đến snapshot/data files. Khi có commit mới, snapshot thay đổi một cách nhất quán theo cơ chế catalog/commit. Hỗ trợ quản lý schema evolution, partition evolution, time travel tùy engine và implementation.

### 13.4. Data Lake performance

- Partition pruning: Bỏ qua partition không liên quan.
- Predicate pushdown: Đẩy filter gần source/scan.
- Column pruning: Chỉ đọc cột cần thiết.
- File compaction: Giảm quá nhiều small files.
- Metadata maintenance: Quản lý snapshots/manifests/orphan files an toàn.

### 13.5. Trino/MinIO/Iceberg Questions

1. **MinIO khác PostgreSQL?** Object storage vs relational database.
2. **Iceberg có chứa file data không?** Quản lý table metadata và snapshot, dữ liệu vật lý nằm trong các data files trên storage.
3. **Trino dùng làm ETL được không?** Có thể thực hiện SQL transformations khi connector/permission hỗ trợ, nhưng vai trò/cấu hình thực tế quyết định.
4. **Nessie và Iceberg khác?** Catalog/version layer và table format.
5. **Object storage khác POSIX?** Semantics API/object, không mặc định hỗ trợ thao tác file system như local FS.
6. **Small files gây vấn đề gì?** Metadata và planning overhead, quá nhiều tasks/files.
7. **Partition theo customer_id tốt không?** Cardinality quá cao có thể gây quá nhiều partition; chọn theo query pattern và volume.
8. **Schema evolution là tự động an toàn?** Không, phải xem downstream và tương thích.

---

## 14. Docker, Kubernetes, OpenShift, Linux, Git, CI/CD

### 14.1. Docker

- **Dockerfile:** Chỉ dẫn build image.
- **Image:** Artifact đóng gói application/runtime.
- **Container:** Instance chạy từ image.
- **Volume:** Lưu dữ liệu bền qua vòng đời container.
- **Network:** Kết nối các containers/services.
- **Port mapping:** Map port host–container.
- **Docker Compose:** Khai báo nhiều services, volumes, networks trong YAML.

Lệnh gợi nhớ:

```bash
docker ps
docker logs --tail 100 my_service
docker inspect my_service
docker compose ps
docker compose logs airflow
```

**Bẫy:** Container xóa không đồng nghĩa dữ liệu trên volume được bảo toàn nếu bạn không cấu hình volume; không hardcode secrets trong image.

### 14.2. Kubernetes căn bản

| Object | Vai trò |
|---|---|
| Pod | Đơn vị triển khai container |
| Deployment | Quản lý ReplicaSet/Pod replica cho workload phù hợp |
| StatefulSet | Quản lý ứng dụng cần identity/storage ổn định |
| Service | Endpoint ổn định để truy cập Pods |
| Namespace | Phân chia logic cluster resources |
| ConfigMap | Cấu hình không nhạy cảm |
| Secret | Thông tin nhạy cảm, cần bảo vệ bằng RBAC/encryption policy |
| PersistentVolume/PVC | Storage resources và yêu cầu cấp phát |
| Ingress | Routing HTTP/HTTPS nếu có controller; Gateway API là lựa chọn khác |
| HPA | Scale replica dựa trên metric |

```bash
kubectl get pods -n my-ns
kubectl describe pod my-pod -n my-ns
kubectl logs my-pod -n my-ns
kubectl get deployments -n my-ns
kubectl get svc -n my-ns
```

### 14.3. Pod không lên được

- **Pending:** Thiếu resource, scheduling constraints, PV/PVC unresolved.
- **ImagePullBackOff:** Registry/image/credentials/network.
- **CrashLoopBackOff:** Process/container liên tục chết; đọc logs/events, readiness, config.
- **OOMKilled:** Container vượt memory limit (nếu reported); xem usage, limit, memory leak/workload.

Quy trình: `kubectl get` → `describe` (events) → `logs --previous` khi thích hợp → kiểm tra ConfigMap/Secret, probes, resource requests/limits, network/storage.

### 14.4. OpenShift

OpenShift được xây trên Kubernetes và cung cấp thêm các công cụ quản trị, chính sách bảo mật, routing/deployment/build tùy phiên bản. Kinh nghiệm phát triển Spark SQL trên nền tảng có OpenShift **không đồng nghĩa** kinh nghiệm vận hành cluster K8s.

### 14.5. Linux gắn với DE

Biết `ls`, `pwd`, `cd`, `cat`, `less`, `tail -f`, `grep`, `awk`, `sed`, `find`, `ps`, `top/htop`, `free -h`, `df -h`, `du -sh`, `curl`, `ss -tulpn`, `chmod`, `chown`.

```bash
# Đọc log cuối file
tail -n 100 /var/log/app.log

# Tìm lỗi
grep -nEi 'error|exception|out of memory' /var/log/app.log

# Kiểm tra bộ nhớ/đĩa
free -h
df -h
```

### 14.6. Git và CI/CD

- **Git:** Branch, commit, pull, merge/rebase, pull request, conflict resolution.
- **CI:** Tự động kiểm tra lint, unit tests, SQL compilation, dbt tests.
- **CD:** Triển khai workflow/config/image qua môi trường dev/test/prod có kiểm soát.
- **Code Review:** Kiểm tra logic, bảo mật, migration và rollback.
- **Secret management:** Không commit credentials/token vào Git.

### 14.7. Cloud VM vs Managed Services

CMC Cloud trong dự án demo cung cấp **máy chủ ảo/hạ tầng**. Việc deploy Docker/Airflow/MinIO/PostgreSQL lên VM không tự động có nghĩa bạn dùng managed Kubernetes, serverless, Glue, EMR hay AWS production. Với AWS/GCP/Azure JD nêu, nắm nguyên lý tương ứng: Compute, Object Storage, Network/VPC, IAM, logging, managed databases, scaling, cost.

### 14.8. K8s/DevOps Questions

1. **Docker vs K8s?** Container build/run vs orchestration cluster.
2. **Pod vs Deployment?** Pod đơn vị chạy; Deployment quản lý desired replicas/version rollout.
3. **Service làm gì?** Discovery/endpoint ổn định, load distribution theo cơ chế service.
4. **Secret đủ để bảo mật không?** Cần RBAC, encryption at rest, access audit, network policy.
5. **OOMKilled debug?** Logs, metrics, limit, memory usage, workload.
6. **OpenShift có giống K8s?** Dựa trên K8s, có thêm layer platform.
7. **Bạn làm K8s ở VCB?** Trả lời đúng phạm vi: biết basic và tiếp xúc OpenShift; không tự nhận quản trị cluster khi chưa làm.
8. **CI/CD cho Airflow?** Test DAG import, lint, validate config, deploy DAG/image, rollback, secrets management.
9. **Phân biệt VM với Container?** VM ảo hóa cả guest OS; container chia sẻ kernel host và cô lập process theo cơ chế OS.
10. **Git merge conflict xử lý?** Hiểu base/ours/theirs, giải quyết và chạy tests; không xóa tùy tiện thay đổi của người khác.

---
# C. GIẢI THÍCH SÂU SÁU DỰ ÁN TRONG CV

> Cách kể một dự án: **(1) khách hàng cần gì → (2) kiến trúc và công nghệ → (3) phần mình trực tiếp làm → (4) khó khăn/giải pháp → (5) cách kiểm thử → (6) giới hạn phạm vi trách nhiệm**. Không nhận thiết kế một hệ thống lớn nếu bạn chỉ phát triển các job hoặc một nhánh pipeline.
>
> Các mẫu trả lời dưới đây dựa trên các phần việc bạn đã mô tả, được viết để bạn luyện cách diễn đạt; điều chỉnh nếu thực tế khác và tuyệt đối không tự thêm số liệu hiệu năng/thành tích.

## C1. Vietcombank – Banking CRM System (Spark SQL, Airflow, Trino, OpenShift)

### 1. Bối cảnh và bài toán

Hệ thống CRM cần dữ liệu từ Core Banking và các hệ thống nội bộ để phục vụ nền tảng Salesforce CRM. Trong vai trò Data Engineer, bạn mô tả việc xây dựng/điều chỉnh Spark SQL ETL theo mapping, truy vấn/tiếp nhận dữ liệu nguồn qua Trino, xử lý tầng Staging → Sharing, tối ưu SQL bằng summary tables, kiểm tra kết quả và hỗ trợ troubleshooting.

### 2. Kiến trúc ở mức được biết

```text
Core Banking / Other Banking Systems
             |
    Data Access / Trino
             |
       Staging data
             |
   Spark SQL ETL (Airflow orchestrates)
  joins, filters, mapping, aggregation
             |
       Sharing data
             |
       CRM / Salesforce use

OpenShift: nền tảng môi trường chạy, không mặc định bạn quản trị cluster.
```

**Quan trọng:** Đường dữ liệu thực tế có thể gồm nhiều tầng/connector khác. Không phát biểu rằng Trino tự động chuyển dữ liệu qua Spark theo một giao thức cụ thể nếu bạn không xác nhận trong job.

### 3. Công việc trực tiếp cần giải thích được

- **Mapping:** Mở tài liệu nguồn–đích, xác định source tables, join keys, filter, transform expressions, trường tính toán, null handling.
- **Spark SQL:** Viết JOIN/CASE WHEN/CAST/GROUP BY/Window nếu mapping yêu cầu; chạy job theo cơ chế được team cấu hình.
- **Airflow:** Những task nào gọi SQL/job, dependency ra sao, nơi xem log, retry và kiểm tra status.
- **Staging–Sharing:** Mỗi tầng chứa gì, tiêu chí publish, cách kiểm tra số dòng và các giá trị nghiệp vụ.
- **Optimization:** Summary/pre-aggregation dùng để tránh lặp phép tính hoặc giảm lượng dữ liệu downstream; biết trade-off phải cập nhật bảng trung gian.
- **Data Validation:** Row count, tổng hợp, key matching, nulls, duplicate, logic theo mapping.

### 4. Các câu hỏi truy sâu – đáp án ôn

**Q1. Vì sao Trino và Spark SQL cùng tồn tại?**

Trino chuyên distributed SQL query/federated access qua connectors; Spark SQL chuyên processing ETL phân tán. Một kiến trúc có thể dùng Trino để truy vấn nguồn và Spark làm transformation. Cần xem chính xác luồng của job thực tế.

**Q2. Tại sao dùng Spark thay SQL trực tiếp trong một RDBMS?**

Khi dữ liệu đa nguồn/quy mô lớn hoặc transformation cần distributed processing, Spark có thể phù hợp. Nhưng SQL trong Oracle/Postgres/Trino đôi khi đủ; phải chọn theo volume, locality, cost, throughput và kiến trúc đã có.

**Q3. Airflow thực thi SQL thế nào?**

Airflow là orchestrator, có thể gọi shell/Python/Spark submit/operator, API hoặc cơ chế nội bộ; không tự khẳng định bạn dùng một operator chưa biết. Hãy mô tả đúng job/script/task thực tế.

**Q4. Staging và Sharing khác gì?**

Staging là vùng xử lý trung gian, Sharing là vùng cung cấp dữ liệu đã transform phục vụ hệ tiêu thụ. Rule thực tế tùy kiến trúc.

**Q5. Nếu JOIN gây nhân bản ghi?**

Kiểm tra cardinality/business key và grain; xác định bảng lookup có nhiều dòng theo version, lọc đúng effective date hoặc tổng hợp phù hợp trước khi JOIN; đối soát kết quả.

**Q6. Nếu Sharing thiếu 2% dữ liệu?**

Kiểm tra row count/source keys từng bước; điều kiện filter/inner join, mapping, reject records, cut-off, watermark và sink write; điều tra key bị thiếu trước khi backfill.

**Q7. Summary Table giúp tối ưu thế nào?**

Materialize kết quả tổng hợp dùng nhiều lần, giảm computation. Cần bảo đảm grain, refresh, độ mới và tương đương business logic.

**Q8. Spark SQL khác PySpark?**

Spark SQL là module/query; PySpark là API Python, SQL được gọi qua `spark.sql()` nếu chương trình PySpark dùng nó. Kinh nghiệm chủ yếu viết SQL thì nói đúng vậy.

**Q9. Nếu Spark stage chậm?**

Kiểm tra Spark UI: stage, task duration, shuffle, data skew, spill, physical plan, source scan, partition, join strategy.

**Q10. Nếu ETL output sai nhưng task Success?**

Thêm data-quality checks, kiểm mapping/business rules, reconciliation source-to-target. Success chỉ nói chương trình không báo lỗi theo logic hiện tại.

**Q11. Bạn có dùng Salesforce trực tiếp?**

Nếu không triển khai Salesforce, nói chỉ xây dựng dữ liệu phục vụ hệ CRM; không nhận làm Salesforce developer.

**Q12. Bạn có quản lý OpenShift/K8s cluster?**

Nếu chỉ dùng môi trường triển khai của team, nói không trực tiếp quản trị. Có kiến thức K8s basic và biết debug mức log/workload nếu đã dùng.

### 5. Mẫu trả lời 1–2 phút

> “Ở dự án CRM ngân hàng Vietcombank, nhóm em tham gia tích hợp dữ liệu từ Core Banking và các hệ thống khác để phục vụ nền tảng CRM. Phần của em là phát triển các Spark SQL ETL job theo tài liệu mapping, gồm JOIN, lọc và tổng hợp dữ liệu ở luồng Staging–Sharing. Các job được điều phối qua Airflow trên nền tảng dữ liệu triển khai với OpenShift, có truy xuất nguồn thông qua Trino theo kiến trúc dự án. Em thực hiện kiểm tra dữ liệu sau chạy, hỗ trợ xử lý lỗi và tối ưu một số logic SQL bằng bảng tổng hợp. Em tập trung vào phát triển và chất lượng pipeline chứ không trực tiếp quản trị toàn bộ OpenShift/Salesforce.”

### 6. Điểm cần chuẩn bị trước interview

Phải có ít nhất **một mapping/job bạn thật sự nhớ**, kể được source, target, key, JOIN, rule, số dòng/bottleneck (nếu nhớ), cách test và kết quả. Nếu quên tên bảng hoặc dữ liệu bảo mật, dùng tên giả định **và nói rõ ví dụ đã ẩn thông tin**, không biến ví dụ thành thành tích có thật.

---

## C2. KienlongBank – ODS & Banking Report Optimization (Oracle SQL/PLSQL)

### 1. Bối cảnh

Dự án có khoảng **250 báo cáo cần rà soát/tối ưu hiệu năng** trên Oracle phục vụ ODS và reporting. Con số này là **phạm vi chung**, không phải số báo cáo cá nhân tối ưu. Bạn được giao một phần và hỗ trợ compile, validate, troubleshooting, SIT/UAT.

### 2. Công việc chính

1. Tiếp nhận SQL/PLSQL báo cáo chạy chậm và input parameters.
2. Đo baseline khi có điều kiện (thời gian, volume, plan).
3. Dùng EXPLAIN PLAN/DBMS_XPLAN để tìm scan/JOIN/SORT/group nặng.
4. Viết lại SQL/điều chỉnh JOIN/temporary tables; xem xét indexing khi phù hợp.
5. Compile và kiểm tra lỗi PL/SQL nếu liên quan.
6. Đối soát kết quả trước–sau, hỗ trợ SIT/UAT.

### 3. Một ví dụ tối ưu giả định – tránh nhận làm thật nếu chưa làm

**SQL ban đầu:**

```sql
SELECT t.branch_id, SUM(t.amount)
FROM transactions t
WHERE TRUNC(t.posting_date) = DATE '2026-10-26'
GROUP BY t.branch_id;
```

**Phương án thử:**

```sql
SELECT t.branch_id, SUM(t.amount)
FROM transactions t
WHERE t.posting_date >= DATE '2026-10-26'
  AND t.posting_date <  DATE '2026-10-27'
GROUP BY t.branch_id;
```

Có thể hỗ trợ optimizer tận dụng index/partition tốt hơn, nhưng cần xem thống kê, schema, plan và kết quả thực tế. Không khẳng định cải thiện % khi chưa đo.

### 4. Những câu hỏi truy sâu

**Q1. Bạn dùng `EXPLAIN PLAN` đọc gì?**

Operation, access path, join method, estimated cardinality/cost; nếu có runtime stats đọc actual rows, buffers, elapsed time và compare. Estimated cost không phải execution time.

**Q2. Cách nhận biết bottleneck?**

Xem operator/SQL step có nhiều buffer reads, physical I/O, actual time, nhiều rows hoặc temporary spills; xác minh số liệu thực tế.

**Q3. Vì sao Hash Join thường phù hợp với tập lớn?**

Có thể hash build side và probe side hiệu quả, tránh nhiều random lookups; vẫn chịu memory/temp trade-off.

**Q4. Vì sao Nested Loops đôi khi tốt?**

Outer nhỏ và inner có index/cheap lookup, tiết kiệm scan toàn bảng.

**Q5. Khi nào dùng temp table?**

Khi kết quả intermediate phải tái sử dụng hoặc tách expensive computation mang lại lợi ích đã benchmark; chú ý TEMP I/O và scope dữ liệu.

**Q6. Bạn có tự tạo index không?**

Phân biệt đề xuất, thử nghiệm, tạo index thật; quyền production có thể do DBA. Đừng ghi “đã tạo” nếu chỉ đánh giá phương án.

**Q7. Lỗi compile procedure?**

Kiểm tra syntax, dependencies, permissions, type mismatch; xem `SHOW ERRORS` hoặc `USER_ERRORS` theo quyền, sửa rồi compile/test.

**Q8. Tối ưu nhanh nhưng tổng tiền khác?**

Không được chấp nhận, phải điều tra filter/joins/cardinality/nulls/rounding; so sánh dữ liệu chi tiết và các KPI nghiệp vụ.

**Q9. Vì sao có index mà query vẫn Full Scan?**

Nếu quét nhiều dòng hoặc selectivity thấp, full scan có thể cost tốt hơn; cũng xét thống kê và predicate.

**Q10. Source có 250 reports, bạn làm bao nhiêu?**

Trả lời đúng số trực tiếp được giao/đã làm và mức hỗ trợ; không gộp số dự án vào số thành tích cá nhân.

**Q11. Oracle ODS khác DWH?**

ODS thường tích hợp gần vận hành; DWH mô hình hóa để phân tích/lịch sử. Chức năng thực tế phụ thuộc thiết kế.

**Q12. SQL tuning có thể gây regression?**

Có. Plan/parameter/cardinality có thể thay đổi; benchmark nhiều inputs, data volumes và kiểm thử regression.

### 5. Mẫu trả lời 1–2 phút

> “Em tham gia dự án tối ưu hệ thống ODS và báo cáo ngân hàng của KienlongBank trên Oracle. Phạm vi dự án có khoảng 250 báo cáo cần rà soát, còn em được giao một phần trong đó. Công việc của em là phân tích SQL/PLSQL chạy chậm, xem execution plan để tìm điểm nghẽn rồi áp dụng viết lại truy vấn, tối ưu JOIN hoặc dùng bảng tạm ở các trường hợp phù hợp. Em cũng hỗ trợ compile, kiểm tra và đối soát dữ liệu trước–sau để bảo đảm truy vấn tối ưu không làm sai số liệu, cùng các bước SIT/UAT.”

### 6. Điều dễ bị bắt bẻ

Nếu interviewer yêu cầu số report bạn **cá nhân tối ưu**, không nói “250” hoặc “15” khi chỉ là scope nhóm. Nếu chưa ghi lại before/after, mô tả giải pháp/tiêu chí đo thay vì tự tạo số giây phần trăm.

---

## C3. Gimasys – Vietnam Airlines Reporting Migration (BigQuery → ClickHouse)

### 1. Bối cảnh

Bạn thuộc InsightData, tham gia công việc từ xa qua Gimasys cho hệ thống báo cáo thương mại Vietnam Airlines. Mục tiêu dự án là chuyển workload từ BigQuery sang ClickHouse để tối ưu chi phí và hiệu năng theo yêu cầu khách hàng.

### 2. Nhiệm vụ bạn đã mô tả

- Migration table/view/logic procedure từ BigQuery sang ClickHouse; điều chỉnh schema mới.
- Với view/procedure nặng, chuyển sang dbt models materialized thành bảng vật lý để giảm query-time computation.
- Tải dữ liệu theo từng partition/batch ngày hoặc tháng, phụ thuộc partition và volume để kiểm soát peak memory, tránh OOM.
- Tối ưu query/logic dbt, JOIN/filter và table structure; đánh giá index/sorting keys.
- Validation kết quả giữa hệ nguồn và đích.

### 3. Vì sao ClickHouse khác BigQuery?

**BigQuery:** Managed cloud analytic warehouse với cơ chế scaling và mô hình billing riêng. **ClickHouse:** Column-oriented analytic DB, nhiều biến thể managed/self-hosted. Bảng MergeTree có ORDER BY/sparse index. Không nói ClickHouse luôn nhanh/rẻ hơn; depends on workload, compute/storage, vận hành.

### 4. MergeTree, ORDER BY, PARTITION BY, Index

```sql
CREATE TABLE demo_transactions (
  txn_id String,
  customer_id String,
  txn_date Date,
  amount Decimal(18,2)
)
ENGINE=MergeTree
PARTITION BY toYYYYMM(txn_date)
ORDER BY (customer_id, txn_date);
```

- `PARTITION BY` giúp tổ chức parts thành partition để quản lý/skip ở điều kiện phù hợp, không dùng để tạo hàng triệu partition nhỏ.
- `ORDER BY` định nghĩa thứ tự sắp xếp vật lý theo sorting key, cực quan trọng cho data skipping.
- Sparse primary index khác B-tree lookup của Oracle.
- Data skipping index hữu ích cho một số điều kiện và phân phối dữ liệu, nhưng thêm index có overhead.

### 5. Vì sao tránh OOM bằng daily/monthly batch?

Giới hạn tập dữ liệu mỗi lần đọc/transform/insert, giảm peak RAM, tránh query intermediate quá lớn và dễ retry đúng kỳ. Nhưng batch quá nhỏ tạo overhead và nhiều ClickHouse data parts; phải cân đối kích thước.

### 6. Vì sao chuyển heavy views/procedures sang dbt table?

View logic nặng có thể phải chạy lại mỗi lần báo cáo truy vấn; precompute thành bảng vật lý chuyển chi phí sang refresh, giúp đọc thường nhanh hơn. Phải quản lý freshness, SQL equivalence, load strategy và dữ liệu lịch sử.

### 7. Các câu hỏi truy sâu

**Q1. Dữ liệu BigQuery và ClickHouse có kiểu dữ liệu tương đương hoàn toàn không?**

Không; cần mapping kiểu số, Nullable, Date/DateTime/timezone, String, array và SQL functions.

**Q2. BigQuery stored procedure chuyển sang ClickHouse stored procedure 1:1?**

Không mặc định. Một số procedural/SQL logic phải thiết kế lại thành dbt models/ETL jobs vì khác feature set.

**Q3. Tại sao chia ngày/tháng?**

Giới hạn peak memory và workload của từng batch, giúp retry theo kỳ.

**Q4. OOM nguyên nhân gì?**

Intermediate JOIN/aggregation lớn, sort, concurrency, memory limit, batch quá lớn; điều tra query plan/resource.

**Q5. Bạn đã dùng index gì?**

Nêu chính xác `ORDER BY`, sorting key hay skipping index nào nếu thực sự làm; không gọi chung “đánh index như Oracle”.

**Q6. `dbt materialized='table'` khác incremental?**

Table thường rebuild kết quả; incremental chỉ biến đổi phần cần cập nhật, phụ thuộc adapter/config.

**Q7. Hệ thống sau migration sai số tổng doanh thu, kiểm ở đâu?**

Data types, timezone/currency, NULL, join, rounding, missing partitions, procedure translation, aggregation grain.

**Q8. Dữ liệu ClickHouse quá nhiều parts?**

Kiểm soát batch size, insert frequency, partitioning và background merges; tránh nhiều inserts nhỏ.

**Q9. Tại sao không chỉ dùng materialized view?**

Cần phân biệt ClickHouse materialized view engine semantics, refresh model của dbt và tính phức tạp migration; chọn theo refresh/consistency/workload.

**Q10. Bạn chứng minh giảm chi phí bằng gì?**

Chỉ nói số liệu khi dự án thực sự có benchmark/billing. Nếu không, mô tả đó là mục tiêu dự án, không là KPI cá nhân đã xác minh.

### 8. Mẫu trả lời 1–2 phút

> “Em tham gia dự án chuyển nền tảng báo cáo thương mại từ BigQuery sang ClickHouse qua Gimasys. Em xử lý migration các bảng, view và logic procedure, chuyển đổi schema và SQL cho phù hợp hệ thống đích. Với các view/procedure tốn tài nguyên, em chuyển logic sang dbt model và materialize kết quả thành bảng. Em chia dữ liệu theo partition ngày hoặc tháng khi extract/load để giới hạn memory, tránh OOM; sau đó tối ưu query và đối soát dữ liệu giữa hai nền tảng. Em phân biệt rõ phần thiết kế/triển khai trực tiếp với mục tiêu hiệu năng chung của dự án.”

---

## C4. HG Media – Data Warehouse & Intelligent Reporting

### 1. Bối cảnh nghiệp vụ

HG Media quản lý tài nguyên âm nhạc/video qua nhiều hệ: Odoo (sản xuất/thu mua), HG Stock (lưu kho/phân phối), hệ quản lý kênh YouTube, công cụ phân tích, distributor/DSP và file báo cáo. Cần một DWH tập trung chuẩn hóa dữ liệu phục vụ báo cáo về sản xuất, sử dụng tài nguyên, hệ thống kênh và thị trường YouTube.

### 2. Kiến trúc / tech stack bạn cung cấp

```text
Odoo / HG Stock / Channel Tools / Excel / Elasticsearch / Distributor
                             |
                Python ingestion / integrations
                             |
                    MinIO (RAW files)
                             |
                   PostgreSQL Staging
                             |
                    dbt transformations
                        Silver → Gold
                             |
                      Reporting/BI
           Apache Airflow orchestration; Docker runtime
```

Các nguồn cụ thể và mức độ tự động thu thập từng nguồn phải theo scope bạn trực tiếp thực hiện; không mặc định bạn tự viết crawler Selenium nếu chỉ mô tả hệ thống chung.

### 3. Master Data – bài toán thú vị nhất

Một tài nguyên âm nhạc có thể có `Resource ID`, `ISRC`, `Editing Code`, `YouTube Video ID`, distributor identifier. Nếu không mapping, doanh thu của cùng bài nhạc dễ bị phân tán theo tên/ID khác nhau.

**Data Mastering:** Xây dựng bảng mapping nguồn → master ID, kiểm tra one-to-one vs one-to-many, xử lý unmatched IDs và thay đổi lịch sử.

### 4. Star Schema và KPI

Ví dụ khái quát (không khẳng định schema production):

- `dim_resource(resource_key, resource_id, title, artist_key, ...)`
- `dim_platform(platform_key, platform_name, ...)`
- `dim_date(date_key, ...)`
- `fact_streams(date_key, resource_key, platform_key, streams, estimated_revenue)`

**Grain:** Một bản ghi theo ngày + resource + platform (+ geography/distributor nếu theo nghiệp vụ). Nếu JOIN dim bản quyền nhiều dòng, có thể nhân doanh thu.

### 5. Các câu hỏi truy sâu

**Q1. Vì sao làm DWH thay vì dashboard truy vấn nhiều hệ trực tiếp?**

Chuẩn hóa key/schema, giảm tải nguồn, quản lý business logic và một nguồn dữ liệu được kiểm soát.

**Q2. Tại sao Raw và Staging đều cần?**

Raw giữ dữ liệu gốc, Staging chuyển thành schema kiểu dữ liệu có thể transform/query; dễ reprocess.

**Q3. Master Data là gì?**

Tập các thực thể chuẩn dùng liên kết dữ liệu xuyên hệ, cần rules xử lý duplicate và mapping.

**Q4. Nếu doanh thu của một track lệch giữa distributor và BI?**

Kiểm tra source cutoff/độ trễ báo cáo, tỷ giá, rate, aggregation grain, ISRC mapping và kỳ dữ liệu.

**Q5. Dữ liệu tới từ Excel và Elasticsearch khác nhau?**

Ingestion connector/parser khác; về Silver chuẩn hóa về schema/business definitions chung.

**Q6. dbt dùng ở đâu?**

Các bước làm sạch, mapping, transform từ Staging sang Silver/Gold theo yêu cầu đã nêu.

**Q7. Khi source thay đổi schema?**

Phát hiện qua test/contract, cập nhật mapping và kiểm downstream.

**Q8. Có cần SCD?**

Khi business yêu cầu theo dõi thay đổi tài nguyên/artist/ownership theo thời gian; xác định chính xác thuộc tính nào cần lịch sử.

### 6. Mẫu trả lời

> “HG Media có nhiều hệ thống quản lý sản xuất, lưu kho và khai thác nội dung số nên dữ liệu chưa tập trung. Em tham gia xây dựng pipeline thu thập dữ liệu đa nguồn bằng Python; dữ liệu gốc lưu MinIO, dữ liệu có cấu trúc đưa vào PostgreSQL Staging. Nhóm dùng dbt transform sang Silver/Gold theo mapping và Airflow để điều phối. Kết quả hướng tới việc cung cấp dữ liệu thống nhất cho các báo cáo kinh doanh. Phần em tập trung vào ingestion/transformation và phối hợp kiểm tra dữ liệu.”

---

## C5. Go Minh Long – MISA Excel Data Integration & Reporting

### 1. Bài toán

Gần 20 định dạng báo cáo Excel xuất từ MISA. Khó khăn: merged cells, nhiều hàng header, định dạng sheet khác nhau, tổng/subtotals xen lẫn chi tiết, kiểu ngày/số không đồng nhất. Bạn xây công cụ lấy báo cáo và module Python bóc tách dữ liệu, load Staging → Silver → Dashboard, dùng Airflow/dbt/MinIO/PostgreSQL/Docker.

### 2. Một kiến trúc hợp lý với mô tả

```text
MISA -> công cụ lấy/tải Excel -> MinIO Raw (giữ nguyên)
     -> Python parser theo report type -> PostgreSQL Staging
     -> dbt clean/map/integrate -> Silver -> dashboard
Airflow orchestration; Docker containers
```

Phương thức tải Excel (API/browser/manual export) chưa xác định từ mô tả, **không tự nhận Selenium/Playwright**.

### 3. Tư duy thiết kế parser

- Tách từng **report type**, có rule nhận diện sheet/header/table position.
- Tách layer ingestion file vs parsing vs validation vs load.
- Ghi metadata: source file, timestamp, report type, kỳ dữ liệu, checksum nếu cần.
- Chuẩn hóa column names, dtypes, decimal separator, date formats.
- Xử lý `merged cells` dựa theo ý nghĩa nghiệp vụ, không fill mù tất cả ô trống.
- Bỏ các dòng tổng/nhãn không phải fact chi tiết theo rule.
- Data Quality: số bản ghi, schema, business key, tổng tiền nếu áp dụng.
- On failure: quarantine/báo file sai template, không silently ingest.

### 4. Các câu hỏi truy sâu

**Q1. Vì sao không dùng một `pandas.read_excel()` duy nhất?**

File thay đổi header, merged cells và nhiều bảng phụ; cần template parsing.

**Q2. `openpyxl` so với `pandas`?**

openpyxl thao tác workbook/cells/merged ranges; pandas tốt cho tabular transform sau khi xác định vùng dữ liệu.

**Q3. Dữ liệu không có schema?**

Excel vẫn có cấu trúc nhưng không nhất quán; gọi *semi-structured/irregular tabular*. Chọn từ chính xác.

**Q4. Thay đổi format MISA thì sao?**

Detect template/version, validate schema, cập nhật parser, test regression.

**Q5. Nếu file tải lại hai lần?**

File hash/batch ID, business key và idempotent load, tránh duplicate.

**Q6. Vì sao MinIO?**

Giữ bản nguồn, audit và reprocess.

**Q7. dbt đóng vai trò gì?**

Transform, cleaning/mapping từ Staging sang Silver; Airflow gọi workflow.

**Q8. Xử lý báo cáo tổng hợp có số tổng không bằng cộng các dòng?**

Xác minh hidden rows, rounding, business rules, filters và cách report format; không tự sửa bằng ép tổng.

### 5. Mẫu trả lời

> “Ở dự án GML, em tham gia tự động hóa việc thu thập gần 20 loại báo cáo Excel từ MISA. Vấn đề chính là các file có header, merged cells và cấu trúc khác nhau nên em dùng Python thiết kế logic bóc tách/chuẩn hóa theo từng mẫu. File gốc được lưu MinIO, dữ liệu chuẩn hóa nạp PostgreSQL Staging rồi dùng dbt xử lý sang Silver để phục vụ dashboard. Em dùng Airflow điều phối workflow trên môi trường Docker.”

---

## C6. CMC Cloud Infrastructure – Technical Demo Data Pipeline & BI

### 1. Bối cảnh

Đây là **technical demo/PoC**, phối hợp cùng CMC giới thiệu giải pháp dữ liệu cho khách hàng. CMC cấp máy chủ ảo (dịch vụ infrastructure/cloud VM). Nhóm triển khai Docker, Airflow, MinIO, PostgreSQL và tích hợp Power BI Service qua Power BI Gateway theo mô tả của bạn.

### 2. Kiến trúc

```text
[CSV Files] -> [MinIO Raw] -> [ETL job] -> [PostgreSQL] -> [Power BI]
                             ^                              ^
                         Airflow DAG                  Gateway/Refresh
         Container deployment on CMC-provided virtual machine
```

Điểm cần phân biệt: Máy chủ ảo do CMC Cloud cung cấp **không đồng nghĩa** bạn đã triển khai Kubernetes managed, serverless hay một hệ thống production SLA cao.

### 3. Các khái niệm phải trả lời

- **Docker vs VM:** VM ảo hóa guest OS; Docker container đóng gói ứng dụng trên kernel host.
- **MinIO:** Lưu raw, hỗ trợ audit/replay.
- **Airflow:** Lập lịch/orchestrate extract → transform → load/validation.
- **PostgreSQL:** Dữ liệu có cấu trúc cho BI.
- **Power BI Gateway:** Kết nối nguồn dữ liệu cần gateway từ Power BI Service; refresh schedule cấu hình ở Service; gateway không tự ETL CSV.
- **Power BI Desktop vs Service:** Desktop xây report/model, Service host/share/refresh theo configuration.

### 4. Các câu hỏi truy sâu

**Q1. Khi dựng demo bước đầu làm gì?**

Kiểm tra VM/network/security, Docker/Compose, volumes, database credentials, endpoints, deploy service, smoke test và sample data.

**Q2. Vì sao dùng MinIO trước Postgres?**

Lưu raw và tách ingestion/processing, cho phép re-run và troubleshooting.

**Q3. Power BI không refresh?**

Kiểm tra data source credentials, Gateway online, network/database access, mapping dữ liệu, Power BI refresh history, schedule/timeout.

**Q4. Airflow failed ngay trước demo?**

Xem log, restore bằng retry an toàn, kiểm tra dataset; có thể chuẩn bị snapshot demo nếu đã thống nhất và không đánh lừa khách hàng về dữ liệu live.

**Q5. Vì sao Docker?**

Môi trường nhất quán và triển khai nhanh nhiều services trên VM.

**Q6. Dữ liệu demo có phản ánh production?**

Không mặc định; phải công khai là PoC khi nói scalability/availability.

**Q7. Có cần backup DB?**

Nếu system quan trọng, có; với demo tùy mức độ cần bảo toàn. Dùng volume và backup đúng chiến lược.

**Q8. Scheduled refresh và DirectQuery khác nhau?**

Import-mode cần refresh để cập nhật data model; DirectQuery truy vấn nguồn khi thực hiện truy vấn phù hợp, đòi hỏi connectivity và performance phù hợp.

### 5. Mẫu trả lời

> “Đây là dự án technical demo về giải pháp xử lý dữ liệu end-to-end. CMC cung cấp máy chủ ảo, nhóm em triển khai các thành phần qua Docker, xây pipeline CSV → MinIO → PostgreSQL và dùng Airflow để điều phối. Sau đó cấu hình Gateway phục vụ Power BI Service và kiểm thử luồng dữ liệu từ nguồn đến dashboard. Em phối hợp cùng đội CMC để trình diễn giải pháp cho khách hàng. Đây là PoC/demo chứ không phải hệ thống production được vận hành lâu dài.”

---
# D. KIẾN THỨC RIÊNG THEO HAI JD VPBANK

## D1. Banking domain: cần biết gì dù bạn là Data Engineer?

### 1. Các hệ thống phổ biến

| Thuật ngữ | Ý nghĩa phổ biến | Data Engineer thường quan tâm |
|---|---|---|
| Core Banking | Hệ thống nghiệp vụ cốt lõi (tài khoản, giao dịch...) | Source, business date, transaction consistency |
| CRM | Quản lý thông tin và tương tác khách hàng | Customer 360, master mapping, serving |
| ODS | Kho dữ liệu vận hành tích hợp | Source mapping, freshness, consistency |
| DWH | Kho dữ liệu phân tích/lịch sử | Fact/dim, SCD, aggregates |
| LOS | Loan Origination System | Dữ liệu hồ sơ và quy trình khoản vay |
| LMS | Loan Management System (trong ngữ cảnh cho vay) | Dư nợ, lịch thanh toán, trạng thái khoản vay |
| BI/Reporting | Khai thác và trực quan hóa | KPIs, data marts, reconciliation |
| AML/Fraud | Chống rửa tiền/phát hiện gian lận | Latency, streaming, audit, rules |

Đây là thuật ngữ ngành, **không phải danh sách hệ thống chính thức của VPBank**.

### 2. Khách hàng – tài khoản – giao dịch – khoản vay

Một Banking Data Model tổng quát có thể bao gồm:

- `customer` / `customer_identifier` / `customer_contact` / `customer_segment`
- `account` / `customer_account_relationship` (hỗ trợ N:M)
- `transaction` / `transaction_status` / `transaction_channel`
- `loan` / `repayment_schedule` / `disbursement` / `repayment`
- `branch` / `product` / `currency` / `exchange_rate`
- `daily_balance` / `account_snapshot`

**Cần biết rõ grain:** Một dòng `transaction` không luôn bằng một nghiệp vụ hoàn chỉnh; một transaction có thể có legs/entries, reversal hoặc posting records. Định nghĩa theo tài liệu nguồn.

### 3. CIF, account ID, business date, posting date

- **CIF/Customer ID:** Mã khách hàng trong phạm vi hệ thống quy định, không mặc định globally unique qua mọi hệ.
- **Account ID:** Tài khoản; quan hệ customer–account có thể phức tạp.
- **Transaction time:** Thời gian phát sinh theo hệ thống ghi nhận.
- **Posting date:** Ngày hạch toán.
- **Business date/EOD:** Ngày nghiệp vụ được xác lập theo quy tắc ngân hàng.
- **Settlement date:** Ngày hoàn tất quyết toán/thanh toán theo ngữ cảnh nghiệp vụ.

**Bẫy:** Query dùng ngày giao dịch thay ngày hạch toán thì báo cáo EOD có thể lệch, dù SQL không báo lỗi.

### 4. Reversal, cancellation, adjustment

Phải hỏi business rule khi tính tổng giao dịch:

- Giao dịch có status SUCCESS/POSTED mới tính hay không?
- Giao dịch bị đảo có tính âm hay loại bỏ?
- Một giao dịch được điều chỉnh vào ngày sau, báo cáo lịch sử có restate không?
- Có đa tiền tệ không, chọn tỷ giá lúc nào?
- Có hoàn tiền/refund và double-count không?

### 5. Financial decimal, rounding và currency

Dữ liệu tiền nên sử dụng kiểu exact decimal có precision/scale phù hợp (Oracle NUMBER, PostgreSQL NUMERIC/DECIMAL...) để kiểm soát rounding. Khi quy đổi ngoại tệ, ngày tỷ giá và quy tắc làm tròn phải theo nghiệp vụ, không tự suy diễn.

### 6. Snapshot balance vs transaction flow

- **Transaction amount:** Flow measure, có thể cộng trong kỳ nếu business rules phù hợp.
- **End-of-day balance:** Snapshot/stock measure, cộng qua ngày có thể vô nghĩa. Có thể cộng qua tài khoản ở cùng thời điểm nếu thích hợp.

### 7. Đối soát ngân hàng

Một pipeline tổng hợp giao dịch phải so sánh:

- Row count theo business_date, source, transaction type.
- Tổng amount theo currency/status/branch.
- Missing/duplicate transaction IDs.
- Giao dịch đảo/điều chỉnh.
- Late postings.
- Balance rollforward nếu nghiệp vụ có thể áp dụng: `opening + credits - debits ± adjustments = closing` theo đúng dấu và quy tắc.

### 8. Bảo mật dữ liệu

- Least privilege, RBAC, service accounts, encryption in transit/at rest theo nền tảng.
- Masking/tokenization/pseudonymization cho PII và dữ liệu nhạy cảm.
- Không hardcode credential; quản lý secret.
- Audit logs, source lineage, phân quyền môi trường dev/test/prod.
- Không chụp hay sao chép dữ liệu thật từ ngân hàng ra môi trường cá nhân để làm ví dụ phỏng vấn.

---

## D2. Phân tích yêu cầu và chuyển thành thiết kế kỹ thuật

**Ví dụ BA yêu cầu:** “Báo cáo doanh số theo chi nhánh và khách hàng VIP mỗi ngày.”

Trước khi viết SQL, bạn phải hỏi:

1. “Doanh số” = tổng phát sinh giao dịch nào? Có reversal/refund không?
2. Dùng transaction_date hay posting_date?
3. “VIP” là trạng thái hiện tại hay tại ngày giao dịch? (SCD)
4. Chi nhánh phát sinh hay chi nhánh quản lý khách hàng?
5. Đa tiền tệ có quy đổi không? Tỷ giá ngày nào?
6. Cutoff/EOD lúc nào? Late-arriving được restate không?
7. Data volume, SLA, tần suất cập nhật, hình thức query?
8. Tiêu chí chấp nhận số liệu và người ký nghiệm thu?

Sau đó tạo source-to-target mapping, fact grain, DQ checks, versioned transformation, test cases và runbook.

**Phỏng vấn hỏi “BA yêu cầu mơ hồ?”** – Không đoán business rule, đưa ví dụ phản chứng và hỏi xác nhận trước triển khai.

---

## D3. Thiết kế hệ thống ETL/ELT ngân hàng từ đầu

### Đề bài giả định

“Thiết kế một hệ thống nhận dữ liệu giao dịch từ Core Banking, cung cấp số liệu dashboard đến 7h sáng hôm sau.”

### Đáp án hệ thống

**Bước 1 – Requirements**

- Source tables/contract, volume, peak, growth, lịch nguồn đóng sổ.
- Business date, timezone, late arrival, UPDATE/DELETE/reversal.
- SLA 7h, data quality, RPO/RTO, security, retention.

**Bước 2 – Ingestion**

Chọn CDC nếu nguồn/latency hỗ trợ, hoặc incremental timestamp/partition query hợp lý. Raw append với metadata: source, ingest_time, business_date, batch_id, checksum khi cần.

**Bước 3 – Staging/Silver**

Kiểm schema, dữ liệu lỗi, kiểu ngày/số, normalization, dedup, master mapping, validate referential integrity.

**Bước 4 – DWH Model**

`fact_transaction` (grain 1 transaction posting nếu nghiệp vụ quy định), `dim_customer`, `dim_branch`, `dim_product`, `dim_date`; SCD2 nếu cần phân tích lịch sử.

**Bước 5 – Orchestration**

Airflow DAG extract → validate raw → transform → load/publish → reconcile → notify. Retry idempotent, backfill period, concurrency phù hợp nguồn.

**Bước 6 – Observability & Security**

Metrics/logs/alert, SLA freshness, data reconciliation, RBAC, secrets, audit, runbook.

### Câu trả lời miệng chuẩn

> “Đầu tiên em sẽ xác định business definition, dữ liệu nguồn, volume, lịch chốt dữ liệu và SLA. Sau đó lựa chọn cơ chế incremental/CDC phù hợp, lưu Raw để truy vết và staging để kiểm tra kiểu dữ liệu. Em thiết kế fact/dimension dựa trên grain và lịch sử thuộc tính, dùng SQL hoặc Spark để transform, điều phối Airflow và bảo đảm idempotent load/backfill. Cuối cùng thêm reconciliation, monitoring, cảnh báo và kiểm soát quyền truy cập để báo cáo đúng và có thể khôi phục khi lỗi.”

### Các trade-off nên tự đặt câu hỏi

- Làm Full Refresh đơn giản hơn nhưng tốn chi phí; incremental phức tạp hơn nhưng hiệu quả hơn ở bảng lớn.
- Pre-aggregation giúp BI nhanh nhưng tăng độ trễ làm mới và storage.
- Streaming giảm latency nhưng tăng chi phí/state/error semantics.
- Partitioning giúp pruning nhưng quá nhiều partition gây overhead.
- SCD2 giữ lịch sử nhưng yêu cầu join by effective date.
- Data Quality chặn publish có thể trễ SLA nhưng bảo vệ accuracy; cần severity chính xác.

---

## D4. Data Product, Governance, Data Contract và Lineage (mở rộng từ JD Alphaway)

**Data Product:** Bộ dữ liệu/đầu ra được quản lý như sản phẩm: có owner, SLA, schema, chất lượng, tài liệu, version, nhóm consumer và quy trình thay đổi. Không phải chỉ là “một bảng trong database”.

**Data Contract:** Thỏa thuận định dạng và ý nghĩa dữ liệu giữa source và consumer: schema, field definitions, nullable, key, freshness, compatibility, trách nhiệm thay đổi.

**Lineage:** Ghi nhận dữ liệu đầu ra có nguồn từ đâu, qua những job/model nào và chịu tác động thế nào khi schema thay đổi.

**Data Governance:** Quyền sở hữu, phân quyền, phân loại dữ liệu, lưu giữ, audit, tiêu chuẩn chất lượng và quy trình quản lý thay đổi.

**Hỏi “Nếu source đổi kiểu cột tiền từ INT sang STRING?”** – Kiểm tra impact, contract, parser/cast, schema target, fallback, regression tests và lịch triển khai; không để cast im lặng sai dữ liệu.

---

## D5. So sánh công nghệ trong hai JD với năng lực bạn mô tả

| JD đề cập | Kiến thức phải nắm | Điểm CV liên quan | Lưu ý trung thực |
|---|---|---|---|
| Banking Domain | ODS, CRM, giao dịch, đối soát, EOD | VCB/KLB | Không nhận nghiệp vụ chưa từng phụ trách |
| SQL/Oracle/Postgres | Joins, execution plan, transaction, index, tuning | KLB, GML, HG | Chỉ nhận index/procedure bạn thật sự triển khai |
| Spark SQL/Python | Shuffle, join, data skew, ETL, parsing | VCB, GML | Không đồng nhất Spark SQL với PySpark coding |
| ETL/ELT | Mapping, incremental, idempotent, validation | Cả 6 dự án | Cần kể một job cụ thể |
| Airflow | DAG, task, logs, retries, backfill | VCB, HG, GML, CMC | Nói rõ tự viết DAG hay chỉnh job/task |
| DWH/Lakehouse | ODS, fact/dim, medallion, files, catalog | HG, Gimasys | Phân biệt role design vs development |
| Kafka/Streaming | Topic, offset, group, semantics | Chủ yếu kiến thức nền | Chưa có bằng chứng triển khai production |
| Cloud/K8s | VM, Docker, Pod, Service, OpenShift | CMC/VCB | K8s (Basic) ≠ cluster admin |
| dbt | models, materialization, tests | HG, Gimasys, GML | Nói đúng table vs incremental |
| DataStage/ODI/Glue/EMR | Phân biệt ETL tools và managed Spark/orchestration | Không ghi trong CV | Chỉ trả lời nguyên lý/khả năng học, đừng nhận kinh nghiệm |
| IBM DWH, Redshift, Databricks | Storage/SQL engines, query cost, Spark platform | Không có bằng chứng project | Kiến thức mở rộng, không ghi đã làm |
| Python/Java/Scala | SQL + một ngôn ngữ lập trình đủ tốt | Python, Java trong skills | Tự đánh giá độ thành thạo thật |

---

## D6. Incident Response: xử lý sự cố pipeline một cách chuyên nghiệp

**Ví dụ:** 05:30 pipeline tổng hợp giao dịch ngày trước chưa cập nhật xong, SLA 07:00.

1. **Triage:** Xác định hệ thống/luồng/partition bị ảnh hưởng, severity, SLA.
2. **Evidence:** Xem Airflow logs, query logs, Spark UI, tài nguyên, freshness, row count.
3. **Root cause hypothesis:** Nguồn đến muộn? Schema change? Bad SQL plan? OOM? Permission? Sink full?
4. **Containment:** Tránh phát hành dữ liệu sai hoặc thông báo degraded state theo quy định.
5. **Recovery:** Retry/backfill/idempotent replay, cân nhắc rollback để tránh lỗi lan.
6. **Validation:** Đối soát raw→target, số lượng, số tiền, business status.
7. **Communication:** Cập nhật BA/BI/ops: ảnh hưởng, dữ liệu kỳ nào, ETA do nhóm chịu trách nhiệm xác định, không hứa tùy tiện.
8. **Prevention:** Alerts, DQ, runbook, tuning, capacity planning, RCA.

**Câu hỏi “Production đang lỗi, em có sửa dữ liệu tay không?”** – Không tự ý sửa production nếu chưa được cấp quyền/quy trình. Có thể đề xuất correction script có review/audit/backup/rollback khi thực sự cần.

---

## D7. Data Security – hỏi nhiều trong môi trường ngân hàng

- **Access control:** Least privilege, service-to-service identities, RBAC, separation of duties.
- **Encryption:** At rest/in transit theo nền tảng.
- **Secrets:** Secret manager/connection backend; không commit Git, không in log.
- **Audit:** Truy vết ai đọc/sửa, lineage và change history khi phù hợp.
- **PII:** Mask/redact/tokenize test datasets.
- **Environment isolation:** Dev/UAT/Prod tách dữ liệu và quyền.
- **Retention:** Tuân thủ chính sách dữ liệu, không tự đặt thời hạn.

**Hỏi “Muốn debug dữ liệu khách hàng nhưng không được lấy prod data về máy cá nhân?”** – Dùng truy cập được phân quyền, dữ liệu masked/synthetic, log an toàn và test trong môi trường được phép.

---
# E. PHỎNG VẤN GIẢ LẬP: CÂU HỎI VÀ ĐÁP ÁN

> Các câu dưới đây được viết để **đọc thành tiếng và tự trả lời**, không chỉ học thuộc. Một câu trả lời tốt thường bắt đầu 1–3 câu đúng trọng tâm, sau đó giải thích sâu và nêu ví dụ nếu được hỏi tiếp. **Dấu [Tình huống giả định]** nghĩa là cách xử lý kỹ thuật đề xuất, không phải kinh nghiệm đã xác minh của cá nhân.

## E1. Giới thiệu bản thân và cách nói về kinh nghiệm

### Q1. Em hãy giới thiệu ngắn gọn về bản thân và kinh nghiệm Data Engineer?

**Mẫu đáp dựa trên các công việc đã mô tả:**

> “Em đang theo học ngành Khoa học Máy tính tại PTIT và có kinh nghiệm tham gia các dự án Data Engineering về tích hợp dữ liệu, ETL/ELT, Data Warehouse và SQL tuning. Ở Vietcombank, em tập trung phát triển Spark SQL ETL theo mapping và kiểm tra dữ liệu. Ở KienlongBank, em tham gia phân tích/tối ưu Oracle SQL và PL/SQL cho báo cáo. Ngoài banking, em có trải nghiệm migration BigQuery sang ClickHouse với dbt, xây pipeline Python/Airflow và hệ demo trên Cloud VM. Điểm mạnh của em là SQL, pipeline development, kiểm tra dữ liệu và khả năng phân tích sự cố.”

Không dùng con số năm kinh nghiệm hoặc timeline không khớp hồ sơ/hợp đồng thật.

### Q2. Trong 6 dự án, đâu là dự án mạnh nhất?

Chọn **VCB** nếu role yêu cầu Spark/Airflow/Banking, hoặc **KLB** nếu role yêu cầu Oracle/SQL tuning. Nên bảo vệ sâu được một job và một tình huống thật, không chỉ kể tên công nghệ.

### Q3. Em đã thiết kế pipeline end-to-end chưa?

Trả lời phân tầng: “Ở GML/CMC em có tham gia dựng nhiều bước từ ingest đến reporting; ở VCB em chủ yếu phát triển Spark SQL job theo mapping trong pipeline có sẵn. Em không nhận mình tự thiết kế toàn bộ kiến trúc VCB nếu vai trò của em không phải vậy.”

### Q4. Tại sao có thể phỏng vấn level Middle dù chưa tốt nghiệp?

Đánh giá dựa trên khả năng giải quyết bài toán và trách nhiệm thực tế; chưa tốt nghiệp là điểm cần minh bạch. Không lấy “lương kỳ vọng” thay cho bằng chứng kỹ thuật.

### Q5. Điểm yếu kỹ thuật hiện tại của em?

Một ví dụ trung thực: “Em có kiến thức nền Kafka/Kubernetes nhưng chưa trực tiếp chịu trách nhiệm vận hành cluster streaming production; em đã tập trung ôn semantics, monitoring, K8s resources và sẵn sàng theo kiến trúc của team.” Chỉ nói thế nếu đúng.

### Q6. Em thường làm gì khi nhận task mới từ BA?

“Xác nhận business rule, source/target, mapping, grain, kỳ dữ liệu, SLA và test conditions; ước lượng tác động, triển khai, kiểm thử, code review, bàn giao tài liệu.”

### Q7. Em có thể làm việc độc lập đến đâu?

Nêu task tự làm thực tế (SQL mapping, parser, dbt model, Airflow job, validation), ranh giới phụ thuộc DBA/DevOps/BA; không nói “tự build tất cả” nếu không đúng.

---

## E2. SQL / Oracle: 15 câu quan trọng

### Q8. Làm sao tìm một SQL chạy chậm?

“Lấy baseline và execution plan; xem row estimate vs actual, scan, join, sort, temp spill/I/O; kiểm thống kê/index/cardinality/filters; thử query rewrite và benchmark; cuối cùng validate logic dữ liệu.”

### Q9. Vì sao câu SQL có index vẫn chậm?

“Index có thể đọc nhiều rowid, bảng quá lớn, predicate selectivity thấp, stale stats, join nặng, sort hoặc I/O; phải xem toàn plan chứ không chỉ một operator.”

### Q10. Hash Join và Nested Loops khác nhau?

“Nested Loops lặp phía ngoài và tìm dòng liên quan ở phía trong, tốt nếu outer nhỏ/inner indexed; Hash Join xây hash phía phù hợp để ghép nhiều dòng, tốt trong nhiều workload lớn nhưng dùng memory.”

### Q11. ROW_NUMBER khác RANK và DENSE_RANK?

`ROW_NUMBER`: 1,2,3 luôn duy nhất. `RANK`: 1,1,3. `DENSE_RANK`: 1,1,2. Chọn dựa yêu cầu đồng hạng.

### Q12. JOIN giữa bảng CUSTOMER và TRANSACTION tại sao làm tăng row count?

Quan hệ một khách hàng nhiều giao dịch. Phải xác định mục tiêu: số khách hàng riêng biệt, số giao dịch hay doanh số, chọn grain cho truy vấn.

### Q13. INNER JOIN có thể làm mất dữ liệu?

Có, nếu khóa không match hoặc NULL. Khi đối soát missing records, cân nhắc anti-join và mapping.

### Q14. Khi nào FULL OUTER JOIN hữu ích?

Đối soát hai tập dữ liệu để tìm key chỉ có ở nguồn, chỉ có ở đích hoặc ở cả hai; cần xử lý duplicate keys trước khi so sánh.

### Q15. SQL nào tìm duplicate?

`GROUP BY business_key HAVING COUNT(*) > 1`, hoặc `ROW_NUMBER() OVER(PARTITION BY business_key ORDER BY updated_at DESC, tie_breaker)` để giữ phiên bản mới nhất.

### Q16. Tại sao COUNT khớp nhưng báo cáo vẫn sai?

Có thể khác key/amount, hoán đổi bản ghi, sai rounding, sai nguồn/kỳ, reversal, source changed between reads. So thêm hash/key-level and business metrics.

### Q17. Tại sao không nên dùng FLOAT cho tiền?

Floating-point nhị phân có thể tạo sai số làm tròn; dùng exact DECIMAL/NUMBER khi yêu cầu tài chính phù hợp.

### Q18. Tại sao WHERE TRUNC(date) có thể làm query chậm?

Expression trên cột có thể khó tận dụng index bình thường/partition pruning; thử range predicate hoặc function-based index và kiểm plan.

### Q19. Bitmap index vs B-tree?

Bitmap hợp với một số phân tích ít cập nhật, cardinality thấp; B-tree phổ biến hơn cho tra cứu OLTP/range. Không áp dụng máy móc.

### Q20. CTE dùng để optimize được không?

Không tự động; làm logic rõ hơn, đôi lúc optimizer inline/materialize theo DB và plan. Đo thực tế.

### Q21. Temp Table có chắc cải thiện?

Không. Có thêm chi phí ghi/đọc; chỉ hữu ích nếu giảm tính lại, giúp optimizer hoặc tái sử dụng intermediate.

### Q22. Ở KLB bạn tối ưu 250 báo cáo?

Không. Khoảng 250 là phạm vi chung; nêu phần bạn được giao và vai trò hỗ trợ một cách chính xác.

---

## E3. Spark: 12 câu quan trọng

### Q23. Spark SQL và PySpark là một không?

Khác khái niệm nhưng nằm trong Spark. Spark SQL là module SQL; PySpark là API Python. PySpark có thể gọi Spark SQL và dùng DataFrame API.

### Q24. Driver vs Executor?

Driver điều phối, Executors thực thi task và giữ data/shuffle/cache.

### Q25. Job/Stage/Task?

Action kích hoạt job; execution được chia stages theo ranh giới dependency/shuffle; stage gồm tasks theo partitions.

### Q26. Shuffle là gì và tại sao đắt?

Redistribution data giữa partitions/executors, tạo network/disk/memory overhead; thường phát sinh ở groupBy/join/distinct.

### Q27. Lazy Evaluation giúp gì?

Spark có thể tối ưu chuỗi transformations thành logical/physical plan trước khi action.

### Q28. Broadcast Join dùng khi nào?

Phía nhỏ có thể broadcast đến executors, tránh shuffle lớn; kiểm bộ nhớ và kích thước thực.

### Q29. Data Skew xử lý thế nào?

Xem Spark UI và distribution, identify hot keys; AQE/skew join, salting, broadcast, xử lý special keys hoặc thiết kế lại aggregation.

### Q30. Executor OOM vs Driver OOM?

Driver OOM do collect/metadata; Executor OOM do big partitions/hash/sort/cache/broadcast... Cần xác định log/state cụ thể.

### Q31. Repartition vs Coalesce?

Repartition thường shuffle và phân phối lại, coalesce thường giảm partitions tránh full shuffle nhưng có thể mất cân bằng.

### Q32. Tại sao Spark SQL dùng Parquet?

Columnar scan/column pruning, nén, metadata và hiệu quả query analytic.

### Q33. Spark query thành công nhưng mất bản ghi?

Mapping/filter, join type, NULL join keys, dedup logic, write mode, incremental window, source delay; đối soát theo keys.

### Q34. AQE là gì?

Sử dụng runtime statistics để điều chỉnh plan như số shuffle partitions, strategy JOIN và một số skew cases. Không phải phép tối ưu thần kỳ.

---

## E4. Airflow, ETL, dbt: 14 câu

### Q35. Airflow khác Spark?

Orchestration vs compute engine.

### Q36. DAG là gì?

Đồ thị task có hướng, không chu trình, thể hiện dependencies.

### Q37. Task lỗi ở giữa DAG, xử lý?

Log, nguyên nhân, partial writes, idempotency, retry đúng phạm vi, reconciliation.

### Q38. Idempotency là gì?

Same input/run re-execution không tạo hậu quả sai/trùng; MERGE, partition overwrite an toàn, batch control.

### Q39. Backfill có thể làm sai dữ liệu không?

Có nếu dùng NOW() thay business date, data late/change, duplicate writes, hoặc không rollback/reconcile.

### Q40. Watermark là gì?

Mốc tiến độ theo timestamp/sequence/batch; commit sau khi xử lý và validate, có biện pháp cho tie/late.

### Q41. Retry mọi lỗi được không?

Không. Lỗi tạm thời có thể retry; lỗi schema/business deterministic cần fix.

### Q42. Airflow XCom dùng để lưu DataFrame lớn?

Không nên, dùng object storage/DB và truyền path/metadata.

### Q43. dbt là ETL engine toàn diện không?

Chủ yếu transformation; ingestion/orchestration do công cụ khác tùy hệ thống.

### Q44. dbt View vs Table?

View thường tính query khi đọc; Table precompute nhưng phải refresh.

### Q45. dbt incremental có rủi ro nào?

Unique key sai, late data, deletes, schema changes và thiếu backfill.

### Q46. Data contract là gì?

Thỏa thuận schema, business meaning, freshness, nullable, key và khả năng tương thích giữa producer–consumer.

### Q47. CDC có phải mỗi ngày lấy bản ghi mới không?

CDC thường phát hiện thay đổi INSERT/UPDATE/DELETE; incremental timestamp chỉ là một lựa chọn, có thể không bắt hard delete.

### Q48. Nếu ETL Success nhưng business báo sai số?

Tạm coi quality incident; đi từ source snapshot, mapping, joins, target, currency, business date, validate test.

---

## E5. Kafka, Lakehouse, Cloud: 12 câu

### Q49. Kafka Topic và Partition?

Topic logical stream, partitions tạo parallelism và thứ tự theo partition.

### Q50. Kafka Offset?

Record position trong partition, consumer commit progress.

### Q51. Kafka Consumer Lag lớn?

Consumer không theo kịp producer hoặc downstream blocking; xem throughput, consumer errors, DB sink, partitions.

### Q52. At-least-once nghĩa gì?

Không muốn mất event nhưng có thể duplicate; idempotent sink.

### Q53. Trino vs Spark?

Distributed SQL query engine vs general distributed data processing engine.

### Q54. MinIO vs PostgreSQL?

Object storage vs RDBMS.

### Q55. Iceberg khác Parquet?

Iceberg là table format/metadata/snapshot management; Parquet là physical columnar file format.

### Q56. Data Lake khác DWH?

Lake lưu file đa dạng; DWH tổ chức dữ liệu theo nhu cầu phân tích/SQL và chất lượng mô hình; lakehouse kết hợp đặc điểm của hai.

### Q57. Kubernetes Pod và Deployment?

Pod là workload unit; Deployment quản lý replicas và rollout theo desired state.

### Q58. Docker Container có phải VM?

Không; container cách ly process trên kernel host, VM có guest OS riêng.

### Q59. OpenShift là gì?

Kubernetes-based application platform với layer quản trị/bảo mật/build/deployment bổ sung.

### Q60. CMC Cloud project có phải làm AWS/K8s managed không?

Không, từ mô tả là hạ tầng Cloud VM cấp để dựng PoC bằng Docker; đừng nâng cấp thành managed cloud skills chưa làm.

---

## E6. Banking, Data Modeling và tình huống: 16 câu

### Q61. Grain là gì? Vì sao phải xác định?

Đơn vị một hàng fact. Nếu grain sai, JOIN/aggregate có thể double count.

### Q62. Fact và Dimension?

Fact chứa sự kiện/measure, dimension chứa ngữ cảnh mô tả.

### Q63. SCD2 giải quyết gì?

Lưu các phiên bản thay đổi thuộc tính dimension theo thời gian để phân tích as-was.

### Q64. ODS vs DWH?

ODS cho tích hợp/operational data, DWH cho phân tích/lịch sử; phụ thuộc triển khai cụ thể.

### Q65. Business Date khác Posting Date?

Business Date là ngày theo lịch nghiệp vụ; Posting Date là ngày hạch toán, không mặc định trùng transaction timestamp.

### Q66. Khi giao dịch bị reverse, có xóa hẳn giao dịch cũ?

Không tự quyết định. Cần business rule, audit và nguồn transaction lifecycle; có thể giữ reversal entry/status.

### Q67. Tại sao không lấy trực tiếp dữ liệu từ Core Banking cho BI nặng?

Tránh ảnh hưởng OLTP, đồng thời cần tích hợp, chuẩn hóa, historization và quản trị dữ liệu.

### Q68. Một CIF có nhiều account, JOIN thế nào để không nhân số dư?

Xác định grain: daily account balance vs customer segment, customer–account relation, ownership weighting, effective dates; không cộng snapshot theo giao dịch.

### Q69. Khách hàng thay đổi nhóm VIP, muốn báo cáo lịch sử?

SCD2 hoặc snapshot theo business date tùy yêu cầu; không gắn VIP hiện tại vào tất cả giao dịch quá khứ nếu cần as-was.

### Q70. Dữ liệu chốt EOD về trễ 1 ngày?

Xử lý watermark/lookback/backfill và reconciliation; chính sách restatement theo nghiệp vụ.

### Q71. Báo cáo số dư thấp hơn nguồn dù giao dịch khớp?

Xem business cut-off, account coverage, snapshots, conversion, source balance, timezone, internal transfers, reversal và missing accounts.

### Q72. Làm sao xử lý số tài khoản/CCCD trong log?

Tránh ghi PII thật, mask/tokenize và áp dụng quyền truy cập/audit.

### Q73. Nếu BA không thể xác định định nghĩa doanh số?

Nêu các ví dụ phản chứng (refund, reversal, currency, posting dates) để họ chọn rule, ghi lại specification.

### Q74. Dashboard sai số nhưng task green?

Success status không đủ; kiểm Data Quality và đối soát từ nguồn theo từng layer.

### Q75. SQL tuning nhanh hơn nhưng semantics khác?

Không chấp nhận; phải rollback/chỉnh lại và đảm bảo nghiệp vụ trước performance.

### Q76. VPBank cần pipeline realtime hay batch, chọn sao?

Theo SLA/latency/business need, chi phí, consistency, source capability; không chạy theo buzzword.

---

## E7. Một số câu hỏi tiếng Anh dễ gặp

**“Can you explain your most recent ETL project?”**

> “My recent work focuses on Spark SQL ETL development based on predefined source-to-target mappings. I handle transformations, data validation and troubleshooting within Airflow-orchestrated workflows. I can explain one specific job and its data quality checks in detail.”

**“How do you troubleshoot a slow SQL query?”**

> “I start with the baseline and execution plan, identify costly scans, joins and sorts, check cardinality and statistics, then test query rewrites or access-path improvements. Finally, I compare both performance and result correctness.”

**“Have you worked with Kafka or Kubernetes in production?”**

> “I understand the fundamentals, but I would distinguish that knowledge from direct production ownership. My main hands-on experience has been with SQL-based ETL, Airflow and related data platforms.”

Sửa nội dung cuối theo kinh nghiệm thật, tránh nói quá mức.

---

## E8. 18 câu tình huống đánh giá năng lực ở level Junior/Middle

| # | Tình huống | Trục chẩn đoán và xử lý |
|---|---|---|
| 1 | DAG fail ở bước load | Log, connection, partial commit, idempotent retry |
| 2 | Task Success nhưng target thiếu 2% | Mapping, JOIN, filter, watermark, rejects, reconciliation |
| 3 | Job Spark 20 phút lên 3 giờ | Spark UI, input growth, skew, shuffle, resources, query plan |
| 4 | Spark executor OOM | Hot key, partition size, cache, broadcast, spill, executor memory |
| 5 | Oracle query full scan | Selectivity, index, partition, stats, acceptable cost |
| 6 | Index mới không giúp | Logical/physical plan, cardinality, table lookup overhead |
| 7 | Đầu nguồn schema đổi | Schema contract, compatibility, casts, mapping, downstream tests |
| 8 | Dữ liệu ngày trước về muộn | Lookback, backfill, business cutoff, idempotency |
| 9 | Bảng fact tăng gấp 10 | Partition, incremental, preaggregation, storage, capacity |
| 10 | Kafka lag lớn | Consumer performance, sink, partitions, rebalance, errors |
| 11 | Dữ liệu duplicate sau retry | Unique key, upsert, batch_id, transaction semantics |
| 12 | Hai DWH tổng tiền lệch | Currency, rounding, time periods, status, join grain |
| 13 | Analyst muốn report realtime | Confirm actual latency need and trade-off with streaming |
| 14 | View ClickHouse nặng | Sorting key, precompute/dbt table, partition, query design |
| 15 | dbt incremental miss changes | Watermark, late data, unique key, delete handling |
| 16 | ODS load đụng nguồn OLTP | Source load, scheduling, CDC/replica, query optimization |
| 17 | K8s Pod CrashLoopBackOff | Events, logs, config, probes, permission, resources |
| 18 | Khách hàng hỏi kết quả tuning bằng số | Chỉ cung cấp benchmark đã đo; không dựng số liệu |

---
# F. BÀI SQL, SPARK VÀ THIẾT KẾ PIPELINE TỰ LUYỆN

> Các bài dưới đây dùng dữ liệu **giả lập**, không phải dữ liệu khách hàng ngân hàng. Mục đích là bạn đọc yêu cầu, tự nói cách giải, sau đó kiểm đáp án. SQL chủ yếu gần PostgreSQL/ANSI; nếu người phỏng vấn dùng Oracle hoặc Spark SQL, cần chuyển cú pháp date, upsert, limit/DDL cho đúng dialect.

## F1. Dataset mẫu

Giả sử ba bảng:

```sql
CREATE TABLE customers (
  customer_id VARCHAR(20) PRIMARY KEY,
  customer_name VARCHAR(100),
  segment VARCHAR(20)
);

CREATE TABLE accounts (
  account_id VARCHAR(20) PRIMARY KEY,
  customer_id VARCHAR(20) NOT NULL,
  branch_id VARCHAR(20) NOT NULL
);

CREATE TABLE transactions (
  transaction_id VARCHAR(20),
  account_id VARCHAR(20),
  posting_date DATE,
  amount NUMERIC(18,2),
  status VARCHAR(20),
  updated_at TIMESTAMP
);
```

Lưu ý `transactions` chưa có PK trong ví dụ để cố ý kiểm tra duplicate; trong production cần xác định nghiệp vụ có cho nhiều dòng/một transaction ID hay không.

### Bài 1. Tính tổng giao dịch theo ngày/chi nhánh

**Yêu cầu:** Chỉ lấy status `SUCCESS`, group theo ngày và branch.

```sql
SELECT t.posting_date, a.branch_id,
       COUNT(*) txn_count,
       SUM(t.amount) total_amount
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
WHERE t.status = 'SUCCESS'
GROUP BY t.posting_date, a.branch_id
ORDER BY t.posting_date, a.branch_id;
```

**Điểm dễ sai:** Nếu account–branch quan hệ theo lịch sử thì JOIN cần effective-date; nếu tài khoản có nhiều owner thì JOIN owner mapping có thể nhân dòng.

### Bài 2. Lấy giao dịch mới nhất của mỗi tài khoản

```sql
WITH x AS (
 SELECT t.*,
        ROW_NUMBER() OVER (
           PARTITION BY account_id
           ORDER BY posting_date DESC, updated_at DESC, transaction_id DESC
        ) AS rn
 FROM transactions t
)
SELECT * FROM x WHERE rn = 1;
```

**Bẫy:** Nếu chỉ có posting_date mà nhiều giao dịch cùng ngày, phải có tie-breaker phù hợp, không giả định `transaction_id` là thứ tự thời gian nếu không có quy định.

### Bài 3. Tìm customer chưa có account

```sql
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM accounts a
  WHERE a.customer_id = c.customer_id
);
```

### Bài 4. Những account có giao dịch duplicate theo transaction_id

```sql
SELECT account_id, transaction_id, COUNT(*) cnt
FROM transactions
GROUP BY account_id, transaction_id
HAVING COUNT(*) > 1;
```

### Bài 5. Dedup giữ record updated_at mới nhất

```sql
WITH d AS (
 SELECT t.*,
        ROW_NUMBER() OVER (
          PARTITION BY transaction_id
          ORDER BY updated_at DESC, account_id
        ) rn
 FROM transactions t
)
SELECT transaction_id, account_id, posting_date,
       amount, status, updated_at
FROM d
WHERE rn=1;
```

Bản ghi có cùng `updated_at` cần tie-breaker đáng tin cậy, ví dụ `source_sequence`; trong ví dụ `account_id` chỉ minh họa cách sắp xếp ổn định, không bảo đảm “phiên bản đúng” theo nghiệp vụ.

### Bài 6. Tìm chênh lệch tổng tiền source-target

```sql
WITH s AS (
 SELECT posting_date, SUM(amount) amt, COUNT(*) cnt
 FROM source_transactions
 GROUP BY posting_date
), t AS (
 SELECT posting_date, SUM(amount) amt, COUNT(*) cnt
 FROM target_transactions
 GROUP BY posting_date
)
SELECT COALESCE(s.posting_date,t.posting_date) AS dt,
       s.amt AS src_amt, t.amt AS tgt_amt,
       s.cnt AS src_cnt, t.cnt AS tgt_cnt
FROM s FULL OUTER JOIN t ON s.posting_date=t.posting_date
WHERE s.amt IS DISTINCT FROM t.amt
   OR s.cnt IS DISTINCT FROM t.cnt;
```

`IS DISTINCT FROM` là cú pháp có ở PostgreSQL và một số hệ khác; Oracle/Spark hỗ trợ có thể khác tùy version. Cần định nghĩa NULL vs missing source day đúng.

### Bài 7. Tính cumulative sum theo tài khoản

```sql
SELECT account_id, transaction_id, posting_date, amount,
       SUM(amount) OVER (
         PARTITION BY account_id
         ORDER BY posting_date, transaction_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_amount
FROM transactions;
```

Bài này **không tự động là số dư thực tế**, vì thiếu opening balance, debit/credit signs và reversals.

### Bài 8. Top 3 khách hàng có tổng giao dịch lớn nhất mỗi chi nhánh

```sql
WITH totals AS (
 SELECT a.branch_id, a.customer_id, SUM(t.amount) amt
 FROM transactions t
 JOIN accounts a ON t.account_id=a.account_id
 WHERE t.status='SUCCESS'
 GROUP BY a.branch_id, a.customer_id
), ranked AS (
 SELECT totals.*,
        DENSE_RANK() OVER(PARTITION BY branch_id ORDER BY amt DESC) rnk
 FROM totals
)
SELECT * FROM ranked WHERE rnk <= 3;
```

**Bẫy:** DENSE_RANK có thể trả nhiều hơn 3 khách khi đồng hạng; muốn chính xác 3 dòng, dùng ROW_NUMBER với tiêu chí phụ.

---

## F2. Một case ETL end-to-end: CSV → MinIO → PostgreSQL → dbt → Dashboard

**[Bài thiết kế giả định]** Có một file CSV mỗi ngày chứa các giao dịch `transaction_id`, `account_id`, `posting_time`, `amount`, `status`.

### Thiết kế mục tiêu

```text
CSV file
  |
  +-- Save immutable source file + metadata to MinIO/raw/business_date=...
  |
Python parsing/validation
  |
PostgreSQL staging_transactions (with batch_id, source_file)
  |
dbt stg model (cast, standardize, dedup)
  |
dbt fact_transaction / daily_branch_summary
  |
Dashboard/BI

Airflow triggers, checks, retries; metrics/logs; audit metadata
```

### Metadata nên lưu

`batch_id`, `source_file`, `source_system`, `ingested_at`, `business_date`, `file_hash`, `row_count`, `schema_version`, `processing_status`. Không phải dự án nào cũng buộc có mọi cột, nhưng chúng hữu ích để replay/audit.

### Quality Gates

1. Đọc file thành công và schema đúng.
2. `transaction_id` không NULL nếu rule yêu cầu.
3. Currency/decimal/date parsing hợp lệ.
4. Xác định duplicate policy.
5. Row counts/rejects không vượt ngưỡng.
6. Post-load reconcile count và sum.
7. Publish sang Gold chỉ khi critical checks đạt.

### Idempotency

Khóa batch/file giúp tránh nạp trùng cả file. Business key/record version giúp MERGE đúng từng transaction. Nếu file cũ được gửi lại với nội dung mới, cần version/policy, không chỉ chặn file trùng tên.

### Nếu job fail sau staging load

- Xác định batch_id đã hoàn tất bước nào.
- Nếu stage insert partial, rollback hoặc replace batch theo transaction.
- Retry từ bước cần thiết.
- Không tăng watermark khi chưa publish và validate.
- Kiểm chứng dashboard không đọc partial data.

---

## F3. Bài tập Spark SQL/PySpark tương đương

**Yêu cầu:** Chỉ lấy giao dịch hợp lệ, tính total theo ngày/chi nhánh.

Spark SQL:

```sql
SELECT to_date(posting_time) business_date,
       branch_id,
       COUNT(*) txn_count,
       SUM(amount) total_amount
FROM transactions
WHERE status = 'SUCCESS'
GROUP BY to_date(posting_time), branch_id;
```

PySpark:

```python
from pyspark.sql import functions as F

result = (
    transactions
      .filter(F.col('status') == 'SUCCESS')
      .withColumn('business_date', F.to_date('posting_time'))
      .groupBy('business_date','branch_id')
      .agg(F.count('*').alias('txn_count'),
           F.sum('amount').alias('total_amount'))
)
```

**Điều phải giải thích:** `groupBy` có thể shuffle; `to_date` tùy timezone/source type; date dimension có thể cần business calendar, không phải cứ calendar day là business date.

### Bài chẩn đoán Spark

**[Tình huống]** Dữ liệu nguồn tăng từ 10GB lên 200GB, job chậm, tasks cuối chạy lâu.

- Kiểm tra Spark UI stages/task skew.
- Kiểm tra partition count, skewed keys, input files.
- `explain` plan, join/shuffle/spill.
- Filter/project sớm và cải thiện strategy JOIN khi đúng.
- Thiết kế incremental/load theo partition.
- Benchmark và kiểm tra correctness.

Không có một “tham số kỳ diệu” phù hợp mọi ứng dụng.

---

## F4. Bài dbt model và tests

**Staging model** `models/staging/stg_transactions.sql`:

```sql
SELECT
  CAST(transaction_id AS VARCHAR) AS transaction_id,
  CAST(account_id AS VARCHAR) AS account_id,
  CAST(amount AS NUMERIC(18,2)) AS amount,
  UPPER(TRIM(status)) AS status,
  posting_date
FROM {{ source('banking_raw', 'transactions') }}
```

**Model report**:

```sql
{{ config(materialized='table') }}

SELECT posting_date,
       COUNT(*) AS transaction_count,
       SUM(amount) AS total_amount
FROM {{ ref('stg_transactions') }}
WHERE status = 'SUCCESS'
GROUP BY posting_date
```

**Test YAML:**

```yaml
version: 2
models:
  - name: stg_transactions
    columns:
      - name: transaction_id
        data_tests:
          - not_null
```

**Câu hỏi nên tự trả lời:** Nếu `transaction_id` có duplicate theo nghiệp vụ thì nên làm unique test trực tiếp không? Không; phải xác định grain/record version. Nếu full rebuild quá chậm, nên cân nhắc incremental model nhưng phải thiết kế unique key, late updates và backfill.

---

## F5. Bài design banking fact/dimension

**Đề:** Báo cáo tổng phát sinh giao dịch theo chi nhánh, sản phẩm và phân khúc khách hàng tại ngày giao dịch.

### Mô hình giả định

- `fact_transaction(txn_sk, business_txn_id, date_key, branch_key, product_key, customer_segment_key, amount, status, ...)`.
- `dim_date(date_key, calendar_date, month, year, business_calendar_flag...)`.
- `dim_branch(branch_key, branch_id, region, valid_from, valid_to...)`.
- `dim_product(product_key, product_id, category, ...)`.
- `dim_customer_segment(segment_key, customer_id, segment, valid_from, valid_to...)` hoặc customer dimension theo thiết kế.

**Giải thích:** Định nghĩa fact grain; chọn `customer_segment_key` đúng version tại ngày giao dịch nếu cần SCD2, tránh join chỉ bằng customer ID hiện tại. Xác định business_date, reversal, currency rõ trước khi tính amount.

**Câu hỏi phản biện:** Nếu yêu cầu lại muốn phân tích tất cả giao dịch theo **phân khúc hiện tại**, mô hình query/serving phải đáp ứng “as-is” chứ không cứng nhắc dùng SCD2 as-was.

---

## F6. Bài tổng hợp Interview: 10 tình huống trả lời bằng phương pháp

**Case 1: Oracle query chạy 15 phút, cần xuống 3 phút.**

Tìm baseline, execution plan actual, rows/IO, predicate, JOIN, cardinality, index, partitions, summary table; benchmark mọi thay đổi, validate tương đương. Không cam kết 3 phút khi chưa đo.

**Case 2: Spark join bị skew.**

Tìm hot keys, thử broadcast hợp lý, AQE skew optimization, salting/handling special keys, partition strategy; kiểm correctness.

**Case 3: DAG retry làm dữ liệu trùng.**

MERGE/upsert hoặc transaction/partition replace an toàn; checkpoint commit sau validation.

**Case 4: DWH thiếu một ngày dữ liệu nhưng source giờ đã có.**

Backfill theo business_date, lookback, kiểm downstream dependencies/reports, kiểm SLA.

**Case 5: BigQuery procedure chuyển sang ClickHouse không chạy.**

Kiểm SQL dialect, function differences, data types, procedural logic, tách thành dbt transformations/jobs theo dependency, test từng bước.

**Case 6: Power BI refresh fail.**

Kiểm Gateway, DB/host/port, credentials, dataset mapping, refresh history, source locks/timeouts.

**Case 7: K8s Pod restart liên tục.**

Describe events, logs current/previous, exit status, configuration, memory, dependency/health probes.

**Case 8: Kafka replay 2 ngày event.**

Thiết kế consumer replay window theo offset/retention, idempotent sink, control duplicates, reconciliation.

**Case 9: Business yêu cầu KPI nhưng không định nghĩa status.**

Hỏi rule, lập examples và thống nhất nghiệm thu trước SQL.

**Case 10: Vendor khác cùng onsite bank, tại sao lương khác?**

Đây là câu HR, không phải kỹ thuật. Hợp đồng, scope, mức độ trách nhiệm, ngân sách vendor và thời điểm tuyển có thể khác; không suy diễn mức lương của người khác hoặc khai thông tin bảo mật.

---

# G. THUẬT NGỮ, BẪY PHỎNG VẤN VÀ NGUỒN THAM KHẢO

## G1. Thuật ngữ gói gọn để nhớ

| Viết tắt | Diễn giải |
|---|---|
| DE | Data Engineer |
| ETL | Extract – Transform – Load |
| ELT | Extract – Load – Transform |
| CDC | Change Data Capture |
| DWH | Data Warehouse |
| ODS | Operational Data Store |
| OLTP | Online Transaction Processing |
| OLAP | Online Analytical Processing |
| SCD | Slowly Changing Dimension |
| SLA | Service Level Agreement |
| SLO | Service Level Objective |
| DQ | Data Quality |
| SIT | System Integration Testing |
| UAT | User Acceptance Testing |
| OOM | Out of Memory |
| AQE | Adaptive Query Execution |
| EOD | End of Day |
| CIF | Customer Information File/Customer Identifier theo ngữ cảnh ngân hàng |
| PII | Personally Identifiable Information |
| RPO/RTO | Recovery Point/Time Objective |
| PoC | Proof of Concept |
| RBAC | Role-Based Access Control |
| IAM | Identity and Access Management |
| S3A | Hadoop S3 filesystem connector |
| JDBC | Java Database Connectivity |
| DAG | Directed Acyclic Graph |
| XCom | Airflow cross-communication mechanism |

## G2. Những phát biểu dễ bị phản biện

| Nói thiếu chính xác | Nên hiểu và nói đúng |
|---|---|
| “Spark SQL là PySpark.” | Spark SQL module; PySpark là Python API, có thể dùng Spark SQL. |
| “Airflow xử lý Big Data.” | Airflow orchestrates; Spark/SQL/DB là execution engines. |
| “Có index là query sẽ nhanh.” | Tùy selectivity, plan, I/O, DML cost. |
| “Full Table Scan luôn xấu.” | Có lúc quét phần lớn bảng thì hợp lý. |
| “Số row bằng nhau là đối soát đúng.” | Cần key/value/business aggregates. |
| “Chuyển view thành table là tự động nhanh và đúng.” | Có cost refresh/freshness và phải test logic. |
| “ClickHouse index giống Oracle.” | MergeTree sorting/sparse primary index khác B-tree. |
| “K8s Basic = biết admin cluster.” | Kiến thức Pod/Service khác kinh nghiệm vận hành production. |
| “Tổng dự án 250 báo cáo = mình tối ưu 250.” | 250 là phạm vi dự án, phân biệt số được giao. |
| “Hai vendor vào VPBank là chung một team.” | Chưa chắc; xác nhận cụ thể team và scope. |
| “Từng dùng MinIO nên biết AWS Glue/EMR.” | Không; khác dịch vụ và vai trò. |
| “Điều kiện WHERE cột ngày là đủ cho EOD.” | Phải chọn đúng business/transaction/posting date. |
| “Cứ retry task fail.” | Kiểm partial effects và idempotency trước. |
| “Kafka đảm bảo đúng một lần ở mọi sink.” | Cần semantics/transaction/idempotent integration cụ thể. |
| “Giá trị float tốt như decimal cho tiền.” | Tùy business; thường dùng exact decimal. |

## G3. Cách nói khi quên chi tiết thật của dự án

Một câu trả lời chuyên nghiệp có thể là:

> “Phần này em không nhớ chính xác tên bảng/cấu hình từ dự án do phạm vi công việc trước đây, nên em không muốn đưa thông số sai. Em nhớ nguyên lý và cách em xử lý là ... Nếu triển khai lại, em sẽ kiểm tra plan/log/mapping theo các bước ...”

Nếu không nhớ/không làm thì **không tạo SQL giả rồi bảo là code từ production**. Có thể đưa **ví dụ giả định**, nhưng nói rõ là ví dụ.

## G4. Nguồn tham khảo kỹ thuật chính thức để kiểm tra chi tiết theo version

Những nguồn dưới đây dùng để xác minh kiến thức mở rộng. Nội dung hai JD và chi tiết CV là từ tài liệu/trao đổi của người dùng, không phải từ các tài liệu công nghệ này.

- [Apache Spark – SQL Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning/): join hints, partition, Adaptive Query Execution, skew.
- [Apache Spark – PySpark Documentation](https://spark.apache.org/docs/latest/api/python/): DataFrame API và Spark SQL.
- [Apache Airflow – Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html): retries, idempotent tasks, thiết kế workflow.
- [dbt – Incremental Models](https://docs.getdbt.com/docs/build/incremental-models): incremental, unique_key, materializations.
- [ClickHouse – MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree): ORDER BY, partition, sorting keys.
- [Apache Kafka – Documentation](https://kafka.apache.org/documentation/): topics, offsets, consumers, semantics.
- [Apache Trino – Documentation](https://trino.io/docs/current/): query engine và connectors.
- [Apache Iceberg – Documentation](https://iceberg.apache.org/docs/latest/): snapshots, table format, partition/schema evolution.
- [Kubernetes – Concepts](https://kubernetes.io/docs/concepts/): Pods, Deployments, Services, ConfigMaps, Secrets.
- [Oracle Database – DBMS_XPLAN](https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/DBMS_XPLAN.html): execution plan và runtime statistics.

## G5. Trước khi trả lời từng câu hỏi, kiểm tra 5 điều

1. **Đề bài hỏi cái gì?** Lý thuyết, code, architecture, incident hay kinh nghiệm cá nhân?
2. **Giả định nào cần làm rõ?** Business date, volume, source, unique key, SLA, version engine.
3. **Giải pháp có đúng logic dữ liệu không?** Không chạy theo performance mà bỏ correctness.
4. **Trade-off là gì?** Cost, memory, latency, complexity, operational impact.
5. **Mình thực sự từng làm chưa?** Phân biệt trực tiếp làm, hỗ trợ, chỉ hiểu, ví dụ minh họa.

---

**KẾT THÚC TÀI LIỆU.** Trọng tâm của hai vị trí onsite VPBank là **SQL/Oracle + Banking Data + ETL/ELT + Spark + Airflow + Data Modeling + Data Quality + Troubleshooting**. Khi nắm nguyên lý, nêu được ca triển khai thật và có phương pháp phân tích sự cố, bạn sẽ trả lời tốt hơn nhiều so với học thuộc tên công nghệ.
