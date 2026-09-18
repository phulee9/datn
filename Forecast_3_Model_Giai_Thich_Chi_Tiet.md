# 3 MODEL FORECAST GIẢI THÍCH CHI TIẾT CHO NGƯỜI MỚI

> Dành cho người chưa từng học Machine Learning. Mọi khái niệm đều giải thích từ đầu và có trích dẫn nguồn gốc lý thuyết cụ thể.

---

## Mục lục

1. [Bắt đầu từ đâu? Bài toán forecast là gì?](#1-bắt-đầu-từ-đâu-bài-toán-forecast-là-gì)
2. [Viên gạch chung: Cây quyết định](#2-viên-gạch-chung-cây-quyết-định-decision-tree)
3. [Nền tảng chung: Gradient Boosting](#3-nền-tảng-chung-gradient-boosting)
4. [XGBoost](#4-xgboost)
5. [LightGBM](#5-lightgbm)
6. [CatBoost](#6-catboost)
7. [So sánh trực diện 3 model](#7-so-sánh-trực-diện-3-model)
8. [Áp dụng vào đồ án forecast bán lẻ](#8-áp-dụng-vào-đồ-án-forecast-bán-lẻ)
9. [Tài liệu gốc để trích dẫn trong báo cáo](#9-tài-liệu-gốc-để-trích-dẫn-trong-báo-cáo)

---

## 1. Bắt đầu từ đâu? Bài toán forecast là gì?

### 1.1. Bài toán

Mỗi ngày, mỗi cửa hàng, mỗi sản phẩm có một con số bán ra:

```
2026-03-01 | STORE_01 | COCA_330 | 31 lon
2026-03-02 | STORE_01 | COCA_330 | 35 lon
2026-03-03 | STORE_01 | COCA_330 | 28 lon
...
```

Câu hỏi forecast: **dựa vào quá khứ, đoán 7 ngày tới mỗi ngày bán bao nhiêu?**

### 1.2. Vì sao không đoán bừa?

Cách đơn giản nhất là Seasonal Naive: "thứ Hai tuần sau bán bằng thứ Hai tuần này". Nếu model Machine Learning không thắng được cách đơn giản này thì nó vô dụng. Vì vậy đồ án luôn so model ML với baseline.

### 1.3. Vì sao 3 model này không đọc trực tiếp chuỗi ngày?

XGBoost, LightGBM, CatBoost đều là model **học từ bảng** (tabular), không phải model chuỗi thời gian chuyên biệt như Prophet hay LSTM. Chúng không tự hiểu "ngày hôm qua" hay "tuần trước" là gì.

Vì vậy ta phải **biến chuỗi thời gian thành bảng** bằng feature engineering:

| Feature | Ý nghĩa | Ví dụ cho ngày 2026-03-15 |
|---|---|---|
| `lag_1` | Bán hôm qua | `qty` ngày 2026-03-14 |
| `lag_7` | Bán cùng thứ tuần trước | `qty` ngày 2026-03-08 |
| `lag_14` | Bán cùng thứ 2 tuần trước | `qty` ngày 2026-03-01 |
| `roll_mean_7` | Trung bình 7 ngày trước | `mean(qty 7 ngày trước)` |
| `roll_std_7` | Độ biến động 7 ngày trước | `std(qty 7 ngày trước)` |
| `weekday` | Thứ trong tuần (0-6) | 6 = Chủ nhật |
| `is_weekend` | Có phải cuối tuần | 0 hoặc 1 |
| `promotion_flag` | Có khuyến mãi | 0 hoặc 1 |
| `store_id`, `sku`, `category` | Cửa hàng / sản phẩm | STORE_01, COCA_330 |

> Quy tắc quan trọng: mọi lag và rolling đều phải `shift(1)` trước khi tính. Tức là feature của ngày *t* chỉ được nhìn dữ liệu đến ngày *t-1*. Nếu không shift, model sẽ nhìn thấy đáp án của chính ngày cần dự báo — gọi là **target leakage**, làm metric đẹp giả tạo.

---

## 2. Viên gạch chung: Cây quyết định (Decision Tree)

### 2.1. Cây quyết định là gì?

Hãy tưởng tượng bạn là quản lý kho, muốn đoán hôm nay bán bao nhiêu lon Coca:

```
Hôm nay có khuyến mãi không?
├── Có  → Cuối tuần không?
│         ├── Có  → đoán 38 lon
│         └── Không → đoán 33 lon
└── Không → Hôm qua bán trên 30 không?
           ├── Có  → đoán 29 lon
           └── Không → đoán 24 lon
```

Đó chính là một **cây quyết định**: mỗi nút là một câu hỏi yes/no trên một feature, mỗi lá là một con số dự báo.

Nguồn gốc lý thuyết cây quyết định dạng này được hệ thống hóa trong Breiman và cộng sự, *Classification and Regression Trees (CART)*, 1984.

### 2.2. Điểm mạnh và điểm yếu của một cây đơn lẻ

- Mạnh: dễ hiểu, chạy nhanh, không cần chuẩn hóa dữ liệu.
- Yếu: một cây đơn lẻ rất dễ **overfit** (học thuộc lòng dữ liệu train) hoặc **underfit** (quá đơn giản).

Vì vậy người ta không dùng một cây, mà dùng **nhiều cây cộng lại** — đó là Boosting.

---

## 3. Nền tảng chung: Gradient Boosting

### 3.1. Ý tưởng trực quan

Gradient Boosting do Jerome Friedman đề xuất năm 1999-2001, bài báo gốc là:

> Friedman, J. H. "Greedy Function Approximation: A Gradient Boosting Machine." *Annals of Statistics*, 29(5), 2001.

Ý tưởng:

```
Cây 1: đoán thử → sai 5 lon
Cây 2: học để sửa 5 lon sai đó → vẫn sai 2 lon
Cây 3: học để sửa 2 lon còn lại → sai 0.5 lon
...
Dự báo cuối = Cây 1 + Cây 2 + Cây 3 + ...
```

Mỗi cây mới **không đoán lại từ đầu**, mà chỉ học phần **sai số còn lại** (residual/gradient) của tất cả cây trước đó.

### 3.2. Công thức tổng quát (đã đơn giản hóa)

Gọi $F_{m-1}(x)$ là dự báo sau $m-1$ cây, $y$ là giá trị thật.

1. Tính gradient (độ sai) tại mỗi điểm:

$$r_{i,m} = -\frac{\partial L(y_i, F_{m-1}(x_i))}{\partial F_{m-1}(x_i)}$$

Với loss MAE, $r$ chính là dấu của sai số. Với loss MSE, $r$ chính là $y_i - F_{m-1}(x_i)$.

2. Train cây mới $h_m(x)$ để dự báo $r_{i,m}$.

3. Cập nhật:

$$F_m(x) = F_{m-1}(x) + \nu \cdot h_m(x)$$

Trong đó $\nu$ (learning_rate, ví dụ 0.05) là bước học — nhỏ thì học chậm nhưng vững.

### 3.3. Vì sao gọi là "Gradient"?

Vì phần sai số được tính bằng **đạo hàm (gradient)** của hàm loss theo dự báo hiện tại. Thuật toán đi xuống theo hướng gradient giống như leo núi đi xuống dốc.

### 3.4. Ba model so sánh đều là Gradient Boosting trên cây

| Điểm chung | Giải thích |
|---|---|
| Họ thuật toán | Đều là GBDT (Gradient Boosted Decision Trees) |
| Input | Bảng feature (lag, rolling, calendar, category) |
| Output | Số lượng bán dự báo (regression) |
| Cần feature engineering | Có, không tự hiểu chuỗi thời gian |
| Train nhanh hơn Deep Learning | Có, phù hợp đồ án |

**Khác nhau ở: cách xây cây, cách xử lý biến phân loại, tốc độ, và mức overfit.**

---

## 4. XGBoost

### 4.1. Nguồn gốc

> Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proceedings of KDD 2016*. arXiv:1603.02754.

XGBoost (eXtreme Gradient Boosting) là bản GBDT được tối ưu mạnh về hiệu năng và khả năng scale. Đây là model thắng nhiều cuộc thi Kaggle nhất giai đoạn 2015-2018.

### 4.2. Ý tưởng cốt lõi

XGBoost giữ nguyên khung Gradient Boosting của Friedman, nhưng thêm 3 cải tiến lớn:

#### a) Hàm mục tiêu có regularization

Thay vì chỉ tối thiểu hóa sai số, XGBoost tối thiểu hóa:

$$\text{Obj} = \sum_{i=1}^{n} L(y_i, \hat{y}_i) + \sum_{k=1}^{K} \Omega(f_k)$$

$$\Omega(f) = \gamma T + \frac{1}{2}\lambda \|w\|^2 + \alpha \|w\|_1$$

Trong đó:
- $T$ = số lá của cây
- $w$ = trọng số (giá trị dự báo) tại mỗi lá
- $\gamma$ = phạt khi cây có nhiều lá (khuyến khích cây đơn giản)
- $\lambda$ (reg_lambda, L2) và $\alpha$ (reg_alpha, L1) = phạt trọng số lớn

Ý nghĩa: **cây phức tạp hoặc trọng số lớn sẽ bị phạt**. Điều này chống overfit một cách có nguyên tắc, không chỉ dựa vào early stopping.

Đây là điểm XGBoost nêu rõ trong Section 2.2 của bài báo KDD 2016.

#### b) Khai triển Taylor bậc 2

Khi tìm điểm tách tốt nhất, XGBoost dùng cả gradient ($g_i$) và hessian ($h_i$, đạo hàm bậc 2):

$$g_i = \frac{\partial L}{\partial \hat{y}_i}, \quad h_i = \frac{\partial^2 L}{\partial \hat{y}_i^2}$$

Gain khi tách một nút được tính xấp xỉ:

$$\text{Gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L+\lambda} + \frac{G_R^2}{H_R+\lambda} - \frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right] - \gamma$$

Trong đó $G_L, H_L$ là tổng gradient/hessian nhánh trái, $G_R, H_R$ là nhánh phải. Công thức này có trong Section 2.1-2.2 của bài báo.

Nhờ dùng hessian, XGBoost chọn điểm tách chính xác hơn GBDT truyền thống chỉ dùng gradient.

#### c) Tìm điểm tách gần đúng có trọng số (Weighted Quantile Sketch)

Với dữ liệu lớn, không thể thử mọi giá trị tách. XGBoost đề xuất thuật toán **Weighted Quantile Sketch** (Section 3.2, Algorithm 2 trong bài báo) để tìm các điểm tách ứng viên dựa trên phân phối có trọng số theo $h_i$ (hessian). Điều này giúp train nhanh trên dữ liệu lớn mà vẫn giữ độ chính xác.

#### d) Xử lý sparsity và thiếu dữ liệu

XGBoost học **hướng mặc định (default direction)** cho giá trị thiếu tại mỗi nút tách (Section 3.4). Khi gặp NaN, cây tự biết nên đi nhánh trái hay phải để tối ưu loss.

#### e) Cách xây cây: level-wise

```
        gốc
       /    \
     A        B        ← level 1 xây xong mới xuống
    / \      / \
   C   D    E   F      ← level 2
```

XGBoost mở rộng cây theo **tầng (level-wise)**: mỗi tầng được tách gần như đầy đủ trước khi xuống tầng tiếp theo. Cách này cân bằng, ít overfit hơn leaf-wise khi chuỗi ngắn.

### 4.3. Khi nào dùng XGBoost?

- Muốn một **baseline GBDT kinh điển**, tài liệu nhiều, hyperparameter chuẩn dễ tìm.
- Dữ liệu không quá lớn (vài nghìn đến vài trăm nghìn dòng).
- Cần giải thích regularization ($\lambda$, $\alpha$, $\gamma$) trong báo cáo.
- Trong đồ án: XGBoost là **mốc đối chiếu ổn định** cho LightGBM và CatBoost.

### 4.4. Hyperparameter quan trọng

| Tham số | Ý nghĩa | Giá trị khởi điểm trong notebook |
|---|---|---|
| `n_estimators` | Số cây | 250 |
| `max_depth` | Độ sâu tối đa | 6 |
| `learning_rate` (eta) | Bước học | 0.05 |
| `subsample` | Tỷ lệ dòng lấy mẫu mỗi cây | 0.9 |
| `colsample_bytree` | Tỷ lệ cột lấy mẫu mỗi cây | 0.9 |
| `reg_lambda`, `reg_alpha` | L2/L1 regularization | mặc định |
| `objective` | Hàm loss | `reg:absoluteerror` (MAE) |

---

## 5. LightGBM

### 5.1. Nguồn gốc

> Ke, G. và cộng sự. "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." *Advances in Neural Information Processing Systems (NeurIPS) 30*, 2017.

LightGBM do Microsoft Research phát triển, mục tiêu là **train nhanh hơn và tốn ít RAM hơn XGBoost** trên dữ liệu lớn.

### 5.2. Ý tưởng cốt lõi

LightGBM giữ khung GBDT nhưng thay đổi cách lưu dữ liệu và cách chọn lá để tách.

#### a) Histogram-based learning

Thay vì thử mọi giá trị tách như XGBoost truyền thống, LightGBM **rời rạc hóa (binning)** mỗi feature liên tục thành tối đa `max_bin` bins (mặc định 255):

```
Giá trị thật:  31.2, 31.8, 32.1, 33.5, 38.7, 39.2 ...
Bins:          [31-32), [32-34), [38-40) ...
Histogram:     đếm số mẫu + tổng gradient mỗi bin
```

Sau đó chỉ thử tách tại ranh giới bins. Điều này giảm độ phức tạp từ $O(n)$ xuống $O(\text{bins})$ mỗi feature.

Kỹ thuật histogram cho GBDT được đề cập trong nhiều công trình trước đó, nhưng LightGBM là một trong những implementation tối ưu nhất (Section 3 trong bài báo NeurIPS 2017).

#### b) Leaf-wise tree growth (khác XGBoost)

Đây là khác biệt lớn nhất:

```
XGBoost (level-wise):           LightGBM (leaf-wise):

        gốc                            gốc
       /    \                         /    \
     A        B                      A        B
    / \      / \                   / \
   C   D    E   F                C   D
                                 / \
                                E   F   ← luôn tách lá có gain lớn nhất
```

- **Level-wise (XGBoost)**: tách đều theo tầng, cây cân bằng.
- **Leaf-wise (LightGBM)**: mỗi lần chỉ tách **một lá duy nhất** — lá nào cho gain lớn nhất thì tách trước, bất kể nó ở tầng nào.

Hệ quả:
- Leaf-wise giảm loss nhanh hơn với cùng số lá → **train nhanh hơn, accuracy cao hơn** khi dữ liệu đủ lớn.
- Nhưng cây có thể rất sâu và mất cân bằng → **dễ overfit** khi dữ liệu ít hoặc chuỗi ngắn.

Vì vậy LightGBM khuyến nghị giới hạn `num_leaves` (ví dụ 31) và `min_child_samples` (ví dụ 20) để kìm overfit — đúng như notebook đang làm.

Nội dung leaf-wise được mô tả trong Section 3.1 của bài báo LightGBM.

#### c) GOSS — Gradient-based One-Side Sampling

Với dữ liệu lớn, LightGBM không dùng toàn bộ mẫu để tính gain. GOSS (Section 4.1 trong bài báo) làm như sau:

- Giữ lại tất cả mẫu có gradient lớn (tức là đang sai nhiều — cần học).
- Lấy mẫu ngẫu nhiên một phần mẫu có gradient nhỏ.
- Khi tính gain, nhân trọng số bù cho phần đã bỏ bớt.

Ý nghĩa: **tập trung học vào điểm đang sai**, bỏ bớt điểm đã đoán gần đúng → nhanh hơn mà ít mất accuracy.

#### d) EFB — Exclusive Feature Bundling

Nhiều feature thưa (sparse) hiếm khi cùng khác 0. EFB (Section 4.2) bó các feature ít xung đột thành một feature duy nhất → giảm số feature phải duyệt.

Trong đồ án forecast, EFB ít tác dụng vì feature dày (dense), nhưng GOSS và histogram vẫn giúp LightGBM nhanh nhất.

### 5.3. Khi nào dùng LightGBM?

- Dữ liệu lớn: nhiều cửa hàng × nhiều SKU × nhiều ngày.
- Cần **train nhanh, thử nhiều hyperparameter**.
- Là lựa chọn mặc định cho tabular/retail forecasting hiện nay.
- Trong đồ án: LightGBM là **ứng viên tốc độ**.

### 5.4. Hyperparameter quan trọng

| Tham số | Ý nghĩa | Giá trị trong notebook |
|---|---|---|
| `n_estimators` | Số cây | 250 |
| `num_leaves` | Số lá tối đa mỗi cây | 31 |
| `max_depth` | Độ sâu tối đa (kìm leaf-wise) | 6 |
| `min_child_samples` | Số mẫu tối thiểu mỗi lá | 20 |
| `learning_rate` | Bước học | 0.05 |
| `objective` | Hàm loss | `mae` |

> Lưu ý: trong LightGBM, `num_leaves` quan trọng hơn `max_depth`. Với `max_depth=6`, số lá tối đa của cây cân bằng là $2^6 = 64$, nhưng ta giới hạn 31 để tránh overfit.

---

## 6. CatBoost

### 6.1. Nguồn gốc

> Prokhorenkova, L. và cộng sự. "CatBoost: Unbiased Boosting with Categorical Features." *Advances in Neural Information Processing Systems (NeurIPS) 31*, 2018. arXiv:1706.09516 và arXiv:1808.06863.

CatBoost (Categorical Boosting) do Yandex phát triển, mục tiêu là **xử lý biến phân loại (categorical) tốt hơn** và giảm hiện tượng **target leakage** khi encode category.

### 6.2. Vấn đề CatBoost giải quyết

Trong forecast bán lẻ, các biến như `store_id`, `sku`, `category` là chuỗi ký tự, không phải số. XGBoost/LightGBM cần **encode thủ công** (ví dụ gán STORE_01→0, STORE_02→1). Cách encode này có 2 vấn đề:

1. Gán số tùy ý tạo ra thứ tự giả (STORE_02 > STORE_01 không có ý nghĩa).
2. Nếu tính target statistics (trung bình `qty` theo `sku`) trên toàn bộ train rồi đưa vào feature → **leakage**: feature đã nhìn thấy target của chính dòng đó.

CatBoost sinh ra để giải quyết cả hai.

### 6.3. Ý tưởng cốt lõi

#### a) Ordered Target Statistics

Thay vì tính trung bình target theo category trên toàn bộ dữ liệu, CatBoost tính theo **thứ tự ngẫu nhiên (random permutation)**:

```
Permutation 1: dòng 3 chỉ được nhìn dòng 1,2 để tính trung bình sku
Permutation 2: dòng 1 chỉ được nhìn dòng 5,7 ...
```

Công thức (Section 3.1 trong bài báo NeurIPS 2018):

$$\hat{x}_{i,k} = \frac{\sum_{j < i, \, x_{j,k} = x_{i,k}} y_j + a \cdot p}{\sum_{j < i, \, x_{j,k} = x_{i,k}} 1 + a}$$

Trong đó:
- $x_{i,k}$ là giá trị category $k$ tại dòng $i$
- Chỉ tính trên các dòng **trước** $i$ trong permutation
- $a, p$ là prior (làm mịn khi category hiếm)

Ý nghĩa: **không dòng nào được nhìn target của chính nó hoặc tương lai** → giảm leakage và overfit trên category nhiều mức.

#### b) Ordered Boosting

GBDT truyền thống tính gradient (residual) trên cùng dữ liệu vừa dùng để train cây → gradient bị **biased** (lạc quan giả). CatBoost đề xuất **Ordered Boosting** (Section 3.2):

- Với mỗi permutation, train cây chỉ trên các dòng trước đó.
- Gradient của dòng $i$ được tính bằng model chỉ train trên dòng trước $i$.

Điều này tốn kém hơn nhưng cho gradient **unbiased**, giảm overfit — đặc biệt khi có nhiều category.

#### c) Xử lý categorical native

CatBoost nhận trực tiếp cột dạng chuỗi:

```python
CatBoostRegressor(cat_features=['store_id', 'sku', 'category'])
```

Không cần `LabelEncoder` hay `OneHotEncoder` thủ công. Trong notebook, CatBoost là model duy nhất nhận category native; XGBoost và LightGBM dùng cùng một bảng encode số để so sánh công bằng.

#### d) Cây đối xứng (Symmetric / Oblivious Trees)

CatBoost mặc định dùng **oblivious trees**: mọi nút ở cùng độ sâu dùng chung một feature và ngưỡng tách. Cây trông như:

```
        feature A < 5 ?
       /              \
  feature B < 10 ?  feature B < 10 ?
   /      \          /      \
  lá1    lá2       lá3    lá4
```

Ưu điểm: inference rất nhanh (có thể vector hóa), ít overfit. Nhược điểm: kém linh hoạt hơn cây6978 không đối xứng.

Trong notebook ta dùng `depth=6` (tương đương độ sâu cây), CatBoost sẽ tự chọn cấu trúc oblivious phù hợp.

### 6.4. Khi nào dùng CatBoost?

- Train **một global model cho nhiều cửa hàng và nhiều SKU** (category nhiều mức).
- Muốn **giảm công encode** và giảm leakage do category.
- Chấp nhận train chậm hơn LightGBM để đổi lấy xử lý category tốt hơn.
- Trong đồ án: CatBoost là **ứng viên category** — đúng như kết quả benchmark synthetic data cho thấy CatBoost thắng nhẹ (MAE 2.029 vs 2.076 vs 2.097).

### 6.5. Hyperparameter quan trọng

| Tham số | Ý nghĩa | Giá trị trong notebook |
|---|---|---|
| `iterations` | Số cây (tương đương n_estimators) | 250 |
| `depth` | Độ sâu cây oblivious | 6 |
| `learning_rate` | Bước học | 0.05 |
| `loss_function` | Hàm loss | `MAE` |
| `cat_features` | Danh sách cột category native | `['store_id','sku','category']` |
| `random_seed` | Seed | 20260918 |

---

## 7. So sánh trực diện 3 model

### 7.1. Bảng tổng hợp

| Tiêu chí | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| **Bài báo gốc** | Chen & Guestrin, KDD 2016 | Ke và cs., NeurIPS 2017 | Prokhorenkova và cs., NeurIPS 2018 |
| **Họ thuật toán** | GBDT | GBDT | GBDT |
| **Cách xây cây** | Level-wise (theo tầng) | Leaf-wise (theo lá) | Oblivious + Ordered Boosting |
| **Tìm điểm tách** | Weighted Quantile Sketch + exact/greedy | Histogram binning (max 255 bins) | Histogram + Ordered TS |
| **Tốc độ train** | Trung bình | **Nhanh nhất** | Chậm nhất (do ordered boosting) |
| **RAM** | Cao nhất | Thấp nhất | Trung bình |
| **Xử lý category** | Encode thủ công | Có hỗ trợ, nhưng không mạnh | **Native, mạnh nhất** |
| **Chống overfit** | L1/L2 + gamma | num_leaves + min_child_samples | Ordered boosting + prior |
| **Overfit khi chuỗi ngắn** | Ít hơn | **Dễ nhất** nếu không giới hạn lá | Ít hơn |
| **Cài trên Windows** | Dễ | Cần `msvc-runtime` (đã fix trong notebook) | Dễ |
| **Tài liệu Python** | Rất nhiều | Nhiều | Nhiều |
| **1 SKU / 1 cửa hàng** | Tốt | Tốt | Không nổi trội |
| **Nhiều SKU chung 1 model** | Tốt | Tốt | **Tốt nhất** |
| **Vai trò trong đồ án** | Mốc GBDT kinh điển | Ứng viên tốc độ | Ứng viên category |

### 7.2. Cùng một bài toán, khác cách tách cây

Giả sử có 1000 dòng train, mỗi dòng có `lag_7` và `store_id`:

- **XGBoost** sẽ thử các ngưỡng `lag_7` dựa trên quantile có trọng số hessian, xây cây cân bằng theo tầng.
- **LightGBM** sẽ bin `lag_7` thành ~255 bins, tính histogram gradient mỗi bin, rồi luôn tách lá có gain lớn nhất.
- **CatBoost** sẽ permutation `store_id`, tính ordered target statistics cho `store_id`, rồi xây cây oblivious với ordered boosting.

Kết quả cuối cùng đều là một tập hợp cây cộng lại, nhưng **đường đi khác nhau** dẫn đến trade-off tốc độ/category/overfit khác nhau.

### 7.3. Vì sao không thể nói trước model nào thắng?

Vì cả ba đều là GBDT, khác biệt không phải bản chất thuật toán mà là **cài đặt chi tiết**. Model thắng phụ thuộc vào:

- Số lượng category và mức độ quan trọng của chúng.
- Độ dài chuỗi và mức nhiễu.
- Cách tạo feature (lag/rolling nào quan trọng nhất).

Vì vậy đồ án **bắt buộc benchmark công bằng** thay vì chọn theo tên.

---

## 8. Áp dụng vào đồ án forecast bán lẻ

### 8.1. Pipeline chung (đã implement trong notebook)

```
sales_daily_synthetic.csv (5.040 dòng: 3 store × 8 SKU × 210 ngày)
        ↓
build_training_features() — shift(1), lag_1/7/14, roll_mean/std, calendar
        ↓
Rolling-origin backtest: 3 folds × horizon 7 ngày, recursive forecast
        ↓
┌───────────────┬───────────────┬───────────────┐
│   XGBoost     │   LightGBM    │   CatBoost    │
│ (encode số)   │ (encode số)   │ (native cat)  │
└───────────────┴───────────────┴───────────────┘
        ↓
MAE / WAPE / train_seconds mỗi fold
        ↓
Chọn model có MAE trung bình thấp nhất
        ↓
Retrain trên toàn bộ lịch sử → forecast 7 ngày → JSON API
```

### 8.2. Kết quả trên synthetic data (đã chạy)

| Model | MAE trung bình | WAPE trung bình | train_seconds/fold |
|---|---|---:|---:|
| **CatBoost** | **2.029** | **8.37%** | ~6.8s |
| XGBoost | 2.076 | 8.72% | ~0.85s |
| LightGBM | 2.097 | 8.82% | ~0.39s |
| Seasonal Naive | 3.252 | 13.42% | ~0s |

Nhận xét để trình bày:

1. **Cả 3 GBDT đều thắng Seasonal Naive** → có giá trị ML.
2. **CatBoost thắng nhẹ** → phù hợp kỳ vọng vì global model nhiều SKU/store, category quan trọng.
3. **LightGBM nhanh nhất** (gấp ~17 lần CatBoost) → nếu cần train nhanh hoặc scale lên hàng trăm SKU thì LightGBM là lựa chọn thực tế.
4. **Chênh lệch nhỏ** (2.029 vs 2.076) → không nên tuyên bố CatBoost "luôn tốt nhất". Phải nói: *trên synthetic data này, CatBoost tốt nhất; trên dữ liệu thật phải chạy lại*.

### 8.3. Quy tắc benchmark công bằng (bắt buộc)

1. Cùng file `sales_daily_synthetic.csv` (hoặc cùng query PostgreSQL sau này).
2. Cùng bộ feature từ `build_training_features()`.
3. Cùng horizon 7 ngày, cùng 3 cutoffs.
4. Cùng metric MAE/WAPE, **không dùng MAPE** (nhiều ngày bán = 0 làm mẫu số 0).
5. **Không random split** — phải rolling-origin theo thời gian.
6. Recursive forecast: dự báo ngày t+2 dùng dự báo ngày t+1, không dùng actual test.

### 8.4. Chuyển sang dữ liệu thật

Khi ingestion hoàn thiện:

```
Ảnh hóa đơn → Gemini Vision → receipts + receipt_items (PostgreSQL)
→ GROUP BY receipt_date, store_id, product_id → daily_sales
→ thay sales_daily_synthetic.csv bằng daily_sales thật
→ chạy lại cùng notebook → chốt model production
```

Feature engineering, backtest và API contract **không đổi**, chỉ thay nguồn dữ liệu.

---

## 9. Tài liệu gốc để trích dẫn trong báo cáo

> Dùng đúng các nguồn dưới đây trong phần Tài liệu tham khảo. Không bịa tên bài báo.

### 9.1. Nền tảng

1. Breiman, L., Friedman, J. H., Olshen, R. A., & Stone, C. J. *Classification and Regression Trees (CART).* Wadsworth, 1984. — Nguồn gốc cây CART.

2. Friedman, J. H. "Greedy Function Approximation: A Gradient Boosting Machine." *Annals of Statistics*, 29(5), 1189–1232, 2001. — Bài báo gốc về Gradient Boosting.

3. Friedman, J. H. "Stochastic Gradient Boosting." *Computational Statistics & Data Analysis*, 38(4), 367–378, 2002. — Bổ sung subsampling cho GBDT.

### 9.2. XGBoost

4. Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD)*, 785–794, 2016. arXiv:1603.02754.

### 9.3. LightGBM

5. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." *Advances in Neural Information Processing Systems (NeurIPS) 30*, 2017.

### 9.4. CatBoost

6. Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. "CatBoost: Unbiased Boosting with Categorical Features." *Advances in Neural Information Processing Systems (NeurIPS) 31*, 2018. arXiv:1706.09516.

7. Dorogush, A. V., Ershov, V., & Gulin, A. "CatBoost: Gradient Boosting with Categorical Features Support." Workshop on ML Systems at NeurIPS 2017. arXiv:1810.11363. — Bản workshop mô tả chi tiết ordered boosting.

### 9.5. Đánh giá forecast

8. Hyndman, R. J. & Koehler, A. B. "Another Look at Measures of Forecast Accuracy." *International Journal of Forecasting*, 22(4), 679–688, 2006. — Lý do dùng MAE/WAPE thay vì MAPE, và MASE.

9. Tashman, L. J. "Out-of-Sample Tests of Forecasting Accuracy: An Analysis and Review." *International Journal of Forecasting*, 16(4), 437–450, 2000. — Cơ sở cho rolling-origin backtest.

### 9.6. Gợi ý trích dẫn trong slide

```text
- Gradient Boosting: Friedman (2001)
- XGBoost: Chen & Guestrin (KDD 2016)
- LightGBM: Ke et al. (NeurIPS 2017)
- CatBoost: Prokhorenkova et al. (NeurIPS 2018)
- Metric/Backtest: Hyndman & Koehler (2006), Tashman (2000)
```

---

## 10. Câu trả lời mẫu khi bảo vệ

**Hỏi: Ba model khác nhau bản chất không?**

> Không. Cả ba đều là Gradient Boosted Decision Trees theo Friedman (2001). Khác nhau ở cách xây cây (level-wise vs leaf-wise vs ordered boosting), cách xử lý biến phân loại, và tối ưu tốc độ/bộ nhớ. Vì vậy phải benchmark trên cùng dữ liệu thay vì chọn theo tên.

**Hỏi: Vì sao CatBoost thắng trong notebook?**

> Vì notebook train global model cho 3 cửa hàng × 8 SKU, biến `store_id`/`sku`/`category` quan trọng. CatBoost xử lý category native bằng ordered target statistics và ordered boosting (Prokhorenkova et al., NeurIPS 2018) nên giảm leakage và tận dụng category tốt hơn. Trên dữ liệu thật phải chạy lại để khẳng định.

**Hỏi: Vì sao không dùng MAPE?**

> Vì nhiều ngày bán bằng 0 làm mẫu số MAPE bằng 0, metric không xác định (Hyndman & Koehler, 2006). Đồ án dùng MAE và WAPE, đều xác định với target 0.

**Hỏi: Vì sao không random split train/test?**

> Vì dữ liệu thời gian có thứ tự. Random split làm train nhìn thấy tương lai, kết quả không thật (Tashman, 2000). Đồ án dùng rolling-origin backtest: train đến cutoff, forecast 7 ngày tiếp theo, lặp 3 lần.

---

*Tài liệu này đi kèm notebook `notebooks/forecast_gbdt_benchmark.ipynb` (đã execute) và `data/forecast/sales_daily_synthetic.csv`. Khi có dữ liệu PostgreSQL thật, chạy lại cùng pipeline để chốt model production.*
