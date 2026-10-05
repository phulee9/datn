# README — Rule Sinh Hóa Đơn Giả Lập Theo Category WinMart

## 1. Mục tiêu

Tài liệu này mô tả bộ rule dùng để sinh hóa đơn giả lập từ catalog sản phẩm WinMart đã crawl.

Generator không sinh hóa đơn bằng cách random tự do từng sản phẩm. Generator cũng không hardcode rule theo một vài sản phẩm cụ thể. Toàn bộ rule phải dựa trên hệ thống category thật của WinMart trong `categories.csv`, sau đó mọi SKU trong bảng product được map vào category tương ứng để áp dụng rule.

Mục tiêu của bộ rule:

- Sinh hóa đơn có hành vi giống bán lẻ thực tế.
- Không bỏ rơi các sản phẩm ngoài một vài SKU phổ biến.
- Tạo dữ liệu có mùa vụ, khung giờ, ngày trong tuần và event rõ ràng.
- Tạo basket hợp lý để phục vụ phân tích doanh thu, combo và forecast.
- Có thể giải thích được vì sao một category tăng/giảm trong một bối cảnh cụ thể.

---

## 2. Nguyên tắc chung

Một hóa đơn phải được sinh theo chuỗi nghiệp vụ sau:

```text
Chọn ngày mua
→ Chọn khung giờ mua
→ Chọn cửa hàng
→ Xác định bối cảnh mùa/sự kiện
→ Chọn loại basket
→ Sinh số dòng hàng
→ Chọn nhóm category phù hợp
→ Chọn SKU cụ thể trong category
→ Sinh quantity theo category
→ Xuất hóa đơn
```

Không được làm theo kiểu:

```text
Random sản phẩm A
Random sản phẩm B
Random số lượng
Random tổng tiền
```

Lý do: cách random độc lập sẽ làm dữ liệu mất tính nghiệp vụ, không tạo được pattern bán lẻ, không tạo được signal combo và forecast.

---

## 3. Rule phải đi theo category, không đi theo sản phẩm cụ thể

Không viết rule kiểu:

```text
Coca x1.5
Hảo Hảo x1.3
Vinamilk x1.2
```

Vì cách này chỉ ưu tiên một vài sản phẩm được chọn tay, còn các sản phẩm khác trong catalog sẽ không có logic rõ ràng.

Rule đúng phải viết theo category:

```text
MENU09 — Đồ Uống - Giải Khát
  MENU01163 — Nước Suối
  MENU01164 — Nước Ngọt
  MENU0141  — Trà - Các Loại Khác
  MENU01162 — Cà Phê

Mùa hè:
- Nước Suối tăng mạnh
- Nước Ngọt tăng
- Trà tăng
- Cà Phê giữ baseline hoặc tăng nhẹ theo khung giờ sáng
```

Sau đó generator chọn SKU cụ thể bên trong category theo trọng số nội bộ.

> **Nguyên tắc thép toàn bộ tài liệu này: mọi rule, basket, affinity, event đều áp theo `category_code` / nhóm nghiệp vụ, không bao giờ hardcode `item_no` hay tên sản phẩm cụ thể. SKU chỉ được chọn ở bước cuối cùng sau khi category đã được quyết định.**

---

## 4. Nguồn category

Category được lấy từ file:

```text
categories.csv
```

Các trường chính:

| Trường | Ý nghĩa |
|---|---|
| `category_code` | Mã category WinMart |
| `category_name` | Tên category |
| `category_slug` | Slug category |
| `level` | Cấp category |
| `parent_code` | Category cha |
| `root_code` | Category gốc |

Rule sinh hóa đơn ưu tiên dùng:

- `category_code` cấp 2 để áp rule chi tiết.
- `root_code` để áp rule tổng quát.
- `category_name` để giải thích nghiệp vụ.

---

## 5. Mapping category WinMart sang nhóm nghiệp vụ

Generator cần có bước mapping category sang nhóm nghiệp vụ. Đây là bước nền tảng để mọi sản phẩm đều có rule.

### 5.1. Vấn đề thực tế của 2 file crawl

Qua bóc 3062 SKU thực tế (`winmart_products.csv`) đối chiếu `categories.csv` (93 code):

- `category_name` trong file product **toàn là tên ROOT level 1** (`Chăm Sóc Cá Nhân 486`, `Bánh Kẹo 441`, `Giá Siêu Rẻ 36`, `Ưu Đãi Hội Viên 12`, `OMO/COMFORT/ARIEL... ~40 dòng do lệch cột`) — không join được `category_code` level 2 (`MENU0145`, `MENU01163`...).
- `mch5_name` (338 giá trị) mới là khóa có độ mịn thật: `Mì ăn liền 106`, `Sữa tươi tiệt trùng 87`, `Sữa tắm nữ 50`, `Bánh biscuit 50`...
- `uom_name` lỗi: `"Lốc` thiếu dấu, `5500/159000/10000` là giá lọt vào cột UOM do dấu phẩy.

### 5.2. Nguyên tắc mapping

```text
Khóa chính: mch5_name → category_code (Phụ lục A)
Fallback:   category_name ROOT → root_code (chỉ khi mch5_name trống)
Không bao giờ JOIN bằng category_name == category_name
Không bao giờ hardcode item_no / tên sản phẩm
```

Rule làm sạch bắt buộc trước khi gen:

```text
if category_name in ('Giá Siêu Rẻ','Ưu Đãi Hội Viên') or (category_name.isupper() and len < 18):
    → bỏ category_name, dùng mch5_name để map (lệch cột crawl)

if uom_name in ('5500','159000','10000','9600','9500','9000'... là số):
    → uom_name = 'Gói' nếu mch5_name in (Mì, Bánh, Kẹo, Snack...) else 'Chai'

if uom_name == '"Lốc' or uom_name == 'Lốc':
    → uom_name = 'Lốc, Lô, Lố'
```

Chi tiết 338 dòng `mch5_name → category_code` xem **Phụ lục A** cuối tài liệu.

### 5.3. Bảng tổng quan root/category → nhóm nghiệp vụ

| Root / Category | Nhóm nghiệp vụ |
|---|---|
| `MENU08` Sữa các loại | `milk_dairy` |
| `MENU0133` Sữa Tươi | `milk_fresh` |
| `MENU0134` Sữa Hạt - Sữa Đậu | `milk_plant_based` |
| `MENU0135` Sữa Bột | `milk_powder` |
| `MENU01169` Sữa Chua - Váng Sữa | `yogurt_dessert` |
| `MENU0138` Bơ Sữa - Phô Mai + `MENU01161` Sữa đặc | `butter_cheese_condensed` |
| `MENU02` Rau - Củ - Trái Cây | `fresh_produce` |
| `MENU01167` Rau Lá | `fresh_vegetable` |
| `MENU01168` Củ, Quả | `fresh_root_vegetable` |
| `MENU01173` Trái cây tươi | `fresh_fruit` |
| `MENU10` Hóa Phẩm - Tẩy rửa | `household_cleaning` |
| `MENU01140` Nước Giặt | `household_laundry_detergent` |
| `MENU01144` Nước Xả | `household_fabric_softener` |
| `MENU01142` Nước Rửa Chén | `household_dishwashing` |
| `MENU01139` Bình Xịt Côn Trùng | `household_insect_spray` |
| `MENU01141` Nước Lau Sàn - Lau Kính | `household_floor_glass_cleaner` |
| `MENU01143` Nước Tẩy Rửa | `household_cleaning_liquid` |
| `MENU11` Chăm Sóc Cá Nhân | `personal_care` |
| `MENU0147` Chăm Sóc Răng Miệng | `oral_care` |
| `MENU0145` Chăm Sóc Tóc | `hair_care` |
| `MENU0151` Khăn Giấy - Khăn Ướt | `tissue_wet_wipes` |
| `MENU03` Thịt - Hải Sản Tươi | `fresh_meat_seafood` |
| `MENU0111` Thịt | `fresh_meat` |
| `MENU0113` Hải Sản | `fresh_seafood` |
| `MENU07` Bánh Kẹo | `snack_confectionery` |
| `MENU0127` Bánh Xốp - Bánh Quy | `biscuit_cookie` |
| `MENU0128` Kẹo - Chocolate | `candy_chocolate` |
| `MENU0129` Bánh Snack | `snack` |
| `MENU0130` Hạt - Trái Cây Sấy Khô | `nuts_dried_fruit` |
| `MENU31` Đồ uống có cồn | `alcohol` |
| `MENU01135` Bia | `beer` |
| `MENU09` Đồ Uống - Giải Khát | `beverage` |
| `MENU01162` Cà Phê | `coffee` |
| `MENU01163` Nước Suối | `water` |
| `MENU01164` Nước Ngọt | `soft_drink` |
| `MENU0141` Trà - Các Loại Khác | `tea_other_drink` |
| `MENU34` Mì - Thực Phẩm Ăn Liền | `instant_food` |
| `MENU01145` Mì | `instant_noodle` |
| `MENU01146` Cháo | `instant_porridge` |
| `MENU01147` Phở - Bún | `instant_pho_bun` |
| `MENU01148` Miến - Hủ Tíu - Bánh Canh | `instant_vermicelli` |
| `MENU06` Thực Phẩm Khô | `dry_food` |
| `MENU0120` Gạo - Nông Sản Khô | `rice_dry_agri` |
| `MENU0122` Ngũ Cốc - Yến Mạch | `cereal_oat` |
| `MENU0123` Thực Phẩm Đóng Hộp | `canned_food` |
| `MENU04` Thực Phẩm Chế Biến | `processed_food` |
| `MENU0115` Bánh mì | `bread` |
| `MENU0156` Xúc xích - Thịt Nguội | `sausage_cold_cut` |
| `MENU01156` Bánh bao | `dumpling_bao` |
| `MENU35` Gia vị | `seasoning` |
| `MENU01149` Dầu Ăn | `cooking_oil` |
| `MENU01150` Nước Mắm - Nước Chấm | `fish_sauce_dipping_sauce` |
| `MENU01151` Đường | `sugar` |
| `MENU01153` Hạt Nêm | `seasoning_powder` |
| `MENU05` Thực Phẩm Đông Lạnh | `frozen_food` |
| `MENU0157` Hải Sản Đông Lạnh | `frozen_seafood` |
| `MENU01158` Thịt Đông Lạnh | `frozen_meat` |
| `MENU01159` Chả Giò | `frozen_spring_roll` |
| `MENU01160` Cá - Bò Viên | `fish_beef_ball` |
| `MENU33` Trứng - Đậu Hũ | `egg_tofu` |
| `MENU01165` Trứng | `egg` |
| `MENU01138` Đậu hũ | `tofu` |
| `MENU12` Chăm Sóc Bé | `baby_care` |
| `MENU0152` Sữa Bột - Sữa Dinh Dưỡng | `baby_formula_nutrition` |
| `MENU0154` Tã - Bỉm | `diaper` |
| `MENU25` Đồ Dùng Gia Đình | `household_goods` |
| `MENU01170` Vệ Sinh Nhà Cửa | `home_sanitation` |
| `MENU26` Điện Gia Dụng | `home_appliance` |
| `MENU27` Văn Phòng Phẩm - Đồ Chơi | `stationery_toy` |

Nguyên tắc:

```text
Mỗi SKU hợp lệ phải map được về một nhóm nghiệp vụ qua mch5_name.
Nếu category ít phổ biến thì base weight thấp, không phải bằng 0.
Chỉ loại SKU nếu dữ liệu sản phẩm thiếu hoặc lỗi.
```

---

## 6. Rule tần suất mua theo category

Mỗi nhóm category có tần suất mua tự nhiên khác nhau. Đây là base weight trước khi áp mùa vụ, event, ngày trong tuần và khung giờ.

### 6.1. Nhóm mua thường xuyên

Các nhóm này có xác suất xuất hiện cao vì là hàng tiêu dùng hằng ngày hoặc mua lặp lại thường xuyên:

- Sữa tươi, sữa chua, sữa hạt.
- Rau lá, củ quả, trái cây.
- Trứng, đậu hũ.
- Mì, cháo, phở, bún ăn liền.
- Nước suối, nước ngọt, trà.
- Bánh mì, bánh bao.
- Snack, bánh nhỏ.

Căn cứ:

- Đây là nhóm FMCG hoặc thực phẩm tươi/tiện lợi.
- Người dùng có thể mua nhiều lần trong tuần.
- Phù hợp hóa đơn siêu thị mini/khu dân cư.

### 6.2. Nhóm mua trung bình

Các nhóm này có xác suất trung bình, thường xuất hiện theo bữa ăn, dịp cuối tuần hoặc khi cần bổ sung:

- Thịt, hải sản.
- Thực phẩm đông lạnh.
- Gia vị, dầu ăn, nước mắm, hạt nêm.
- Bánh kẹo, hạt, trái cây sấy.
- Cà phê.
- Đồ hộp, ngũ cốc, yến mạch.

Căn cứ:

- Có nhu cầu đều nhưng không nhất thiết mua mỗi ngày.
- Một số nhóm tăng mạnh theo dịp lễ hoặc cuối tuần.

### 6.3. Nhóm mua thưa

Các nhóm này có chu kỳ mua dài hơn, nên base weight thấp:

- Nước giặt, nước xả.
- Nước lau sàn, nước tẩy rửa.
- Dầu gội, chăm sóc da, chăm sóc răng miệng.
- Tã bỉm, chăm sóc bé.
- Đồ dùng gia đình.
- Điện gia dụng.

Căn cứ:

- Đây là nhóm không mua hằng ngày.
- Mỗi lần mua thường dùng được trong nhiều ngày hoặc nhiều tuần.
- Vẫn phải có xác suất xuất hiện, nhưng thấp hơn thực phẩm/đồ uống.

---

## 7. Rule thời gian trong ngày

Khung giờ ảnh hưởng trực tiếp tới loại basket và category được chọn.

| Khung giờ | Hành vi chính | Category tăng xác suất |
|---|---|---|
| 06:30–08:30 | Mua trước giờ làm, ăn sáng | Bánh mì, sữa, sữa chua, cà phê, nước suối, bánh nhỏ |
| 09:00–11:30 | Nội trợ, mua bổ sung buổi sáng | Rau, trái cây, sữa, thịt/hải sản, gia vị |
| 11:30–13:30 | Mua nhanh giờ trưa | Mì/cháo/phở, bánh bao, xúc xích, nước, snack |
| 14:00–16:30 | Mua bổ sung, chuẩn bị bữa tối | Sữa, bánh, trái cây, rau, thịt, trứng |
| 17:00–19:30 | Peak tan tầm, mua cho bữa tối | Rau, thịt, hải sản, trứng, đậu hũ, gia vị, nước, bia |
| 19:30–21:30 | Mua sau bữa tối, mua bổ sung | Snack, bánh kẹo, sữa, nước, khăn giấy, đồ dùng gia đình nhẹ |

Rule:

```text
category_weight_final = category_base_weight × time_slot_multiplier
```

Ví dụ:

- Hóa đơn lúc 07:15 ưu tiên bánh mì, sữa, cà phê.
- Hóa đơn lúc 18:30 ưu tiên rau, thịt, trứng, gia vị, nước.
- Hóa đơn lúc 20:30 ưu tiên snack, sữa, nước, khăn giấy.

---

## 8. Rule ngày trong tuần

Ngày trong tuần ảnh hưởng đến số hóa đơn, độ dài basket và loại category.

| Ngày | Đặc điểm |
|---|---|
| Thứ 2 | Đầu tuần, chủ yếu mua bổ sung, basket nhỏ hơn |
| Thứ 3 | Tăng nhẹ so với thứ 2 |
| Thứ 4 | Baseline |
| Thứ 5 | Baseline |
| Thứ 6 | Chuẩn bị cuối tuần, tăng nước, snack, đồ ăn gia đình |
| Thứ 7 | Cao điểm mua sắm gia đình, basket dài hơn |
| Chủ nhật | Cao, nhưng thấp hơn thứ 7 một chút |

Category tăng vào cuối tuần:

- Rau, củ, trái cây.
- Thịt, hải sản.
- Trứng, đậu hũ.
- Gia vị, dầu ăn.
- Nước suối, nước ngọt, bia.
- Snack, bánh kẹo.
- Thực phẩm đông lạnh.

Rule:

```text
weekday ảnh hưởng cả traffic và basket composition.
Cuối tuần không chỉ nhiều hóa đơn hơn, mà hóa đơn cũng có nhiều dòng hơn.
```

---

## 9. Rule mùa vụ theo tháng

Mùa vụ không được áp vào sản phẩm cụ thể, mà áp vào category.

| Giai đoạn | Bối cảnh | Category tăng |
|---|---|---|
| Tháng 9 | Tựu trường, Trung Thu | Sữa, bánh nhỏ, bánh kẹo, trà, trái cây, văn phòng phẩm/đồ chơi |
| Tháng 10 | Thu ổn định | Baseline, tăng nhẹ bánh kẹo/trà nếu còn Trung Thu |
| Tháng 11 | Se lạnh | Mì, cháo, phở, đồ nóng tăng nhẹ |
| Tháng 12 | Rét, chuẩn bị lễ/Tết | Mì, lẩu/đồ đông lạnh, bánh kẹo, bia, nước ngọt, gia vị |
| Tháng 1 | Cao điểm Tết | Bánh kẹo, hạt, bia, nước ngọt, trà, gia vị, dầu ăn, thịt, đồ đông lạnh |
| Tháng 2 | Tết/sau Tết | Traffic giảm, bánh kẹo giảm sau Tết, vệ sinh nhà cửa tăng nếu nồm |
| Tháng 3 | Nồm ẩm | Lau sàn, nước tẩy rửa, nước giặt, nước xả, khăn giấy |
| Tháng 4 | Giỗ Tổ, 30/4 | Nước, bia, snack, trái cây, đồ ăn nhanh |
| Tháng 5 | Bắt đầu hè | Nước suối, nước ngọt, trà, sữa chua, bia |
| Tháng 6 | Hè, thiếu nhi | Sữa, bánh kẹo, snack trẻ em, nước, sữa chua |
| Tháng 7 | Nóng cao điểm | Nước suối, nước ngọt, trà, bia, sữa chua |
| Tháng 8 | Cuối hè, Vu Lan, tựu trường | Trái cây, sữa, bánh ăn sáng, văn phòng phẩm/đồ chơi |

Rule:

```text
month_multiplier chỉ làm thay đổi xác suất category và traffic.
Không dùng month_multiplier để sửa trực tiếp tổng tiền hóa đơn.
```

---

## 10. Rule sự kiện

Mỗi sự kiện phải định nghĩa tối thiểu:

```text
event_name
date_range
traffic_effect
basket_size_effect
category_effect
combo_effect
```

### 10.1. Trung Thu

Thời gian giả lập:

```text
09-20 → 10-06
```

Category tăng (theo category_code):

- `MENU0127` Bánh xốp, bánh quy.
- `MENU0128` Kẹo, chocolate.
- `MENU0141` Trà.
- `MENU01173` Trái cây tươi.
- `MENU0133/MENU01169` Sữa/bánh cho trẻ em.

### 10.2. Tết Dương

Thời gian giả lập:

```text
12-28 → 01-02
```

Category tăng:

- `MENU01135` Bia.
- `MENU01164` Nước ngọt.
- `MENU0129` Snack.
- `MENU0128` Bánh kẹo.
- `MENU01173` Trái cây.

### 10.3. Pre-Tết Âm (động theo năm)

Thời gian giả lập — **tính động, không hardcode ngày dương**:

```text
Tết Âm lịch − 30 ngày  →  Tết Âm lịch − 1 ngày
Ví dụ 2026 (Tết 17/02): 01-18 → 02-16
Ví dụ 2027 (Tết 06/02): 01-07 → 02-05
```

Category tăng mạnh:

- Bánh kẹo (`MENU0127/0128`).
- Hạt, trái cây sấy (`MENU0130`).
- Bia (`MENU01135`).
- Nước ngọt (`MENU01164`).
- Trà (`MENU0141`).
- Dầu ăn (`MENU01149`).
- Nước mắm, nước chấm (`MENU01150`).
- Hạt nêm, gia vị (`MENU01153/01154/01155`).
- Thịt, hải sản, thực phẩm đông lạnh (`MENU0111/0113/0157/01158`).
- Rau, trái cây (`MENU01167/01168/01173`).
- Vệ sinh nhà cửa (`MENU01170`).

### 10.4. Ngày Tết

Thời gian giả lập (động):

```text
Tết Âm → Tết Âm + 5 ngày
Ví dụ 2026: 02-17 → 02-22
```

Rule:

- Traffic giảm mạnh.
- Basket nhỏ hơn Pre-Tết.
- Chủ yếu mua bổ sung (`small_topup`).

Category còn tăng nhẹ:

- Nước, bia (`MENU01163/01135`).
- Snack (`MENU0129`).
- Trái cây (`MENU01173`).
- Bánh kẹo (`MENU0128`).

### 10.5. Sau Tết

Thời gian giả lập (động):

```text
Tết Âm + 6 ngày → Tết Âm + 21 ngày
Ví dụ 2026: 02-23 → 03-10
```

Rule:

- Traffic giảm.
- Basket nhỏ.
- Giảm bánh kẹo, hạt, bia/nước so với Pre-Tết.
- Tăng dần lại nhóm thực phẩm thường ngày.

### 10.6. Nồm ẩm miền Bắc

Thời gian giả lập:

```text
02-20 → 03-31
```

Category tăng:

- Nước lau sàn, lau kính (`MENU01141`).
- Nước tẩy rửa (`MENU01143`).
- Nước giặt (`MENU01140`).
- Nước xả (`MENU01144`).
- Khăn giấy, khăn ướt (`MENU0151`).
- Bình xịt côn trùng (`MENU01139`) tăng nhẹ khi thời tiết ẩm.

### 10.7. Giỗ Tổ / 30-4 / 1-5

Thời gian giả lập:

```text
04-15 → 05-03
```

Category tăng:

- Bia (`MENU01135`).
- Nước suối (`MENU01163`).
- Nước ngọt (`MENU01164`).
- Trà (`MENU0141`).
- Snack (`MENU0129`).
- Trái cây (`MENU01173`).
- Thực phẩm chế biến (`MENU0115/MENU0156`).

### 10.8. Hè nóng

Thời gian giả lập:

```text
05-01 → 08-15
```

Category tăng:

- Nước suối (`MENU01163`).
- Nước ngọt (`MENU01164`).
- Trà (`MENU0141`).
- Sữa chua, váng sữa (`MENU01169`).
- Bia (`MENU01135`).
- Trái cây (`MENU01173`).

Category giảm:

- Nhóm món nóng/lẩu nếu có.
- Một phần mì/cháo nếu muốn tạo seasonal contrast.

### 10.9. Quốc tế thiếu nhi

Thời gian giả lập:

```text
05-25 → 06-03
```

Category tăng:

- Sữa (`MENU0133/0134/0135`).
- Sữa chua (`MENU01169`).
- Bánh kẹo (`MENU0127/0128`).
- Snack (`MENU0129`).
- Chăm sóc bé (`MENU0152/0154`).
- Đồ chơi nếu catalog có (`MENU27`).

### 10.10. Vu Lan

Thời gian giả lập:

```text
08-15 → 08-30
```

Category tăng:

- Trái cây (`MENU01173`).
- Bánh kẹo (`MENU0128/0127`).
- Trà (`MENU0141`).
- Thực phẩm chay (`MENU01166`).

### 10.11. Tựu trường

Thời gian giả lập:

```text
08-25 → 09-15
```

Category tăng:

- Sữa (`MENU0133/0134`).
- Bánh ăn sáng (`MENU0115`).
- Bánh nhỏ (`MENU0127`).
- Văn phòng phẩm/đồ chơi (`MENU27`).
- Chăm sóc bé (`MENU0152/0154`).

### 10.12. Payday — Ngày lương (mới)

Thời gian giả lập:

```text
05 → 10 mỗi tháng (cố định hàng tháng)
```

| Thuộc tính | Giá trị |
|---|---|
| `traffic_effect` | +15% số hóa đơn |
| `basket_size_effect` | +1 dòng trung bình |
| `category_effect` | `pantry_restock` (Gạo/Dầu ăn/Nước mắm) + `gift_beauty` (Mỹ phẩm/Chăm sóc da) + `MENU01135` Bia + `MENU0129` Snack tăng |
| `note` | Hiệu ứng mạnh hơn seasonality thường, cộng dồn với weekend nếu trùng |

### 10.13. Ngày phụ nữ 8/3 & 20/10 (mới)

Thời gian giả lập:

```text
03-06 → 03-08  (Quốc tế phụ nữ)
10-18 → 10-20  (Phụ nữ VN)
```

| Thuộc tính | Giá trị |
|---|---|
| `traffic_effect` | +20% |
| `basket_size_effect` | +1 dòng |
| `category_effect` | `MENU0150` Mỹ phẩm + `MENU0146` Chăm sóc da + `MENU0148` Chăm sóc phụ nữ + `MENU0128` Bánh kẹo x2.0–3.0 |
| `validation` | Doanh thu nhóm personal_care/beauty 2 dịp này phải cao hơn tuần trước/sau |

### 10.14. Double Day Sale 11/11 (mới)

Thời gian giả lập:

```text
11-10 → 11-12
```

| Thuộc tính | Giá trị |
|---|---|
| `traffic_effect` | +25% |
| `basket_size_effect` | +1 dòng |
| `category_effect` | `MENU0128/0129` Bánh kẹo/Snack + `MENU0133` Sữa + `MENU0150` Mỹ phẩm tăng; đồng thời `sale_boost x1.5` cho SKU có `sale_price < price` |
| `note` | Mô phỏng sàn TMĐT, không phụ thuộc WinMart có sale thật hay không |

### 10.15. Quốc Khánh 2/9 (mới)

Thời gian giả lập:

```text
08-30 → 09-02
```

Category tăng: như Giỗ Tổ/30-4 — `MENU01135` Bia + `MENU01163` Nước suối + `MENU01164` Nước ngọt + `MENU0129` Snack + `MENU01173` Trái cây.

### 10.16. Quy tắc chồng event

```text
Nếu 2+ event chồng ngày (ví dụ Nồm 02-20→03-31 chồng Sau Tết 02-23→03-10):
  → multiplier = max(multiplier_event)  (không nhân dồn, tránh x4 phi thực tế)
  → traffic_effect = max
  → basket_size_effect = max
Nếu Payday (05→10) trùng Weekend:
  → được cộng dồn: traffic payday + weekend, basket +1 payday + weekend effect
```

---

## 11. Rule loại basket

Không nên sinh một hóa đơn bằng cách chọn ngẫu nhiên N category. Nên chọn `basket_type` trước, sau đó chọn category phù hợp với basket đó.

| Basket type | Bối cảnh thường gặp | Category chính (theo category_code) |
|---|---|---|
| `quick_breakfast` | Sáng ngày thường | `MENU0115` Bánh mì, `MENU0133` Sữa, `MENU01169` Sữa chua, `MENU01162` Cà phê, `MENU01163` Nước suối |
| `lunch_quick` | Giờ trưa | `MENU01145/46/47` Mì/cháo/phở, `MENU01156` Bánh bao, `MENU0156` Xúc xích, `MENU01163/164` Nước, `MENU0129` Snack |
| `family_dinner` | Chiều tối | `MENU01167/168` Rau, `MENU0111/0113` Thịt/hải sản, `MENU01165` Trứng, `MENU01138` Đậu hũ, `MENU01150/153` Gia vị |
| `weekend_family` | Cuối tuần | `MENU01167/168/173` Rau/trái cây, `MENU0111` Thịt, `MENU01165` Trứng, `MENU01163` Nước, `MENU01135` Bia, `MENU0129` Snack, `MENU0157/158` Đông lạnh |
| `tet_stockup` | Pre-Tết | `MENU0127/128` Bánh kẹo, `MENU0130` Hạt, `MENU01135` Bia, `MENU01164` Nước ngọt, `MENU0141` Trà, `MENU01149/150/153` Gia vị, dầu ăn |
| `summer_drink` | Mùa hè | `MENU01163` Nước suối, `MENU01164` Nước ngọt, `MENU0141` Trà, `MENU01169` Sữa chua, `MENU01135` Bia |
| `cleaning_household` | Nồm ẩm hoặc mua định kỳ | `MENU01140` Nước giặt, `MENU01144` Nước xả, `MENU01141` Lau sàn, `MENU01143` Tẩy rửa, `MENU0151` Khăn giấy |
| `personal_care` | Mua định kỳ | `MENU0145` Chăm sóc tóc, `MENU0147` Răng miệng, `MENU0146` Chăm sóc da, `MENU0151` Khăn giấy |
| `baby_care` | Gia đình có trẻ nhỏ, 1-6, tựu trường | `MENU0152` Sữa bột, `MENU0154` Tã bỉm, `MENU0151` Khăn ướt, `MENU0133` Sữa, `MENU0127` Bánh |
| `small_topup` | Mua bổ sung nhanh | 1–3 món bất kỳ theo category weight |
| `pantry_restock` *(mới)* | Payday 05-10, cuối tuần, Pre-Tết | `MENU0120` Gạo + `MENU01149` Dầu ăn + `MENU01150/152` Nước mắm/Nước tương + `MENU01153` Hạt nêm (core 60%), optional `MENU01151` Đường, `MENU01152` Dấm |
| `kid_snack` *(mới)* | Tựu trường, hè, 1-6 | `MENU0133` Sữa tươi + `MENU01169` Sữa chua + `MENU0127/129` Bánh snack/biscuit, optional `MENU0128` Kẹo, `MENU0141` Nước hoa quả |
| `gift_beauty` *(mới)* | 8/3, 20/10, 11/11, Noel | `MENU0150` Mỹ phẩm + `MENU0146` Chăm sóc da + `MENU0145/11` Sữa tắm/Dầu gội, optional `MENU0151` Khăn giấy |
| `home_daily` *(mới)* | Quanh năm, tăng T7/CN | `MENU0151` Giấy vs/khăn ướt + `MENU01142` Nước rửa chén + `MENU01170` Vệ sinh nhà cửa |
| `premium_big` *(mới)* | Random 0.3% hóa đơn, tăng Payday | 1 món duy nhất `MENU26` Điện gia dụng / `MENU25` Dụng cụ nhà bếp/sửa chữa giá >400k — luôn 1 dòng, không kèm |

Rule chọn basket:

```text
basket_type được chọn dựa trên:
- tháng
- event (Payday/8-3/11-11/Pre-Tết động)
- ngày trong tuần
- khung giờ
- store profile nếu có
```

Ví dụ:

```text
07:20 ngày thường → ưu tiên quick_breakfast
12:15 ngày thường → ưu tiên lunch_quick
18:30 thứ 7 → ưu tiên weekend_family hoặc family_dinner
05-10 hàng tháng → tăng pantry_restock + gift_beauty (payday)
Pre-Tết (Tết-30→Tết-1) → ưu tiên tet_stockup
Mùa nồm → tăng cleaning_household
Mùa hè → tăng summer_drink
8/3, 20/10 → tăng gift_beauty
0.3% random → premium_big (1 món giá cao, đứng riêng 1 hóa đơn)
```

---

## 12. Rule affinity / co-occurrence theo category (thay combo cứng)

> **Quan trọng:** Không hardcode combo SKU `A+B phải đi cùng`. Toàn bộ affinity áp theo `category_code`, chỉ làm tăng `weight` 30–120% khi category A đã xuất hiện trong basket. SKU cụ thể vẫn random trong category.

| Affinity (category → category) | Khi basket đã có `category_code` A | Thì `category_code` B tăng weight | Bối cảnh | Hệ số |
|---|---|---|---|---|
| `coffee_milk` | `MENU01162` Cà Phê (hòa tan/rang xay/nước) | `MENU01161` Sữa đặc + `MENU0133` Sữa tươi | Sáng 06:30–08:30 | x1.6 |
| `beer_snack` | `MENU01135` Bia | `MENU0129` Snack (kh.tây/rau củ/khác) + `MENU01164` Nước ngọt | T6–CN, lễ, hè | x1.8 |
| `noodle_kimchi` | `MENU01145/01148` Mì/Miến/Bún | `MENU01157` Kim chi + `MENU0156` Xúc xích tiệt trùng/thanh trùng | Trưa/tối | x1.5 |
| `rice_sauce_oil` | `MENU0120` Gạo | `MENU01150` Nước mắm + `MENU01149` Dầu ăn + `MENU01153` Hạt nêm | `pantry_restock` / weekend / Pre-Tết | x1.7 |
| `shampoo_shower` | `MENU0145` Chăm sóc tóc (Dầu gội) | `MENU0146/MENU11` Sữa tắm/Dầu xả — cùng `brand_name` thì + thêm 30% | `personal_care` basket | x1.4 |
| `brush_paste` | `MENU0147` Bàn chải đánh răng | `MENU0147` Kem đánh răng | Quanh năm | x2.0 |
| `milk_diaper` | `MENU0152` Sữa bột/dinh dưỡng trẻ em | `MENU0154` Tã + `MENU0151` Giấy ướt trẻ em | 1/6, tựu trường | x2.2 |
| `breakfast_bread` | `MENU0115` Bánh mì + `MENU01156` Bánh bao | `MENU0133` Sữa + `MENU01162` Cà phê nước | Sáng | x1.5 |
| `fruit_tea_vegan` | `MENU01173` Trái cây tươi | `MENU0141` Trà + `MENU01166` Thực phẩm chay | Vu Lan 15→30/08 | x1.6 |
| `detergent_softener` | `MENU01140` Nước giặt | `MENU01144` Nước xả | Nồm ẩm, `cleaning_household` | x1.8 |
| `floor_tissue` | `MENU01141` Nước lau sàn | `MENU01143` Nước t.rửa toilet + `MENU0151` Giấy/Khăn | Nồm, dọn nhà trước Tết | x1.5 |

Nguyên tắc code:

```text
# Giả mã — affinity theo category_code, không theo SKU
if any(sku.category_code == 'MENU01135' for sku in basket):  # đã có Bia
    weight['MENU0129'] *= 1.8   # Snack tăng
    weight['MENU01164'] *= 1.4  # Nước ngọt tăng
# Sau đó mới chọn SKU ngẫu nhiên trong category đó:
#   Bia → random trong 30 Bia nội địa + 5 Bia NK
#   Snack → random trong 45 Snack kh.tây + 27 Snack rau củ + 11 Snack khác
```

Căn cứ:

- Các category trong cùng affinity có quan hệ sử dụng chung.
- Affinity chỉ tăng xác suất, không ép buộc — giữ tính đa dạng SKU.
- Tạo tín hiệu mua kèm cho thuật toán association rules mà không làm mất tự nhiên.

---

## 13. Rule số dòng hàng trong hóa đơn

Số dòng hàng phụ thuộc vào basket type và bối cảnh.

| Context | Số dòng thường gặp |
|---|---|
| Mua nhanh sáng (`quick_breakfast`) | 1–3 dòng |
| Mua nhanh trưa (`lunch_quick`) | 1–3 dòng |
| Ngày thường | 2–5 dòng |
| Chiều tối ngày thường (`family_dinner`) | 3–6 dòng |
| Cuối tuần (`weekend_family`) | 3–8 dòng |
| Pre-Tết (`tet_stockup`) | 5–15 dòng |
| Ngày Tết | 1–4 dòng |
| Sau Tết | 1–4 dòng |
| Hóa phẩm/tẩy rửa (`cleaning_household`) | 1–4 dòng |
| Chăm sóc cá nhân (`personal_care`) | 1–3 dòng |
| Chăm sóc bé (`baby_care`) | 2–5 dòng |
| Tích trữ pantry (`pantry_restock`) | 4–8 dòng |
| Quà/mỹ phẩm (`gift_beauty`) | 2–5 dòng |
| Hàng giá cao (`premium_big`) | 1 dòng (luôn 1, quantity=1) |

Nguyên tắc:

```text
Không dùng một phân bố số dòng duy nhất cho mọi hóa đơn.
Basket type quyết định số dòng hợp lý.
premium_big luôn 1 dòng, không kèm category khác.
```

---

## 14. Rule quantity & giá theo category

### 14.1. Quantity theo category và UOM

Quantity phải phụ thuộc vào loại category và đơn vị bán (`uom_name`) trong bảng product.

| Nhóm category | Rule quantity |
|---|---|
| Sữa hộp/chai | Số nguyên, thường 1–4; dịp thiếu nhi/tựu trường có thể cao hơn |
| Sữa bột | Thường 1, hiếm khi 2 |
| Sữa chua/váng sữa | 1–4; mùa hè có thể tăng |
| Nước suối/nước ngọt/trà | 1–6; mùa hè/cuối tuần có thể cao hơn |
| Bia | 1–2 lốc/thùng nếu sản phẩm là lốc/thùng; dịp lễ/Tết tăng |
| Cà phê | 1–2 |
| Mì/cháo/phở/bún | 1–5 gói; nếu sản phẩm là thùng thì thường 1 |
| Bánh mì/bánh bao | 1–3 |
| Snack/bánh kẹo | 1–4; Trung Thu/Tết/thiếu nhi tăng |
| Hạt/trái cây sấy | 1–3; Pre-Tết tăng |
| Rau lá | Decimal theo kg hoặc bó/gói tùy product; thường nhỏ |
| Củ/quả | Decimal hoặc số nguyên tùy product |
| Trái cây | Decimal kg hoặc số nguyên tùy product; Vu Lan/Tết tăng |
| Thịt/hải sản tươi | Decimal kg; chiều tối/cuối tuần tăng |
| Thực phẩm đông lạnh | 1–3; cuối tuần/Tết tăng |
| Trứng | Thường 1 vỉ/hộp, hiếm khi 2 |
| Đậu hũ | 1–3 |
| Gia vị/dầu ăn/nước mắm | Thường 1; Pre-Tết có thể 2 |
| Nước giặt/nước xả | Thường 1, hiếm khi 2 |
| Lau sàn/tẩy rửa/rửa chén | Thường 1 |
| Chăm sóc cá nhân | Thường 1 |
| Tã/bỉm/chăm sóc bé | Thường 1–2 |
| Đồ dùng gia đình | Gần như luôn 1 |
| Điện gia dụng | Gần như luôn 1, xác suất xuất hiện rất thấp |
| Văn phòng phẩm/đồ chơi | 1–3, tăng mùa tựu trường/thiếu nhi |

Nguyên tắc quantity:

```text
Hàng đóng gói dùng quantity số nguyên.
Hàng cân ký có thể dùng quantity thập phân — CHỈ khi uom_name in (Kg, Qủa, Bó, Ram).
  Ví dụ 72 SKU có uom_name=Kg (Rau, Trái cây, Thịt) → cho phép 0.2–3.0 kg.
  Các UOM còn lại (Gói, Chai, Hộp, Cái, Lốc, Thùng, Tuýp, Lon, Bộ...) → luôn integer.
Không sinh quantity bằng 0 hoặc âm.
Không sinh quantity phi thực tế so với category.
Trứng (VỈ/Khay), Dầu ăn (Chai/Can), Bia thùng → luôn quantity=1.
Không trùng SKU trong 1 hóa đơn (1 item_no chỉ xuất hiện 1 lần / invoice).
```

### 14.2. Giá và sale boost

```text
invoice_total = sum(final_price * quantity)   # luôn dùng final_price, không dùng price gốc
sale_boost: nếu sale_price < price (đang khuyến mãi):
  → weight[category] *= 1.3  vào Weekend / Payday 05-10 / Double Day 11-11
  → kiểm chứng: nhóm SKU đang sale phải có tần suất xuất hiện cao hơn 20-30% trong các dịp trên
```

---

## 15. Rule không bỏ rơi category ít phổ biến

Mọi category hợp lệ đều phải có cơ hội xuất hiện.

Rule:

```text
base_weight thấp không có nghĩa là bằng 0.
```

Ví dụ:

- Điện gia dụng: xác suất rất thấp (0.3% qua `premium_big`), nhưng vẫn có thể xuất hiện.
- Đồ dùng gia đình: thấp, tăng nhẹ cuối tuần hoặc dịp dọn nhà.
- Văn phòng phẩm/đồ chơi: thấp, tăng vào tựu trường và 1-6.
- Mỹ phẩm/chăm sóc da: thấp đến trung bình, xuất hiện theo basket `gift_beauty` + event 8/3, 20/10, 11/11.
- Bình xịt côn trùng: thấp, tăng nhẹ mùa nồm/ẩm/nóng.

Chỉ loại category/SKU nếu:

- Sản phẩm thiếu tên.
- Sản phẩm thiếu giá hợp lệ.
- Sản phẩm không map được category (sau khi đã qua mch5_name + fallback).
- Sản phẩm lỗi dữ liệu.
- Sản phẩm không phù hợp để xuất hiện trong hóa đơn bán lẻ giả lập.

---

## 16. Rule giải thích hệ số

Mỗi hệ số trong generator phải có căn cứ, không được ghi hệ số rời rạc.

Format giải thích một rule:

```text
category_code:
category_name:
context:
multiplier:
applies_to:
reason:
validation:
```

Ví dụ:

```text
category_code: MENU01163
category_name: Nước Suối
context: Hè nóng T5–T8
multiplier: tăng xác suất chọn category
applies_to: product/category selection weight
reason: Mùa hè miền Bắc nóng, nhu cầu giải khát tăng.
validation: Sau khi sinh dữ liệu, số lượng bán nhóm Nước Suối T5–T8 phải cao hơn T12–T2.
```

Không nên viết:

```text
Nước Suối x2.0
```

mà không giải thích hệ số đó áp dụng vào đâu và kiểm chứng bằng gì.

---

## 17. Validation sau khi sinh dữ liệu

Sau khi generator chạy, cần kiểm tra rule có thật sự tạo pattern đúng hay không.

Các check chính:

| Check | Kỳ vọng |
|---|---|
| Category mùa hè | Nước suối, nước ngọt, trà, sữa chua, bia tăng trong T5–T8 |
| Category Tết | Bánh kẹo, hạt, bia, nước ngọt, trà, gia vị tăng trong Pre-Tết (Tết-30→Tết-1) |
| Category nồm ẩm | Lau sàn, tẩy rửa, nước giặt, nước xả, khăn giấy tăng T2–T3 |
| Category sáng | Bánh mì, sữa, cà phê tăng trong 06:30–08:30 |
| Category chiều tối | Rau, thịt, trứng, gia vị tăng trong 17:00–19:30 |
| Cuối tuần | Basket dài hơn và nhóm gia đình tăng |
| Payday 05-10 | `pantry_restock` và `gift_beauty` tăng, traffic +15% |
| 8/3 & 20/10 | Mỹ phẩm/chăm sóc da/nữ tăng x2–3 |
| 11/11 | SKU đang sale (`sale_price < price`) tăng tần suất 20-30% |
| Affinity cà phê→sữa đặc | `MENU01162` thường đi cùng `MENU01161/MENU0133` |
| Affinity bia→snack | `MENU01135` thường đi cùng `MENU0129` |
| Affinity gạo→nước mắm/dầu | `MENU0120` thường đi cùng `MENU01150/MENU01149` |
| Category ít phổ biến | Vẫn có xuất hiện nhưng tần suất thấp (premium_big 0.3%) |
| Quantity decimal | Chỉ xuất hiện ở UOM Kg/Qủa/Bó/Ram, không ở Gói/Chai/Hộp |
| Không trùng SKU | 1 `item_no` không lặp trong cùng 1 invoice |

Nếu các check trên không đạt, cần chỉnh lại rule category/basket, không sửa bằng cách ép trực tiếp doanh thu hoặc tổng tiền.

---

## 18. Tóm tắt nguyên tắc bắt buộc

1. Rule sinh hóa đơn phải đi theo category WinMart (`category_code`/`mch5_name`), không theo vài SKU cụ thể.
2. Mọi SKU hợp lệ phải map được vào một nhóm nghiệp vụ qua `mch5_name` (khóa chính), `category_name` chỉ fallback.
3. Category ít phổ biến vẫn có base weight, không bị bỏ qua.
4. Thời gian trong ngày ảnh hưởng đến category được chọn.
5. Ngày trong tuần ảnh hưởng đến basket size và basket composition.
6. Mùa vụ và event ảnh hưởng đến category, không sửa trực tiếp tổng tiền. Event Pre-Tết tính động theo Tết Âm lịch; chồng event lấy `max` không nhân dồn; Payday 05-10 hàng tháng + 8/3, 20/10, 11/11, 2/9 là bắt buộc.
7. Basket type phải được chọn trước khi chọn sản phẩm. Có 15 basket (10 cũ + 5 mới `pantry_restock/kid_snack/gift_beauty/home_daily/premium_big`).
8. Co-occurrence phải là affinity theo category (`weight *= 1.4–2.2`), không hardcode SKU. Xem mục 12.
9. Quantity phải phụ thuộc category và `uom_name` (decimal chỉ Kg/Qủa/Bó/Ram; sale_boost `x1.3` cho SKU đang khuyến mãi; không trùng SKU trong 1 hóa đơn).
10. Mỗi hệ số phải có lý do và validation đi kèm.

---

## Phụ lục A — Mapping `mch5_name` → `category_code` (khóa chính, 338 dòng)

> Dùng bảng này để map 3062 SKU. `mch5_name` là khóa chính. Đã nhóm theo `category_code` đích để generator áp weight theo category.

### A1. Nhóm Sữa (MENU08)

| `mch5_name` (số SKU) | `category_code` | Nhóm nghiệp vụ |
|---|---|---|
| Sữa tươi tiệt trùng 87, Sữa tươi thanh trùng 9 | `MENU0133` | `milk_fresh` |
| Sữa đậu nành 17, Sữa hạt 13, Sữa đặc có đường 16, Bột ngũ cốc trái cây 15 | `MENU0134` | `milk_plant_based` / `milk_condensed` |
| Sữa bột chức năng 8, Sữa bột trẻ em 2, Sữa d.dưỡng trẻ em 13, Sữa d.dưỡng người lớn 3, Sữa d.dưỡng ngườilớn 3 | `MENU0135` / `MENU0152` | `milk_powder` / `baby_formula` |
| SCU tiệt trùng 29, SCU lợi khuẩn 34, SCU thanh trùng 3, Sữa chua ăn 25 | `MENU01169` | `yogurt_dessert` |
| Váng sữa 8, Kem sữa tươi làmbánh 5, Bơ động vật 12, P.mai mềm(miếng/hộp) 11, P.mai tráng miệng 10, P.mai cứng 8, P.mai rắc/bột 2, P.mai mềm(khối) 2, Bơ đóng hộp 8 | `MENU0138` | `butter_cheese` |
| Sữa đặc có đường 16 | `MENU01161` | `condensed_milk` |

### A2. Nhóm Rau-Củ-Trái Cây (MENU02)

| `mch5_name` | `category_code` | Nhóm |
|---|---|---|
| Rau gia vị ăn lá 11, Rau gia vị ăn củ 11, Rau gia vị ăn quả 5, Rau cải 6, Rau khác 4, Rau mầm 2, Xà lách 2, Giá đỗ 1, Cần tây 1, Rau dền 1, Nấm 8 | `MENU01167` | `fresh_vegetable` |
| Củ khoai 4, Cà chua 4, Bầu bí 3, Cà rốt 2, Ớt chuông 2, Đậu 2, Củ khác 1, Củ cải 1, Su su 1, Cà 1, Ngô bắp 1, Dưa chuột 1, Măng sơ chế 13 | `MENU01168` | `fresh_root_vegetable` |
| Táo NK 12, Dưa NĐ 5, Xoài NĐ 5, Bưởi NĐ 3, Roi (Mận) NĐ 3, Kiwi NK 7, Cam NĐ 2, Cam NK 2, Chanh dây 1, Táo NĐ 1, Đu Đủ 1, Chôm chôm 1, Hồng xiêm 1, Ổi 1, Chuối 1, Dứa 1, Thanh Long 1, Chà Là NK 1 | `MENU01173` | `fresh_fruit` |

### A3. Nhóm Hóa Phẩm - Tẩy rửa (MENU10)

| `mch5_name` | `category_code` |
|---|---|
| Nước giặt 34, Bột giặt 6 | `MENU01140` |
| Nước xả 20 | `MENU01144` |
| Nước rửa chén bát 12 | `MENU01142` |
| Thuốc diệt côn trùng 9, Đèn diệt c.tr 3 | `MENU01139` |
| Nước lau sàn nhà 11, Nước lau kính 3 | `MENU01141` |
| Nước t.rửa toilet 10, Nước tẩy rửa nhà bếp 6, Nước tẩy quần áo 1, Nước tẩy trang 9 | `MENU01143` |

### A4. Nhóm Chăm Sóc Cá Nhân (MENU11) — 486 SKU, nhóm lớn nhất

| `mch5_name` | `category_code` |
|---|---|
| Kem đánh răng 37, Bàn chải đánh răng 35, Nước súc miệng 9, Tăm chỉ nkhoa 6, Kem đánh răng trẻ em 6, Bchải trẻ em 6 | `MENU0147` |
| Sữa tắm nữ 50, Sữa tắm nam 15, Sữa rửa mặt nữ 22, Sữa rửa mặt nam 5, Mặt nạ dưỡng da 10, Kem dưỡng da mặt 3, Nước hoa hồng 3, Kem chống nắng 9, Nước tẩy trang 9, Kem dưỡng toàn thân 5, Bông tẩy trang 10, Bông tai 10... | `MENU0146` |
| Dầu gội nữ 37, Dầu gội nam 18, Dầu xả & dưỡng tóc 14, Lăn khử mùi Nam 14, Lăn khử mùi nữ 11, Xịt khử mùi Nam 10, Xịt khử mùi nữ 6, Tạo dáng tóc 5 | `MENU0145` |
| BVS Chu kỳ 22, BVS Ban đêm 12, BVS Hàng ngày 8, Dao cạo râu 11, Bao cao su 5, Dung dịch vs 6, Khăn giấy gói 15, Giấy vệ sinh 20, Giấy ướt gia đình 6, Khăn tay 6, Giấy bếp 3 | `MENU0151` / `MENU0148` |
| Sáp thơm 12, Nước xịt phòng 4, Nước rửa tay 14, Xà bông tắm 1, DCCS tai mũi họng 2, Mỹ phẩm t.điểm môi 2, Miếng dán trị mụn 2... | `MENU0149/MENU0150` |

### A5. Nhóm Thịt - Hải Sản (MENU03) + Đông Lạnh (MENU05)

| `mch5_name` | `category_code` |
|---|---|
| Lợn (heo) nội địa 8, Bò Bê NK 2, Bò Bê nội địa 1, Gà nội địa 5, Sơ chế thịt heo 3, Sơ chế Bò Bê 1, Giáp xác tươi 5, Cá nước ngọt 2, Cá nước mặn 1, THS NK tươi 1 | `MENU0111/0113` |
| Thịt bò đông lạnh 12, Tôm đông lạnh 7, Mực đông lạnh 3, Cua đông lạnh 3, Thịt xông khói 12, Giò chả 7, Chả giò đông lạnh 6, Cá-bò viên 4, Chả viên 4, Khoai đông lạnh 5, Há cảo 15, Tàu hũ tempura 3, Lẩu đông lạnh 1... | `MENU01158/0157/01159/01160/0158` |

### A6. Nhóm Bánh Kẹo (MENU07) — 441 SKU

| `mch5_name` | `category_code` |
|---|---|
| Bánh biscuit 50, Bánh xốp và quế 15, Bánh bông lan 16, Bánh pie 10, Bánh gạo 10, Bánh Mochi 7, Bánh gạo Toppoki 11, Bánh ngũ cốc 8, Bánh trứng giòn 4... | `MENU0127` |
| Kẹo mềm 47, Kẹo cứng 36, Chocolate 40, Kẹo gum 13, Kẹo đồ chơi 13, Kẹo truyền thống 1, Kẹo cân ký 1 | `MENU0128` |
| Snack kh.tây chiên 45, Snack rau củ quả 27, Snack khác 11, Snack rong biển 9 | `MENU0129` |
| Hạt bí đóng gói 42, Trái cây s.khô đgói 18, Mứt & Ô mai 9, Thạch cân ký 5, Nho khô 1, Trái cây sấy khô cký 1 | `MENU0130` |

### A7. Nhóm Đồ Uống (MENU09 + MENU31)

| `mch5_name` | `category_code` |
|---|---|
| Bia nội địa 30, Bia nhập khẩu 5, Cider 3 | `MENU01135` |
| Cà phê hòa tan 34, Cà phê rang xay 23, Cà phê nước 4, Cà phê hạt 1 | `MENU01162` |
| Nước khoáng 19, Nước tinh khiết 8, Nước uống chức năng 16, Nước tăng lực 20 | `MENU01163` |
| Nước ngọt có ga 40, Nước uống dinh dưỡng 14, Nước hoa quả 35 | `MENU01164` |
| Nước trà 26, Trà túi lọc 9, Trà thảo dược 6, Trà mạn 8, Trà hòa tan 5, Trà sữa 5 | `MENU0141` |

### A8. Nhóm Mì - Thực Phẩm Ăn Liền (MENU34)

| `mch5_name` | `category_code` |
|---|---|
| Mì ăn liền 106 | `MENU01145` |
| Miến ăn liền 7, Miến khô 6, Hủ tiếu ăn liền 1, Bánh đa ăn liền 3, Bánh đa khô 1 | `MENU01148` |
| Cháo ăn liền 22 | `MENU01146` |
| Bún, phở ăn liền 21, Bún khô Phở khô 4, Nui khô 5, Mỳ khô 14 | `MENU01147` |
| TP ăn liền khác 1 | `MENU34` |

### A9. Nhóm Thực Phẩm Khô (MENU06)

| `mch5_name` | `category_code` |
|---|---|
| Gạo tẻ 10, Gạo dinh dưỡng 2, Gạo nếp 2, Đậu khô 1, Lạc khô 1, Hạt sen khô 1, Nấm khô 1 | `MENU0120` |
| Ngũ cốc ăn sáng 25, Bột ngũ cốc trái cây 15 | `MENU0122` |
| Thịt đóng hộp 8, Cá tôm đóng hộp 8, Bơ đóng hộp 8, Rau củ quả đóng hộp 3, Mứt đóng hộp 1, Mắm đóng hộp 2 | `MENU0123` |
| Rong biển cbiến đgói 38, Bột chiên rán 9, Bột làm bánh 4, Bột gạo mì nếp 3, Bột cacao 2, Các loại bột khác 7, Mỳ chính 10, Tiêu 4, Muối 8, Đường cát 6, Đường viên 5, Dấm 3, Tương cà 7, Tương ớt 15, Mayonnaise 20, Dầu hào 6, Mù tạt 2, Kim chi đóng gói 8, Thực phẩm chay đgói 2, Chà bông 2 | `MENU0124/0125/01166` |

### A10. Nhóm Thực Phẩm Chế Biến (MENU04) + Gia Vị (MENU35) + Trứng Đậu Hũ (MENU33)

| `mch5_name` | `category_code` |
|---|---|
| Bánh mỳ 1, Bánh mỳ sandwich 3, Bánh ngọt khác 5, Bánh bông lan tươi 4, Bánh ngọt 5, Bánh mặn 3 | `MENU0115` |
| Xúc xích tiệt trùng 21, Xúc xích thanh trùng 14, Jambon 1, Thịt muối 4 | `MENU0156` |
| Bánh bao 9 | `MENU01156` |
| Kim chi đóng gói 8 | `MENU01157` |
| Thức uống tr.miệng 4, Nem Chạo 4, Đồ ăn vặt từ thịt 4, Tráng miệng 3 | `MENU0114` |
| Dầu hỗn hợp 14, Dầu nành 12, Dầu ô liu 8, Dầu hướng dương 7, Các loại dầu gạo hạ 7, Dầu KHác 2, Dầu hạt cải 1 | `MENU01149` |
| Nước mắm 37, Tương ớt 15, Nước tương 12, Các loại sốt 50 | `MENU01150/152/154` |
| Đường cát 6, Đường viên 5 | `MENU01151` |
| Bột canh hạt nêm 18, Mỳ chính 10, Hạt sen khô 1... | `MENU01153` |
| Trứng gà 8, Trứng chức năng 3 | `MENU01165` |
| Đậu hũ 7, Đậu đông lạnh 1 | `MENU01138` |

### A11. Nhóm Chăm Sóc Bé (MENU12) + Đồ Dùng Gia Đình (MENU25) + Điện Gia Dụng (MENU26) + VPP Đồ Chơi (MENU27)

| `mch5_name` | `category_code` |
|---|---|
| Sữa d.dưỡng trẻ em 13, Sữa bột trẻ em 2 | `MENU0152` |
| Tã quần trẻ em 4, Tã dán trẻ em 1, Tã quần tã dán nlớn 1 | `MENU0154` |
| Tắm gội t.thân t.em 7, Sữa tắm trẻ em 1, Giấy ướt trẻ em 9, Khăn ướt đa năng 2 | `MENU01137/0155` |
| Dụng cụ nhà bếp 26, Dụng cụ vs nhà cửa 23, Dụng cụ giặt là 17, Đồ ch.đựng thực phẩm 14, Đồ bao gói 19, Khăn tắm 7, Khăn mặt 4, Khăn lau 2, Thảm phòng ngủ 2, Đồ nội thất 1... | `MENU25` |
| Nồi cơm điện 4, Ổ cắm điện 1, Bàn là 1, Bình đun điện 1, Máy xay Máy ép 1, Lò nướng 1, Máy sấy tóc 1, Bếp điện 1, Pin 4 | `MENU26` |
| Bút 29, Vở 7, Đồ dùng học sinh 12, Đồ dùng v.phòng khác 3, Giấy 1, Sổ 2, Băng dính 4, Quà tặng 9, Đồ chơi bé trai 2, Giày/dép nữ 1 | `MENU27` |

> **Cách dùng:** Generator load `mch5_category_map.csv` (tách từ bảng trên) → `sku.category_code = map[sku.mch5_name]` → sau đó `weight[category_code]` mới có tác dụng. Toàn bộ 3062 SKU đều có đường map, không bỏ rơi category ít phổ biến.

