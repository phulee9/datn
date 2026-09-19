# LUỒNG INGEST DỮ LIỆU — SEED DUNNHUMBY + OCR LIVE

> Mục tiêu: có sẵn dữ liệu trong PostgreSQL để Forecast/Combo/Text2SQL chạy ngay,
> đồng thời chứng minh luồng ảnh hóa đơn → Gemini → DB vẫn hoạt động.

## 1. Kiến trúc 2 nhánh

```mermaid
flowchart TB
    subgraph Seed["Nhánh SEED — chạy 1 lần"]
        A["Dunnhumby (Kaggle)\ntransaction_data.csv\nproduct.csv\nhh_demographic.csv"] --> B["scripts/seed_dunnhumby.py\nETL"]
        B --> C["PostgreSQL\nstores / products\nreceipts / receipt_items"]
    end

    subgraph Live["Nhánh LIVE — chạy mỗi khi có ảnh mới"]
        D["Ảnh hóa đơn\n(upload hoặc render từ basket)"] --> E["POST /api/receipts/upload"]
        E --> F["ingestion/service.py\nextract_receipt() → Gemini Vision"]
        F --> G["ingestion/validator.py\nconfidence_score"]
        G -->|>=0.85| H["Ghi receipts + receipt_items\nstatus=confirmed"]
        G -->|<0.85| I["status=needs_review\nchờ PATCH /receipts/{id}"]
        H --> C
        I --> C
    end

    C --> J["View daily_sales\nGROUP BY date, store, product"]
    J --> K["Forecast / Combo / SQL Agent"]
```

## 2. Vì sao tách 2 nhánh

| Nhánh | Vai trò | Có tốn Gemini không |
|---|---|---|
| Seed | Nạp lịch sử hàng trăm nghìn giao dịch để có dữ liệu học | Không |
| Live | Xử lý hóa đơn mới phát sinh, chứng minh OCR chạy được | Có, nhưng chỉ vài ảnh demo |

Ngoài đời cũng vậy: POS/ERP export → import 1 lần, ảnh hóa đơn chỉ xử lý khi phát sinh mới.

## 3. Mapping Dunnhumby → Schema đồ án

### 3.1. product.csv → products

```
PRODUCT_ID  → sku (giữ nguyên PRODUCT_ID dạng string, ví dụ "823451")
COMMODITY_DESC → category
BRAND + CURR_SIZE_OF_PRODUCT → display_name
DEPARTMENT → ghi chú thêm
```

### 3.2. transaction_data.csv → receipts + receipt_items

Dunnhumby không có bảng receipts sẵn, phải gom theo BASKET_ID:

```
BASKET_ID + STORE_ID + DAY (+ household_key) → 1 receipts row
  receipt_date = BASE_DATE + (DAY - 1)   // BASE_DATE tự chọn, ví dụ 2024-01-01
  store_id     = STORE_ID
  total_amount = SUM(SALES_VALUE) trong basket
  status       = confirmed
  raw_json     = JSON dump các dòng transaction trong basket

Mỗi dòng transaction trong basket → 1 receipt_items row
  product_id     = lookup products.sku = PRODUCT_ID
  raw_item_name  = COMMODITY_DESC / SUB_COMMODITY_DESC
  quantity       = QUANTITY
  unit_price     = SALES_VALUE / QUANTITY
  line_total     = SALES_VALUE
```

### 3.3. Giới hạn để không nổ DB

Dunnhumby có ~2.5k household × ~2 năm = hàng triệu dòng transaction, hàng chục nghìn PRODUCT_ID.

Khuyên seed có chọn lọc cho đồ án:

```
- Chọn top N PRODUCT_ID bán chạy nhất (ví dụ 100-200 SKU)
- Hoặc top SKU theo DEPARTMENT quan tâm (GROCERY, DRUG v.v.)
- Lọc STORE_ID có nhiều basket nhất (ví dụ 10-20 store)
```

Đủ để benchmark Forecast (cần chuỗi đủ dài) và Combo (cần basket đa dạng).

## 4. Thay thế ảnh hóa đơn thật khi demo OCR

Dunnhumby không có ảnh scan, nên render ảnh từ basket thật:

```
Chọn BASKET_ID thật (ví dụ 123456)
→ join product.csv lấy tên hàng
→ render ảnh hóa đơn (PIL / reportlab)
→ gửi Gemini OCR
→ JSON phải map lại được PRODUCT_ID đã biết
```

Ảnh là synthetic nhưng line item là transaction thật → demo trung thực nếu nói rõ.

Không được nói CORU và Dunnhumby nối nhau ở cấp từng hóa đơn — chúng là 2 dataset độc lập:
- CORU: test OCR kỹ thuật
- Dunnhumby: seed lịch sử cho Forecast/Combo

## 5. Các bước chạy

### 5.1. Chuẩn bị

```bash
kaggle auth login   # hoặc đặt KAGGLE_API_TOKEN
pip install kaggle pandas sqlalchemy psycopg2-binary pillow reportlab
createdb agent_dashboard
alembic upgrade head
```

### 5.2. Tải Dunnhumby

```bash
kaggle datasets download frtgnn/dunnhumby-the-complete-journey -p data/raw/dunnhumby --unzip
```

### 5.3. Seed DB

```bash
python scripts/seed_dunnhumby.py \
  --raw-dir data/raw/dunnhumby \
  --base-date 2024-01-01 \
  --top-skus 150 \
  --top-stores 15 \
  --database-url postgresql://app:password@localhost:5432/agent_dashboard
```

Script sẽ:
1. Đọc product.csv → upsert products
2. Đọc transaction_data.csv → group by BASKET_ID → insert receipts + receipt_items
3. In thống kê: số store, sku, receipt, item đã seed

### 5.4. Demo OCR 1 basket

```bash
python scripts/render_basket_receipt.py --basket-id 123456 --out storage/receipts/raw/demo.jpg
# rồi upload qua API hoặc gọi trực tiếp extract_receipt()
```

### 5.5. Kiểm tra Forecast dùng được

```sql
SELECT receipt_date::date, store_id, product_id, SUM(quantity)
FROM receipts JOIN receipt_items ON receipts.id = receipt_items.receipt_id
WHERE status='confirmed'
GROUP BY 1,2,3
ORDER BY 1 LIMIT 10;
```

Nếu query ra daily_sales, Forecast Agent đã có dữ liệu.

## 6. Trình bày khi bảo vệ

> Dữ liệu lịch sử được seed từ Dunnhumby Complete Journey — bộ transaction đã ẩn danh của retailer Mỹ — để có đủ lịch sử cho Forecast/Combo/Text2SQL mà không phải OCR hàng loạt. Ảnh hóa đơn demo được render từ basket transaction thật để kiểm thử luồng Gemini Vision → JSON → chuẩn hóa SKU. Khi có dữ liệu POS/hóa đơn Việt Nam, chỉ cần thay bước seed bằng import từ nguồn mới; schema và pipeline không đổi.

## 7. File sẽ tạo

- `scripts/seed_dunnhumby.py` — ETL Dunnhumby → PostgreSQL
- `scripts/render_basket_receipt.py` — render ảnh hóa đơn từ basket thật (tùy chọn)
- Tài liệu này: `Ingestion_Dunnhumby_Flow.md`
