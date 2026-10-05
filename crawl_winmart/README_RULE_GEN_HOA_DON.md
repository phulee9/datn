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

Ví dụ mapping tổng quan:

| Root / Category | Nhóm nghiệp vụ |
|---|---|
| `MENU08` Sữa các loại | `milk_dairy` |
| `MENU0133` Sữa Tươi | `milk_fresh` |
| `MENU0134` Sữa Hạt - Sữa Đậu | `milk_plant_based` |
| `MENU0135` Sữa Bột | `milk_powder` |
| `MENU01169` Sữa Chua - Váng Sữa | `yogurt_dessert` |
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
Mỗi SKU hợp lệ phải map được về một nhóm nghiệp vụ.
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

Category tăng:

- Bánh xốp, bánh quy.
- Kẹo, chocolate.
- Trà.
- Trái cây tươi.
- Sữa/bánh cho trẻ em.

Căn cứ:

- Trung Thu gắn với bánh kẹo, trà, trái cây và trẻ em.

### 10.2. Tết Dương

Thời gian giả lập:

```text
12-28 → 01-02
```

Category tăng:

- Bia.
- Nước ngọt.
- Snack.
- Bánh kẹo.
- Trái cây.

Căn cứ:

- Dịp nghỉ ngắn, tụ họp gia đình/bạn bè.

### 10.3. Pre-Tết Âm

Thời gian giả lập:

```text
01-15 → 02-15
```

Category tăng mạnh:

- Bánh kẹo.
- Hạt, trái cây sấy.
- Bia.
- Nước ngọt.
- Trà.
- Dầu ăn.
- Nước mắm, nước chấm.
- Hạt nêm, gia vị.
- Thịt, hải sản, thực phẩm đông lạnh.
- Rau, trái cây.
- Vệ sinh nhà cửa.

Căn cứ:

- Trước Tết có hành vi mua tích trữ, tiếp khách, biếu tặng và dọn dẹp nhà cửa.

### 10.4. Ngày Tết

Thời gian giả lập:

```text
02-16 → 02-22
```

Rule:

- Traffic giảm mạnh.
- Basket nhỏ hơn Pre-Tết.
- Chủ yếu mua bổ sung.

Category còn tăng nhẹ:

- Nước, bia.
- Snack.
- Trái cây.
- Bánh kẹo.

Căn cứ:

- Một số cửa hàng giảm hoạt động, người dùng đã mua tích trữ trước đó.

### 10.5. Sau Tết

Thời gian giả lập:

```text
02-23 → 03-10
```

Rule:

- Traffic giảm.
- Basket nhỏ.
- Giảm bánh kẹo, hạt, bia/nước so với Pre-Tết.
- Tăng dần lại nhóm thực phẩm thường ngày.

Căn cứ:

- Sau Tết nhu cầu mua sắm lớn giảm, chuyển về mua bổ sung hằng ngày.

### 10.6. Nồm ẩm miền Bắc

Thời gian giả lập:

```text
02-20 → 03-31
```

Category tăng:

- Nước lau sàn, lau kính.
- Nước tẩy rửa.
- Nước giặt.
- Nước xả.
- Khăn giấy, khăn ướt.
- Bình xịt côn trùng tăng nhẹ khi thời tiết ẩm.

Căn cứ:

- Miền Bắc nồm ẩm làm tăng nhu cầu lau dọn, giặt xả và vệ sinh nhà cửa.

### 10.7. Giỗ Tổ / 30-4 / 1-5

Thời gian giả lập:

```text
04-15 → 05-03
```

Category tăng:

- Bia.
- Nước suối.
- Nước ngọt.
- Trà.
- Snack.
- Trái cây.
- Thực phẩm chế biến.

Căn cứ:

- Dịp nghỉ lễ, đi chơi, tụ họp gia đình.

### 10.8. Hè nóng

Thời gian giả lập:

```text
05-01 → 08-15
```

Category tăng:

- Nước suối.
- Nước ngọt.
- Trà.
- Sữa chua, váng sữa.
- Bia.
- Trái cây.

Category giảm:

- Nhóm món nóng/lẩu nếu có.
- Một phần mì/cháo nếu muốn tạo seasonal contrast.

Căn cứ:

- Thời tiết nóng làm tăng nhu cầu giải khát và sản phẩm mát/lạnh.

### 10.9. Quốc tế thiếu nhi

Thời gian giả lập:

```text
05-25 → 06-03
```

Category tăng:

- Sữa.
- Sữa chua.
- Bánh kẹo.
- Snack.
- Chăm sóc bé.
- Đồ chơi nếu catalog có.

Căn cứ:

- Dịp dành cho trẻ em, tăng nhóm sữa/bánh/đồ chơi/chăm sóc bé.

### 10.10. Vu Lan

Thời gian giả lập:

```text
08-15 → 08-30
```

Category tăng:

- Trái cây.
- Bánh kẹo.
- Trà.
- Thực phẩm chay.

Căn cứ:

- Vu Lan thường gắn với cúng lễ, trái cây và thực phẩm chay.

### 10.11. Tựu trường

Thời gian giả lập:

```text
08-25 → 09-15
```

Category tăng:

- Sữa.
- Bánh ăn sáng.
- Bánh nhỏ.
- Văn phòng phẩm/đồ chơi.
- Chăm sóc bé.

Căn cứ:

- Giai đoạn quay lại trường học, tăng đồ ăn sáng, sữa và đồ dùng học tập.

---

## 11. Rule loại basket

Không nên sinh một hóa đơn bằng cách chọn ngẫu nhiên N category. Nên chọn `basket_type` trước, sau đó chọn category phù hợp với basket đó.

| Basket type | Bối cảnh thường gặp | Category chính |
|---|---|---|
| `quick_breakfast` | Sáng ngày thường | Bánh mì, sữa, sữa chua, cà phê, nước suối |
| `lunch_quick` | Giờ trưa | Mì/cháo/phở, bánh bao, xúc xích, nước, snack |
| `family_dinner` | Chiều tối | Rau, thịt/hải sản, trứng, đậu hũ, gia vị |
| `weekend_family` | Cuối tuần | Rau, trái cây, thịt, trứng, nước, bia, snack, đông lạnh |
| `tet_stockup` | Pre-Tết | Bánh kẹo, hạt, bia, nước ngọt, trà, gia vị, dầu ăn |
| `summer_drink` | Mùa hè | Nước suối, nước ngọt, trà, sữa chua, bia |
| `cleaning_household` | Nồm ẩm hoặc mua định kỳ | Nước giặt, nước xả, lau sàn, tẩy rửa, khăn giấy |
| `personal_care` | Mua định kỳ | Chăm sóc tóc, răng miệng, da, khăn giấy |
| `baby_care` | Gia đình có trẻ nhỏ, 1-6, tựu trường | Sữa bột, tã bỉm, khăn ướt, sữa, bánh |
| `small_topup` | Mua bổ sung nhanh | 1–3 món bất kỳ theo category weight |

Rule chọn basket:

```text
basket_type được chọn dựa trên:
- tháng
- event
- ngày trong tuần
- khung giờ
- store profile nếu có
```

Ví dụ:

```text
07:20 ngày thường → ưu tiên quick_breakfast
12:15 ngày thường → ưu tiên lunch_quick
18:30 thứ 7 → ưu tiên weekend_family hoặc family_dinner
Pre-Tết → ưu tiên tet_stockup
Mùa nồm → tăng cleaning_household
Mùa hè → tăng summer_drink
```

---

## 12. Rule combo / co-occurrence theo category

Combo phải sinh theo category, không hardcode SKU cụ thể.

| Combo | Category liên quan | Bối cảnh |
|---|---|---|
| Ăn sáng | Bánh mì + Sữa/Cà phê/Sữa chua | Sáng 06:30–08:30 |
| Mì nhanh | Mì/Phở/Cháo + Trứng/Xúc xích | Trưa, tối, ngày lạnh |
| Bữa tối | Rau + Thịt/Hải sản + Gia vị | Chiều tối |
| Bữa gia đình cuối tuần | Rau + Thịt/Hải sản + Trứng + Nước/Bia | T7/CN |
| Tết | Bánh kẹo + Hạt + Bia/Nước ngọt + Trà | Pre-Tết |
| Hè | Nước suối + Nước ngọt/Trà + Sữa chua | T5–T8 |
| Giặt xả | Nước giặt + Nước xả | Mua định kỳ, nồm ẩm |
| Vệ sinh nhà cửa | Lau sàn + Nước tẩy + Khăn giấy | Nồm ẩm, dọn nhà trước Tết |
| Chăm sóc cá nhân | Chăm sóc tóc + Răng miệng + Khăn giấy | Mua định kỳ |
| Chăm sóc bé | Sữa bột + Tã/Bỉm + Khăn ướt | Gia đình có trẻ nhỏ, 1-6, tựu trường |
| Vu Lan | Trái cây + Trà + Thực phẩm chay | Vu Lan |

Nguyên tắc:

```text
Combo chỉ quyết định nhóm category nên cùng xuất hiện.
SKU cụ thể vẫn được chọn từ catalog theo category tương ứng.
```

Căn cứ:

- Các category trong cùng combo có quan hệ sử dụng chung.
- Combo tạo tín hiệu mua kèm cho thuật toán association rules.
- Không làm mất tính đa dạng SKU vì không cố định sản phẩm cụ thể.

---

## 13. Rule số dòng hàng trong hóa đơn

Số dòng hàng phụ thuộc vào basket type và bối cảnh.

| Context | Số dòng thường gặp |
|---|---|
| Mua nhanh sáng | 1–3 dòng |
| Mua nhanh trưa | 1–3 dòng |
| Ngày thường | 2–5 dòng |
| Chiều tối ngày thường | 3–6 dòng |
| Cuối tuần | 3–8 dòng |
| Pre-Tết | 5–15 dòng |
| Ngày Tết | 1–4 dòng |
| Sau Tết | 1–4 dòng |
| Hóa phẩm/tẩy rửa | 1–4 dòng |
| Chăm sóc cá nhân | 1–3 dòng |
| Chăm sóc bé | 2–5 dòng |

Nguyên tắc:

```text
Không dùng một phân bố số dòng duy nhất cho mọi hóa đơn.
Basket type quyết định số dòng hợp lý.
```

Ví dụ:

- `quick_breakfast`: 1–3 dòng.
- `family_dinner`: 3–6 dòng.
- `weekend_family`: 4–8 dòng.
- `tet_stockup`: 6–15 dòng.
- `cleaning_household`: 2–4 dòng.

---

## 14. Rule quantity theo category

Quantity phải phụ thuộc vào loại category và đơn vị bán trong bảng product.

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

Nguyên tắc:

```text
Hàng đóng gói dùng quantity số nguyên.
Hàng cân ký có thể dùng quantity thập phân.
Không sinh quantity bằng 0 hoặc âm.
Không sinh quantity phi thực tế so với category.
```

---

## 15. Rule không bỏ rơi category ít phổ biến

Mọi category hợp lệ đều phải có cơ hội xuất hiện.

Rule:

```text
base_weight thấp không có nghĩa là bằng 0.
```

Ví dụ:

- Điện gia dụng: xác suất rất thấp, nhưng vẫn có thể xuất hiện.
- Đồ dùng gia đình: thấp, tăng nhẹ cuối tuần hoặc dịp dọn nhà.
- Văn phòng phẩm/đồ chơi: thấp, tăng vào tựu trường và 1-6.
- Mỹ phẩm/chăm sóc da: thấp đến trung bình, xuất hiện theo basket personal care.
- Bình xịt côn trùng: thấp, tăng nhẹ mùa nồm/ẩm/nóng.

Chỉ loại category/SKU nếu:

- Sản phẩm thiếu tên.
- Sản phẩm thiếu giá hợp lệ.
- Sản phẩm không map được category.
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
| Category Tết | Bánh kẹo, hạt, bia, nước ngọt, trà, gia vị tăng trong Pre-Tết |
| Category nồm ẩm | Lau sàn, tẩy rửa, nước giặt, nước xả, khăn giấy tăng T2–T3 |
| Category sáng | Bánh mì, sữa, cà phê tăng trong 06:30–08:30 |
| Category chiều tối | Rau, thịt, trứng, gia vị tăng trong 17:00–19:30 |
| Cuối tuần | Basket dài hơn và nhóm gia đình tăng |
| Combo ăn sáng | Bánh mì thường đi cùng sữa/cà phê/sữa chua |
| Combo giặt xả | Nước giặt thường đi cùng nước xả |
| Combo Tết | Bánh kẹo/hạt/bia/nước ngọt/trà cùng xuất hiện nhiều hơn |
| Category ít phổ biến | Vẫn có xuất hiện nhưng tần suất thấp |

Nếu các check trên không đạt, cần chỉnh lại rule category/basket, không sửa bằng cách ép trực tiếp doanh thu hoặc tổng tiền.

---

## 18. Tóm tắt nguyên tắc bắt buộc

1. Rule sinh hóa đơn phải đi theo category WinMart, không theo vài SKU cụ thể.
2. Mọi SKU hợp lệ phải map được vào một nhóm nghiệp vụ.
3. Category ít phổ biến vẫn có base weight, không bị bỏ qua.
4. Thời gian trong ngày ảnh hưởng đến category được chọn.
5. Ngày trong tuần ảnh hưởng đến basket size và basket composition.
6. Mùa vụ và event ảnh hưởng đến category, không sửa trực tiếp tổng tiền.
7. Basket type phải được chọn trước khi chọn sản phẩm.
8. Combo phải theo category, không hardcode sản phẩm.
9. Quantity phải phụ thuộc category và đơn vị bán.
10. Mỗi hệ số phải có lý do và validation đi kèm.
