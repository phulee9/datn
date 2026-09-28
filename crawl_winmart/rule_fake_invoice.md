# WinMart — Rule Fake Hoá Đơn Miền Bắc (Training Text-to-SQL / Recommend / Forecast)

> Catalog nguồn: `winmart_products.csv` (`item_no, name, brand_name, category_name, mch5_name, price, sale_price, final_price, uom_name, crawl_datetime`)
> Output fake: JSON OCR sạch giống trích xuất từ ảnh hoá đơn thật -> `raw -> staging -> silver(dim/fact)`

---

## 1. Nguyên tắc

- Gen bằng **code 100%**, seed cố định, reproduce được.
- JSON fake = JSON OCR thô, chỉ có gì trên giấy mới có:
  `invoice_id, invoice_code, barcode, tax_code, purchase_datetime, store_code, store_name_raw, cashier_id, items[{line_no, product_name_raw, quantity, unit_price, discount, line_total}], total_discount, total_amount, ocr_confidence`.
- Không có trong JSON OCR: `item_no, brand_name, category_name, mch5_name, address, payment_method` (lấy sau khi JOIN `dim_product/dim_store`).
- `product_name_raw = products.name`, `unit_price/discount/line_total` bám `price/final_price` trong catalog.
- Dữ liệu **sạch 100%**: không OCR noise, không dòng thiếu, không tiền lệch.
- Không để `item_no = NULL`. Nếu `new_product` thì INSERT vào `dim_product` rồi mới ghi fact.
- `ocr_confidence = 1.0` cho bản sạch.

---

## 2. Quy mô

```yaml
num_invoices: 300000   # khuyến nghị, 200k-500k đều ok
date_range: 2025-09-01 -> 2026-08-31  # 12 tháng đủ 4 mùa + Tết
avg_items_per_invoice: 3.0-3.5
=> ~960k dòng fact_invoice_item
```

---

## 3. Thời gian — Month Multiplier (miền Bắc)

| Tháng | Bối cảnh | Hệ số |
|------|----------|------:|
| 09 | Tựu trường, Trung Thu | 1.20 |
| 10 | Thu ổn định (baseline) | 1.00 |
| 11 | Se lạnh, trước Tết | 0.95 |
| 12 | Chuẩn bị Tết, rét | 1.40 |
| 01 | Cao điểm Tết | **2.20** |
| 02 | Sau Tết, nồm ẩm | 0.70 |
| 03 | Nồm, thấp điểm | 0.80 |
| 04 | Giỗ Tổ, 30/4-1/5 | 1.15 |
| 05 | Hè bắt đầu | 1.30 |
| 06 | Hè + thi cử | 1.35 |
| 07 | Nóng đỉnh | 1.40 |
| 08 | Cuối hè, Vu Lan | 1.10 |

```
invoice_count_day = base * month_multiplier * weekday_multiplier * event_multiplier * noise(0.85-1.15)
```

---

## 4. Weekday Multiplier

| Thứ | Hệ số |
|-----|------:|
| T2 | 0.90 |
| T3 | 0.95 |
| T4 | 1.00 |
| T5 | 1.00 |
| T6 | 1.30 |
| T7 | 1.60 |
| CN | 1.55 |

---

## 5. Giờ trong ngày

| Khung giờ | Tỷ trọng | Lý do miền Bắc |
|-----------|---------:|----------------|
| 06:30-08:30 | 12% | Chợ sớm |
| 09:00-11:30 | 15% | Nội trợ |
| 11:30-13:30 | 10% | Trưa |
| 14:00-16:30 | 12% | Đón con |
| 17:00-19:30 | **38%** | Tan tầm — peak lớn nhất |
| 19:30-21:30 | 13% | Sau bữa tối |

Giờ hợp lệ: `06:30 -> 21:30`.

---

## 6. Sự kiện miền Bắc

| Sự kiện | Thời gian | Tác động chính |
|---------|-----------|----------------|
| Trung Thu | 09-20 -> 10-06 | Bánh kẹo x1.8, trà x1.3, trái cây x1.2 |
| Tết Dương | 12-28 -> 01-02 | Bia/nước x1.5, snack x1.4 |
| Pre-Tết | 01-15 -> 02-15 | Bánh kẹo x3.5, hạt khô x3.0, bia/nước x2.5, thịt/giò x2.0 |
| Ngày Tết | 02-16 -> 02-22 | invoice_count x0.35-0.6 (nghỉ) |
| Sau Tết | 02-23 -> 03-10 | invoice_count x0.7 |
| Nồm ẩm | 02-20 -> 03-31 | Lau sàn x1.4, khăn giấy x1.2, giặt xả x1.2 |
| Giỗ Tổ/30-4 | 04-15 -> 05-03 | Bia/nước x1.6, snack x1.5 |
| Hè nóng | 05-01 -> 08-15 | Nước suối x2.0, kem x2.2, bia x1.7, mì/lẩu x0.75 |
| 01-06 | 05-25 -> 06-03 | Sữa x1.5, bánh kẹo x1.6 |
| Vu Lan | 08-15 -> 08-30 | Trái cây x1.5 |
| Tựu trường | 08-25 -> 09-15 | Sữa hộp x1.4, bánh ăn sáng x1.3 |

---

## 7. Seasonal Weight theo mch5_name

| mch5_name | T12-T2 (Đông/Tết) | T5-T8 (Hè) | T9-T11 (Thu) |
|-----------|------------------:|----------:|-------------:|
| Bia/Nước ngọt/Nước suối/Trà | 0.6 | **1.8** | 1.0 |
| Kem/Sữa chua uống | 0.5 | **2.0** | 0.9 |
| Mì/Phở/Cháo ăn liền | **1.5** | 0.8 | 1.1 |
| Lẩu/Gia vị lẩu/Xúc xích | **1.8** | 0.6 | 1.0 |
| Bánh kẹo/Hạt/Giỏ quà | **3.5 (T1)** | 0.7 | 1.2 (T9) |
| Rau/Trái cây | **1.3 (Tết)** | 1.1 | 1.0 |
| Sữa | 1.0 đều | 1.0 | 1.0 |

```
weight = base_weight * seasonal_weight[tháng][mch5]
```

---

## 8. Product Weight

- Pareto: 20% SKU active chiếm 70% lượt mua.
- Active set: 1000-3000 SKU (`final_price>0`, có `name/mch5/brand`, ưu tiên nhóm thiết yếu).
- Base weight cao: Sữa, Mì, Trứng, Rau/Trái cây, Nước, Bánh mì.
- Base weight trung bình: Bánh kẹo, Gia vị, Thịt/cá.
- Base weight thấp: Giặt xả, Dầu gội, Gia dụng.
- Brand bias nhẹ miền Bắc: Vinamilk/TH x1.25, Hảo Hảo x1.25, Omachi x1.15, La Vie/Aquafina x1.15, Kinh Đô x1.15, Comfort/Omo/Sunlight x1.1.
- `sale_price < price` -> weight x1.2, discount >20% -> x1.4.
- `final_price > 500k` -> x0.4, `>1M` -> x0.2.

---

## 9. Số item / hoá đơn

**Ngày thường:**

| Số dòng | Tỷ trọng |
|---------|---------:|
| 1 | 12% |
| 2 | 22% |
| 3 | 24% |
| 4 | 18% |
| 5 | 10% |
| 6-8 | 10% |
| 9-15 | 4% |

**Cuối tuần:** 1:8%, 2:18%, 3:22%, 4:20%, 5:14%, 6-8:13%, 9-15:5%
**Pre-Tết:** 1:5%, 2:12%, 3:18%, 4:20%, 5:18%, 6-8:20%, 9-15:7%
**Sau Tết:** 1:18%, 2:28%, 3:25%, 4:15%, 5:8%, 6-8:5%, 9-15:1%

Không trùng `item_no` trong cùng hoá đơn (tăng `quantity`). Mỗi `mch5` tối đa 2 dòng (Tết/bánh kẹo, nước hè cho phép 3-5).

---

## 10. Quantity

| Loại | Rule |
|------|------|
| Gói/Chai/Hộp/Lon/Túi | 1:76%, 2:18%, 3:4%, 4-5:1.5%, 6-12:0.5% |
| Kg (Rau 0.2-0.8, Trái cây 0.5-2.5, Thịt/cá 0.3-1.5, khác 0.2-2.0) | round 3 số lẻ, VD 0.35/0.5/1.344 |
| Lốc/Thùng (name chứa "lốc/thùng/24 lon/6 chai") | 1:90%, 2:9%, 3:1% |

---

## 11. Giá & Tiền

**Có sale** (`price > final_price`):
```
unit_price = price
discount   = (price - final_price) * quantity
line_total = final_price * quantity
```
**Không sale:**
```
unit_price = final_price
discount   = 0
line_total = quantity * final_price
```

```
total_discount = SUM(discount)
total_amount   = SUM(line_total)
subtotal       = total_amount + total_discount   # tính ở fact
Validate: SUM(line_total)==total_amount, SUM(discount)==total_discount, lệch <=1đ
```

Không random discount, tiền luôn khớp.

---

## 12. Combo (Recommend)

`base_injection = 40%`, cuối tuần 45%, Pre-Tết 55%, Hè 45%, Sau Tết 30%.

| Combo | Áp dụng | Thành phần (theo mch5_name) |
|-------|---------|------------------------------|
| Ăn sáng | quanh năm, sáng 06:30-09:00 | Bánh mì + Sữa/Sữa chua |
| Mì + Trứng | quanh năm, đông x1.5 | Mì/Phở/Bún/Cháo + Trứng + Xúc xích/Rau |
| Lẩu mùa đông | T12-T2, 15% | Gia vị lẩu/Nước lẩu + Thịt + Rau + Nấm/Đậu |
| Tết | 01-15->02-15, 40% | Bánh kẹo + Nước/Bia + Hạt/Trà + Gia vị/Dầu |
| Nước hè | T5-T8, 20% | Nước suối + Nước ngọt/Trà + Kem/Sữa chua |
| Giặt xả | quanh năm, nồm/đông tăng | Nước giặt + Nước xả |
| Chăm sóc cá nhân | quanh năm | Dầu gội + Sữa tắm + Kem đánh răng |
| Trẻ em | tựu trường/1-6 | Sữa + Bánh nhỏ + Khăn ướt |
| Rau/Trái cây | thường xuyên | Rau + Trái cây + Sữa chua |

---

## 13. Store

5-7 store WinMart+ miền Bắc, ví dụ:

| store_code | Khu vực | Weight |
|-----------|---------|-------:|
| 1535 | HN - Cầu Giấy | 0.22 |
| 4179 | HN - Đống Đa | 0.20 |
| 2026 | HN - Hoàng Mai | 0.18 |
| 3001 | HN - Hà Đông | 0.15 |
| 4412 | HN - Long Biên | 0.12 |
| 5108 | Bắc Ninh | 0.07 |
| 6203 | Hải Phòng | 0.06 |

JSON chỉ lưu `store_code + store_name_raw = "WinMart+"`, region lưu ở `dim_store`.

---

## 14. Cashier

- Mỗi store 6-12 cashier: `NV:060167xx`.
- 30% cashier xử lý 60% hoá đơn.
- Ca sáng 06:30-14:00, ca chiều 14:00-21:30.

---

## 15. Mã hoá đơn

| Trường | Rule | VD |
|--------|------|----|
| `invoice_id` | 14 chữ số unique | `47780126004425` |
| `invoice_code` | 1 chữ A-Z + 3 số | `D669` |
| `barcode` | 10 số + "-" + 5 số | `2471066966-41781` |
| `tax_code` | `M1-YY-XXXXX-11 số` | `M1-26-CPN7Q-04138504425` |

---

## 16. Sản phẩm mới

Mặc định `new_product_rate = 0` (match 100%). Nếu bật 1-2% thì INSERT vào `dim_product` với `item_no = NEW000001`, `match_status = new_product`.

---

## 17. Output

```
fake_receipts.jsonl        # mỗi dòng 1 JSON OCR sạch
fake_receipts_config.json  # seed + config reproduce
fake_receipt_items_debug.csv  # optional: invoice_id,line_no,item_no,product_name_raw,quantity,unit_price,discount,line_total
```

---

## 18. Luồng DWH

```
winmart_products.csv -> stg_product -> dim_product
fake_receipts.jsonl  -> raw_receipt_ocr -> stg_receipt + stg_receipt_item -> JOIN dim_product -> fact_invoice + fact_invoice_item
```

## 19. Validate sau gen

- `invoice_id` unique 100%
- `SUM(line_total)==total_amount`, `SUM(discount)==total_discount`
- `match_rate == 100%` (hoặc new_product đã insert)
- Thấy rõ: T1 cao nhất, T2/T3 thấp, T5-T7 nước tăng, T12-T2 mì/lẩu tăng, 17-19h30 peak, T7/CN cao hơn ngày thường

## 20. Config chốt

```yaml
region: northern_vietnam
seed: 42
num_invoices: 300000
date_range: 2025-09-01 -> 2026-08-31
month_multiplier: {1:2.2,2:0.7,3:0.8,4:1.15,5:1.3,6:1.35,7:1.4,8:1.1,9:1.2,10:1.0,11:0.95,12:1.4}
weekday: {T2:0.9,T3:0.95,T4:1.0,T5:1.0,T6:1.3,T7:1.6,CN:1.55}
hour: {06:30-08:30:0.12,09:00-11:30:0.15,11:30-13:30:0.10,14:00-16:30:0.12,17:00-19:30:0.38,19:30-21:30:0.13}
combo: {base:0.40, weekend:0.45, pre_tet:0.55, summer:0.45}
price_mode: catalog_price_with_line_discount
clean: true
```
