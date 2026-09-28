# WinMart Pipeline — Schema DWH (Raw / Staging / Silver) + JSON Extract

## 0. Luồng tổng quan

```
categories.json (menu gốc)
  -> crawl_winmart/winmart_crawler.ipynb
    -> products_raw.csv (debug, 14 cột)
    -> winmart_products.csv (dim_product nguồn, 10 cột)
      -> stg_product -> dim_product

Ảnh hoá đơn WinMart+ (PTT/MSCH/SL/KM/T.Tiền)
  -> OCR/LLM extract
    -> raw_receipt_ocr.extracted_json (JSON thô - chỉ có gì trên giấy)
      -> parse -> stg_receipt + stg_receipt_item
        -> match dim_product (product_name_raw -> item_no)
          -> fact_invoice + fact_invoice_item (join dim_product, dim_store)
```

> Nguyên tắc: **JSON chỉ là raw/audit**. Không tạo "JSON đích" rồi mới ghi fact. Parse JSON -> staging rows -> match -> ghi fact. Tiết kiệm 1 lần I/O, query nhanh hơn, đúng chuẩn dim/fact cho Text-to-SQL / Recommend / Forecast.

---

## 1. JSON khi extract

### 1.1. categories.json (input crawl, từ WinMart)

```json
{
  "data": [
    {
      "parent": {
        "code": "MENU08",
        "name": "Sữa các loại",
        "seoName": "sua-cac-loai--c08",
        "level": 1,
        "rootCode": null
      },
      "lstChild": [
        {
          "parent": {
            "code": "MENU0133",
            "name": "Sữa Tươi",
            "seoName": "sua-tuoi--c0133",
            "level": 2,
            "rootCode": "MENU08"
          },
          "lstChild": []
        }
      ]
    }
  ]
}
```

Collect -> `categories.csv`:
`category_code, category_name, category_slug, level, parent_code, root_code`

### 1.2. Product API (1 item) - `GET https://api-crownx.winmart.vn/it/api/web/v3/item/category?slug=...&storeCode=1535&storeGroupCode=1998`

Field thực tế đã kiểm chứng với `itemNo=10290084`:

```json
{
  "id": "73bdd301-92fd-4bb0-a5e7-9bfc122d5413",
  "itemNo": "10290084",
  "sku": "10290084G1",
  "barcode": "8934868184393",
  "name": "Nước Giặt Comfort Dưỡng Vải Đa Năng Thiên Nhiên Thanh Khiết 3.0KG",
  "description": "Nước Giặt Comfort...",
  "shortDescription": "COMFORT NG Thiên Nhiên Thanh Khiết 3kg",
  "longDescription": "<p>RA MẮT...</p>",
  "brand": "10029",
  "brandName": "COMFORT",
  "isAlcohol": false,
  "seoName": "comfort-ng-thien-nhien-thanh-khiet-3kg--s10290084",
  "mediaUrl": "https://s3-hcmc02.higiocloud.vn/images/2024/11/10290084-20241117095253.jpg",
  "mediaItems": [{"mediaUrl": "..."}],
  "uom": "G1",
  "uomId": "5f10c194-2572-4b2f-b080-959743d37eb0",
  "uomName": "Gói",
  "quantityPerUnit": 1.0,
  "price": 275000.0,
  "salePrice": 137500.0,
  "quantity": 60.0,
  "promotionCode": "2301496289",
  "promotionType": "ZB10",
  "scaleType": "EQUAL",
  "scaleQuantity": 1.0,
  "itemType": "ZTRD",
  "categoryCode": "MENU114",
  "categoryName": "Giá Siêu Rẻ",
  "mch1": "2", "mch1Name": "Phi thực phẩm",
  "mch2": "202", "mch2Name": "Hoá mỹ phẩm",
  "mch3": "20202", "mch3Name": "Hóa phẩm",
  "mch4": "2020201", "mch4Name": "Chất giặt tẩy",
  "mch5": "202020104", "mch5Name": "Nước giặt",
  "uoms": [{ "uom": "G1", "sku": "10290084G1", "price": 275000.0, "salePrice": 137500.0, "quantity": 60.0, "barcode": "8934868184393" }]
}
```

**PAGING:**
```json
{ "paging": { "totalCount": 38, "pageNumber": 1, "pageSize": 50, "totalPages": 38 } }
```

### 1.3. Receipt OCR JSON (JSON thô trích từ ảnh hoá đơn thật)

Chỉ chứa gì nhìn thấy trên giấy - KHÔNG bịa `store.address / payment_method / item_no`:

```json
{
  "invoice_id": "47780126004425",
  "invoice_code": "D669",
  "barcode": "2471066966-41781",
  "tax_code": "M1-26-CPN7Q-04138504425",
  "purchase_datetime": "2026-04-25T10:31:00",
  "store_code": "4179",
  "store_name_raw": "WinMart+",
  "cashier_id": "06016727",
  "items": [
    {
      "line_no": 1,
      "product_name_raw": "LÊ GIÁ mầm tôm 110g",
      "quantity": 1,
      "unit_price": 17500,
      "discount": 0,
      "line_total": 17500
    },
    {
      "line_no": 2,
      "product_name_raw": "KEWPIE Nước xốt mè rang chai 500ml",
      "quantity": 1,
      "unit_price": 133500,
      "discount": 19600,
      "line_total": 113800
    },
    {
      "line_no": 3,
      "product_name_raw": "WMNK Táo Royal Gala NZL",
      "quantity": 1.344,
      "unit_price": 89900,
      "discount": 14650,
      "line_total": 106176
    }
  ],
  "total_discount": 34250,
  "total_amount": 237576,
  "qr_text": "Quét QR để xuất hoá đơn hoặc truy cứu...",
  "ocr_confidence": 0.94
}
```

> `subtotal` không có trên giấy -> tự tính `SUM(line_total) + total_discount` để validate.

### 1.4. Receipt Enriched JSON (tùy chọn, không bắt buộc lưu - chỉ để debug sau khi JOIN)

```json
{
  "invoice_id": "47780126004425",
  "purchase_datetime": "2026-04-25T10:31:00",
  "store_code": "4179",
  "items": [
    {
      "item_no": "10290084",
      "product_name": "Nước Giặt Comfort ...",
      "brand_name": "COMFORT",
      "mch5_name": "Nước giặt",
      "uom_name": "Gói",
      "quantity": 1,
      "unit_price": 133500,
      "discount": 19600,
      "line_total": 113800,
      "match_status": "exact",
      "match_score": 100
    }
  ]
}
```

Nếu lưu file thì chỉ để audit, nguồn chính vẫn là `fact_*`.

---

## 2. LAYER RAW (landing - giữ nguyên như nguồn)

### 2.1. raw_categories_json

```sql
CREATE TABLE raw_categories_json (
    raw_id          BIGSERIAL PRIMARY KEY,
    source_file     TEXT        NOT NULL,          -- categories.json
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload         JSONB       NOT NULL            -- toàn bộ file JSON
);
CREATE INDEX idx_raw_categories_ingested ON raw_categories_json(ingested_at);
```

### 2.2. raw_winmart_product_api

Lưu response API theo từng page/category để có thể replay (khuyến nghị):

```sql
CREATE TABLE raw_winmart_product_api (
    raw_id          BIGSERIAL PRIMARY KEY,
    category_slug   TEXT        NOT NULL,
    page_number     INT         NOT NULL,
    page_size       INT         NOT NULL,
    store_code      TEXT        NOT NULL,
    store_group_code TEXT       NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    http_status     INT,
    payload         JSONB       NOT NULL,          -- { data:{items:[]}, paging:{} }
    UNIQUE (category_slug, page_number, store_code, fetched_at)
);
CREATE INDEX idx_raw_product_slug ON raw_winmart_product_api(category_slug);
CREATE INDEX idx_raw_product_fetched ON raw_winmart_product_api(fetched_at);
```

### 2.3. raw_receipt_ocr

```sql
CREATE TABLE raw_receipt_ocr (
    raw_receipt_id  BIGSERIAL PRIMARY KEY,
    source_image_path TEXT      NOT NULL,          -- s3/local path ảnh hoá đơn
    invoice_id      TEXT,                          -- PTT nếu OCR được, có thể NULL trước khi parse
    ocr_engine      TEXT        NOT NULL,          -- tesseract / gpt4o / gemini ...
    ocr_status      TEXT        NOT NULL DEFAULT 'success', -- success / partial / failed
    ocr_confidence  NUMERIC(5,2),
    extracted_json  JSONB       NOT NULL,          -- JSON thô mục 1.3
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_raw_receipt_invoice ON raw_receipt_ocr(invoice_id);
CREATE INDEX idx_raw_receipt_created ON raw_receipt_ocr(created_at);
CREATE INDEX idx_raw_receipt_json_gin ON raw_receipt_ocr USING GIN (extracted_json);
```

> Nếu dùng SQLite/MySQL: `extracted_json TEXT` (lưu JSON string), không có `JSONB/GIN`.

---

## 3. LAYER STAGING (làm sạch nhẹ, flatten JSON -> rows)

### 3.1. stg_category (từ categories.json)

```sql
CREATE TABLE stg_category (
    category_code   TEXT PRIMARY KEY,  -- MENU08
    category_name   TEXT NOT NULL,
    category_slug   TEXT NOT NULL UNIQUE, -- sua-cac-loai--c08
    level           INT  NOT NULL,
    parent_code     TEXT REFERENCES stg_category(category_code),
    root_code       TEXT,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Nguồn: `categories.csv` do notebook tạo.

### 3.2. stg_product (từ products_raw.csv / API items)

```sql
CREATE TABLE stg_product (
    item_no         TEXT PRIMARY KEY,  -- 10290084
    sku_raw         TEXT,              -- 10290084G1
    name            TEXT NOT NULL,
    name_norm       TEXT NOT NULL,     -- lower + bỏ dấu + chuẩn hoá spaces (để match nhanh)
    brand_code      TEXT,              -- brand
    brand_name      TEXT,
    price           NUMERIC(12,2),
    sale_price      NUMERIC(12,2),
    final_price     NUMERIC(12,2) NOT NULL, -- salePrice ?? price
    uom_name        TEXT,              -- Gói / Chai / Kg
    quantity_per_unit NUMERIC(10,2),
    stock_quantity  NUMERIC(10,2),     -- quantity theo store 1535
    category_code   TEXT REFERENCES stg_category(category_code),
    category_name   TEXT,
    category_slug   TEXT,
    mch5_code       TEXT,
    mch5_name       TEXT,
    barcode         TEXT,
    seo_name        TEXT,
    media_url       TEXT,
    page_number     INT,
    crawl_datetime  TIMESTAMPTZ NOT NULL,
    raw_id          BIGINT REFERENCES raw_winmart_product_api(raw_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_stg_product_name_norm ON stg_product(name_norm);
CREATE INDEX idx_stg_product_brand ON stg_product(brand_name);
CREATE INDEX idx_stg_product_mch5 ON stg_product(mch5_name);
CREATE INDEX idx_stg_product_barcode ON stg_product(barcode);
-- Postgres fuzzy
-- CREATE INDEX idx_stg_product_name_trgm ON stg_product USING GIN (name gin_trgm_ops);
-- CREATE INDEX idx_stg_product_name_norm_trgm ON stg_product USING GIN (name_norm gin_trgm_ops);
```

**File hiện tại sau khi vá:** `winmart_products.csv` chỉ có 10 cột gọn để nạp thẳng vào staging:
`item_no, name, brand_name, category_name, mch5_name, price, sale_price, final_price, uom_name, crawl_datetime`
-> các cột còn lại (`sku_raw, barcode, mch5_code...`) nếu cần thì lấy từ `products_raw.csv` 14 cột.

### 3.3. stg_receipt (flatten từ raw_receipt_ocr)

```sql
CREATE TABLE stg_receipt (
    invoice_id      TEXT PRIMARY KEY,  -- 47780126004425
    invoice_code    TEXT,              -- D669
    barcode         TEXT,              -- 2471066966-41781
    tax_code        TEXT,
    purchase_datetime TIMESTAMPTZ NOT NULL,
    purchase_date   DATE GENERATED ALWAYS AS (purchase_datetime::date) STORED,
    store_code      TEXT NOT NULL,
    store_name_raw  TEXT,
    cashier_id      TEXT,
    total_discount  NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_amount    NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(12,2) GENERATED ALWAYS AS (total_amount + total_discount) STORED,
    raw_receipt_id  BIGINT NOT NULL REFERENCES raw_receipt_ocr(raw_receipt_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_stg_receipt_date ON stg_receipt(purchase_date);
CREATE INDEX idx_stg_receipt_store ON stg_receipt(store_code);
CREATE INDEX idx_stg_receipt_datetime ON stg_receipt(purchase_datetime);
```

### 3.4. stg_receipt_item

```sql
CREATE TABLE stg_receipt_item (
    invoice_id      TEXT NOT NULL REFERENCES stg_receipt(invoice_id) ON DELETE CASCADE,
    line_no         INT  NOT NULL,
    product_name_raw TEXT NOT NULL,
    product_name_norm TEXT NOT NULL,   -- chuẩn hoá để match
    quantity        NUMERIC(10,3) NOT NULL, -- float vì 1.344 kg
    unit_price      NUMERIC(12,2) NOT NULL,
    discount        NUMERIC(12,2) NOT NULL DEFAULT 0,
    line_total      NUMERIC(12,2) NOT NULL, -- quantity*unit_price - discount
    PRIMARY KEY (invoice_id, line_no)
);
CREATE INDEX idx_stg_receipt_item_name_norm ON stg_receipt_item(product_name_norm);
CREATE INDEX idx_stg_receipt_item_invoice ON stg_receipt_item(invoice_id);
```

---

## 4. LAYER SILVER / DWH (chuẩn hoá, sẵn sàng cho BI & train model)

### 4.1. dim_product

```sql
CREATE TABLE dim_product (
    item_no         TEXT PRIMARY KEY,
    sku_raw         TEXT,
    name            TEXT NOT NULL,
    name_norm       TEXT NOT NULL,
    brand_code      TEXT,
    brand_name      TEXT NOT NULL,
    category_code   TEXT,
    category_name   TEXT,
    mch5_code       TEXT,
    mch5_name       TEXT,
    price           NUMERIC(12,2),
    sale_price      NUMERIC(12,2),
    final_price     NUMERIC(12,2) NOT NULL,
    uom_name        TEXT,
    barcode         TEXT,
    seo_name        TEXT,
    media_url       TEXT,
    crawl_datetime  TIMESTAMPTZ NOT NULL,
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to        TIMESTAMPTZ,
    is_current      BOOLEAN NOT NULL DEFAULT true
);
CREATE INDEX idx_dim_product_brand ON dim_product(brand_name);
CREATE INDEX idx_dim_product_mch5 ON dim_product(mch5_name);
CREATE INDEX idx_dim_product_category ON dim_product(category_name);
CREATE INDEX idx_dim_product_name_norm ON dim_product(name_norm);
```

> Nguồn: `SELECT DISTINCT ON (item_no) * FROM stg_product ORDER BY item_no, crawl_datetime DESC`

### 4.2. dim_category (optional, nếu muốn chuẩn star schema)

```sql
CREATE TABLE dim_category (
    category_code   TEXT PRIMARY KEY,
    category_name   TEXT NOT NULL,
    category_slug   TEXT NOT NULL UNIQUE,
    level           INT  NOT NULL,
    parent_code     TEXT REFERENCES dim_category(category_code),
    root_code       TEXT
);
```

### 4.3. dim_store

```sql
CREATE TABLE dim_store (
    store_code      TEXT PRIMARY KEY,  -- 4179
    store_name      TEXT NOT NULL,     -- WinMart+ 4179 (mapping thủ công)
    address         TEXT,              -- 10 Trần Phú Hà Nội (nếu có)
    region          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- seed thủ công 5-10 store, không crawl
INSERT INTO dim_store(store_code, store_name, address) VALUES
  ('1535','WinMart 1535 - Hà Nội','Hà Nội'),
  ('4179','WinMart+ 4179','Hà Nội'),
  ('0001','WinMart+ Demo 0001','TP.HCM');
```

### 4.4. dim_cashier (optional)

```sql
CREATE TABLE dim_cashier (
    cashier_id      TEXT PRIMARY KEY,
    store_code      TEXT REFERENCES dim_store(store_code)
);
```

### 4.5. fact_invoice (1 dòng / hoá đơn)

```sql
CREATE TABLE fact_invoice (
    invoice_id      TEXT PRIMARY KEY,
    invoice_code    TEXT,
    barcode         TEXT,
    tax_code        TEXT,
    purchase_datetime TIMESTAMPTZ NOT NULL,
    purchase_date   DATE NOT NULL,
    store_code      TEXT NOT NULL REFERENCES dim_store(store_code),
    cashier_id      TEXT,
    subtotal        NUMERIC(12,2) NOT NULL,
    total_discount  NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_amount    NUMERIC(12,2) NOT NULL,
    item_count      INT  NOT NULL,       -- COUNT(items)
    total_quantity  NUMERIC(10,3) NOT NULL,
    raw_receipt_id  BIGINT REFERENCES raw_receipt_ocr(raw_receipt_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_fact_invoice_amount CHECK (subtotal = total_amount + total_discount)
);
CREATE INDEX idx_fact_invoice_date ON fact_invoice(purchase_date);
CREATE INDEX idx_fact_invoice_store ON fact_invoice(store_code);
CREATE INDEX idx_fact_invoice_datetime ON fact_invoice(purchase_datetime);
```

### 4.6. fact_invoice_item (1 dòng / món - BẢNG QUAN TRỌNG NHẤT)

```sql
CREATE TABLE fact_invoice_item (
    invoice_id      TEXT NOT NULL REFERENCES fact_invoice(invoice_id) ON DELETE CASCADE,
    line_no         INT  NOT NULL,
    item_no         TEXT REFERENCES dim_product(item_no), -- NULL nếu unmatched
    product_name_raw TEXT NOT NULL,       -- OCR thô để audit
    quantity        NUMERIC(10,3) NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    discount        NUMERIC(12,2) NOT NULL DEFAULT 0,
    line_total      NUMERIC(12,2) NOT NULL,
    match_status    TEXT NOT NULL DEFAULT 'unmatched', -- exact / normalized / fuzzy / unmatched / manual
    match_score     NUMERIC(5,2),         -- 0-100
    PRIMARY KEY (invoice_id, line_no)
);
CREATE INDEX idx_fact_item_invoice ON fact_invoice_item(invoice_id);
CREATE INDEX idx_fact_item_item_no ON fact_invoice_item(item_no);
CREATE INDEX idx_fact_item_match ON fact_invoice_item(match_status);
```

> **Không lưu** `brand_name/mch5_name/price` lặp trong fact -> JOIN `dim_product` khi query. Tiết kiệm dung lượng, tránh lệch khi giá đổi.

---

## 5. ER (rút gọn)

```
raw_receipt_ocr 1--* stg_receipt 1--* stg_receipt_item
raw_winmart_product_api 1--* stg_product 1--1 dim_product

dim_store 1--* fact_invoice 1--* fact_invoice_item *--1 dim_product
dim_store 1--* dim_cashier
```

---

## 6. Pipeline chi tiết từng step

| Step | Input | Output | Ghi chú |
|------|-------|--------|---------|
| 1 | `categories.json` | `categories.csv` + `stg_category` | `collect_categories()` trong notebook |
| 2 | `stg_category` | `raw_winmart_product_api` | crawl `api-crownx.winmart.vn` theo `slug`, `PAGE_SIZE=50`, `REQUEST_DELAY=0.8` |
| 3 | `raw_winmart_product_api` | `stg_product` | `parse_product()` -> flatten, dedup `seen_item_nos` theo `item_no` |
| 4 | `stg_product` | `dim_product` | `SELECT DISTINCT ON (item_no)` + `name_norm` |
| 5 | Ảnh hoá đơn | `raw_receipt_ocr` | OCR/LLM -> JSON thô mục 1.3 |
| 6 | `raw_receipt_ocr` | `stg_receipt` + `stg_receipt_item` | JSON flatten, `product_name_norm = normalize(product_name_raw)` |
| 7 | `stg_receipt_item` JOIN `dim_product` | `fact_invoice_item.item_no` | exact -> normalized -> fuzzy (rapidfuzz) + check `unit_price ~= final_price` |
| 8 | `stg_receipt` | `fact_invoice` | enrich `store_code -> dim_store` |
| 9 | `fact_*` | BI / Text-to-SQL / Recommend / Forecast | Aggregate `daily_sales(date, mch5_name) = SUM(quantity, revenue)` |

**Match rule gợi ý:**
1. `product_name_norm = dim_product.name_norm` -> `exact`
2. `fuzzy >= 85` + `ABS(unit_price - final_price)/final_price < 0.2` -> `fuzzy`
3. Không match -> `item_no=NULL, match_status=unmatched` -> cho vào queue review thủ công.

---

## 7. Query mẫu (dùng cho Text-to-SQL / Forecast / Recommend)

```sql
-- Doanh thu theo ngày + mch5 (forecast)
SELECT f.purchase_date, p.mch5_name,
       SUM(i.quantity) AS total_qty,
       SUM(i.line_total) AS revenue
FROM fact_invoice f
JOIN fact_invoice_item i ON f.invoice_id = i.invoice_id
JOIN dim_product p ON i.item_no = p.item_no
GROUP BY f.purchase_date, p.mch5_name
ORDER BY f.purchase_date;

-- Top combo (recommend - frequent itemset)
SELECT a.item_no AS item_a, b.item_no AS item_b, COUNT(*) AS co_occurrence
FROM fact_invoice_item a
JOIN fact_invoice_item b ON a.invoice_id = b.invoice_id AND a.item_no < b.item_no
GROUP BY a.item_no, b.item_no
ORDER BY co_occurrence DESC LIMIT 20;

-- Text-to-SQL: sản phẩm sữa rẻ nhất dưới 50k
SELECT item_no, name, final_price FROM dim_product
WHERE mch5_name = 'Sữa tươi' AND final_price < 50000
ORDER BY final_price LIMIT 5;

-- Kiểm tra hoá đơn thiếu match
SELECT invoice_id, COUNT(*) AS unmatched
FROM fact_invoice_item WHERE item_no IS NULL GROUP BY invoice_id;
```

---

## 8. Tối ưu tốc độ & dung lượng

- **Tốc độ:** index trên `name_norm`, `purchase_date`, `item_no`, `store_code`. Match exact trên `name_norm` trước, chỉ fuzzy với ~15% còn lại. Dùng `pg_trgm` nếu Postgres.
- **Dung lượng:** fact chỉ lưu FK + số liệu (`quantity, unit_price, discount, line_total`), không lặp `brand/mch5/media`. JSON chỉ ở `raw_*`.
- **Nhanh:** flatten sớm (JSON -> staging rows), không parse JSON mỗi khi query. Batch insert.
- **Đúng:** `line_total = quantity * unit_price - discount`, `subtotal = total_amount + total_discount`, check constraint ở `fact_invoice`.

---

## 9. File hiện tại trong repo

- `crawl_winmart/categories.json` - input menu gốc (đặt cùng thư mục notebook)
- `crawl_winmart/categories.csv` - output step 1
- `crawl_winmart/products_raw.csv` - 14 cột debug: `item_no,sku_raw,name,brand_name,price,sale_price,final_price,uom_name,category_code,category_name,category_slug,mch5_name,page_number,crawl_datetime`
- `crawl_winmart/winmart_products.csv` - 10 cột silver nguồn: `item_no,name,brand_name,category_name,mch5_name,price,sale_price,final_price,uom_name,crawl_datetime` (dedup bằng `seen_item_nos` ngay trong lúc crawl, không cần cell cleanup cuối)
- `crawl_winmart/winmart_crawler.ipynb` - đã vá: thêm `brand_name/mch5_name/uom_name/crawl_datetime`, bỏ cell "Làm sạch và xuất CSV cuối"

> Cần gen hoá đơn giả thì đọc `winmart_products.csv` làm catalog, gen `raw_receipt_ocr` giả theo đúng JSON thô 1.3, rồi chạy pipeline 6-8.
