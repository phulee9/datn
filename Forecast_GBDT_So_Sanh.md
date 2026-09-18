# LÝ THUYẾT CHI TIẾT: XGBOOST · LIGHTGBM · CATBOOST CHO FORECAST BÁN LẺ

> Tài liệu lý thuyết đầy đủ cho báo cáo tốt nghiệp. Mọi khẳng định kỹ thuật đều có trích dẫn tới bài báo gốc (paper) — không bịa. Đọc kèm notebook `notebooks/forecast_gbdt_benchmark.ipynb` và `Forecast_Flow.md`.

---

## Mục lục

1. [Đặt vấn đề và phạm vi](#1-đặt-vấn-đề-và-phạm-vi)
2. [Nền tảng chung: CART và Gradient Boosting](#2-nền-tảng-chung-cart-và-gradient-boosting)
3. [XGBoost — KDD 2016](#3-xgboost--kdd-2016)
4. [LightGBM — NeurIPS 2017](#4-lightgbm--neurips-2017)
5. [CatBoost — NeurIPS 2018](#5-catboost--neurips-2018)
6. [So sánh trực diện](#6-so-sánh-trực-diện)
7. [Ánh xạ vào bài toán forecast của đồ án](#7-ánh-xạ-vào-bài-toán-forecast-của-đồ-án)
8. [Tài liệu tham khảo (để trích dẫn trong báo cáo)](#8-tài-liệu-tham-khảo-để-trích-dẫn-trong-báo-cáo)

---

## 1. Đặt vấn đề và phạm vi

### 1.1. Bài toán forecast trong đồ án

Mỗi quan sát là một bộ `(date, store_id, sku, category, qty, promotion_flag)`. Mục tiêu là dự báo `qty` cho `horizon = 7` ngày tới của một `(store_id, sku)`.

Ba model đều là **học có giám sát trên bảng** (supervised tabular learning), không tự hiểu thứ tự thời gian. Vì vậy pipeline dùng chung `build_training_features()`:

```
lag_1, lag_7, lag_14, roll_mean_7, roll_std_7,
weekday, is_weekend, is_holiday, promotion_flag,
store_id, sku, category  →  target = qty
```

Mọi lag/rolling đều `shift(1)` để feature tại ngày *t* chỉ nhìn dữ liệu đến *t-1* — tránh **target leakage**.

### 1.2. Vì sao chọn đúng 3 model này?

Cả ba cùng họ **Gradient Boosted Decision Trees (GBDT)** theo Friedman (2001), nên khác nhau ở *cài đặt* chứ không phải *họ thuật toán*. So sánh chúng cho thấy trade-off thực tế giữa **regularization / tốc độ / xử lý category** — đúng mối quan tâm của bài toán nhiều cửa hàng × nhiều SKU.

Các họ khác (Prophet, SARIMA, DeepAR/LSTM, Transformer) khác bản chất và được loại ở giai đoạn MVP vì yêu cầu dữ liệu dài hoặc hạ tầng nặng hơn — xem `Forecast_Flow.md` §6.3.

---

## 2. Nền tảng chung: CART và Gradient Boosting

### 2.1. Cây CART

Cây hồi quy CART (Breiman và cộng sự, 1984) đệ quy chia không gian feature bằng các ngưỡng `feature < threshold`, mỗi lá trả về một giá trị hằng số (trung bình hoặc median của target trong lá). Một cây đơn lẻ có bias thấp nhưng variance cao — dễ overfit.

> Breiman, L., Friedman, J. H., Olshen, R. A., & Stone, C. J. *Classification and Regression Trees.* Wadsworth, 1984.

### 2.2. Gradient Boosting Machine — Friedman (2001, 2002)

Friedman đặt bài toán học như **tối ưu hàm trong không gian hàm** (functional gradient descent):

> Friedman, J. H. "Greedy Function Approximation: A Gradient Boosting Machine." *Annals of Statistics*, 29(5), 1189–1232, 2001. DOI: [10.1214/aos/1013203451](https://doi.org/10.1214/aos/1013203451)

> Friedman, J. H. "Stochastic Gradient Boosting." *Computational Statistics & Data Analysis*, 38(4), 367–378, 2002.

Khung thuật toán (đã đơn giản hóa):

1. Khởi tạo $F_0(x) = \arg\min_c \sum_i L(y_i, c)$.
2. Với $m = 1 \ldots M$:
   - Tính **pseudo-residual** (gradient âm của loss tại dự báo hiện tại):
     $$r_{im} = -\left.\frac{\partial L(y_i, F(x_i))}{\partial F(x_i)}\right|_{F=F_{m-1}}$$
     Với MSE thì $r_{im} = y_i - F_{m-1}(x_i)$; với MAE thì $r_{im} = \operatorname{sign}(y_i - F_{m-1}(x_i))$.
   - Fit cây hồi quy $h_m(x)$ vào $\{r_{im}\}$.
   - Cập nhật $F_m(x) = F_{m-1}(x) + \nu \cdot h_m(x)$, với $\nu$ là learning rate (shrinkage).
3. Trả về $F_M(x)$.

Bản **stochastic** (Friedman, 2002) thêm subsampling dòng/cột mỗi vòng boosting để giảm overfit — ý tưởng được cả ba model kế thừa qua `subsample`/`colsample`/`bagging`.

Ba model dưới đây đều **giữ khung này**, khác nhau ở cách xây cây, tính gain, xử lý category và tối ưu hệ thống.

---

## 3. XGBoost — KDD 2016

### 3.1. Bài báo gốc

> Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proceedings of KDD 2016*, 785–794. arXiv: [1603.02754](https://arxiv.org/abs/1603.02754) · Bản KDD: [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)

Đây là paper GBDT được trích dẫn nhiều nhất trong các cuộc thi Kaggle giai đoạn 2015–2018. Phần abstract nêu rõ ba đóng góp hệ thống: **sparsity-aware algorithm**, **weighted quantile sketch** cho approximate tree learning, và tối ưu **cache access / compression / sharding**.

### 3.2. Hàm mục tiêu có regularization (Section 2.2)

XGBoost tối thiểu hóa **regularized objective** thay vì chỉ loss:

$$\mathcal{L}^{(t)} = \sum_{i=1}^{n} l\!\left(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)\right) + \Omega(f_t)$$

$$\Omega(f) = \gamma T + \frac12 \lambda \|w\|_2^2 + \alpha \|w\|_1$$

- $T$: số lá, $w$: trọng số lá.
- $\gamma$: phạt số lá (khuyến khích cây đơn giản).
- $\lambda$ (reg_lambda, L2) và $\alpha$ (reg_alpha, L1): phạt trọng số lớn.

Đây là điểm khác GBDT truyền thống: regularization được **đưa vào objective một cách nguyên tắc**, không chỉ dựa vào early stopping hay giới hạn độ sâu. Báo cáo của bạn có thể trích: *Section 2.2, Regularized Learning Objective*.

### 3.3. Khai triển Taylor bậc 2 (Section 2.2)

Để tìm cây $f_t$ tối ưu, XGBoost khai triển loss đến bậc 2 tại $\hat{y}^{(t-1)}$:

$$\mathcal{L}^{(t)} \approx \sum_{i=1}^{n}\left[g_i f_t(x_i) + \tfrac12 h_i f_t(x_i)^2\right] + \Omega(f_t)$$

$$g_i = \partial_{\hat{y}^{(t-1)}} l(y_i,\hat{y}^{(t-1)}),\qquad h_i = \partial^2_{\hat{y}^{(t-1)}} l(y_i,\hat{y}^{(t-1)})$$

Nhờ có $h_i$ (hessian), gain khi tách nút được tính chính xác hơn GBDT chỉ dùng $g_i$:

$$\text{Gain} = \tfrac12\left[\frac{G_L^2}{H_L+\lambda}+\frac{G_R^2}{H_R+\lambda}-\frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right]-\gamma$$

với $G_L=\sum_{i\in L} g_i$, $H_L=\sum_{i\in L} h_i$ (tương tự cho nhánh phải). Công thức này là cơ sở cho mọi quyết định tách trong XGBoost.

### 3.4. Weighted Quantile Sketch cho approximate split finding (Section 3.2)

Thử mọi ngưỡng tách là $O(n)$ mỗi feature. XGBoost đề xuất **Weighted Quantile Sketch** — tìm tập ứng viên ngưỡng dựa trên phân phối **có trọng số theo $h_i$**, với thuật toán mergeable sketch (Algorithm 2 trong paper). Trên dữ liệu lớn, approximate algorithm cho tốc độ gần tuyến tính mà vẫn giữ accuracy.

### 3.5. Sparsity-aware split finding (Section 3.4)

Với feature thưa / thiếu giá trị, XGBoost học **default direction** tại mỗi nút: khi gặp NaN, cây tự chọn đi trái hay phải để tối đa gain. Không cần impute thủ công trước khi train.

### 3.6. Tối ưu hệ thống (Section 3–4)

- **Column block**: lưu dữ liệu theo cột đã sắp xếp để tái sử dụng.
- **Cache-aware access**: tối ưu truy cập bộ nhớ khi tính histogram/gradient.
- **Out-of-core / distributed**: block compression + sharding cho dữ liệu không vừa RAM.

Những tối ưu này giải thích vì sao XGBoost scale tốt dù chậm hơn LightGBM trên cùng workload dense.

### 3.7. Cách xây cây: level-wise

XGBoost mở rộng cây **theo tầng**: mỗi level được tách gần như đầy đủ trước khi xuống level tiếp theo. Cây cân bằng, ít overfit khi chuỗi ngắn — phù hợp làm **mốc GBDT kinh điển** trong đồ án.

### 3.8. Tham số chính trong notebook

| Tham số | Ý nghĩa | Giá trị |
|---|---|---|
| `n_estimators` | Số cây | 250 |
| `max_depth` | Độ sâu tối đa | 6 |
| `learning_rate` (eta) | Shrinkage $\nu$ | 0.05 |
| `subsample` / `colsample_bytree` | Lấy mẫu dòng/cột (stochastic GBM) | 0.9 |
| `reg_lambda` / `reg_alpha` | L2/L1 trong $\Omega$ | mặc định |
| `objective` | Loss | `reg:absoluteerror` (MAE) |
| Category | Encode thủ công | `CATEGORY_MAPS` shared với LightGBM |

---

## 4. LightGBM — NeurIPS 2017

### 4.1. Bài báo gốc

> Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*. Bản NeurIPS: [proceedings.neurips.cc/2017 — 6449f44a](https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html) · PDF: [neurips.cc/2017 — LightGBM (PDF)](https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf)

Abstract của paper nêu rõ: *existing GBDT implementations must scan all instances to estimate information gain* — LightGBM giải quyết bằng **GOSS** và **EFB**, tăng tốc tới **20×** với accuracy gần như không đổi.

### 4.2. Histogram-based learning

LightGBM rời rạc hóa mỗi feature liên tục thành tối đa `max_bin` bins (mặc định 255), sau đó chỉ thử tách tại ranh giới bins. Histogram lưu **tổng gradient/hessian mỗi bin**, giảm độ phức tạp từ $O(n)$ xuống $O(\text{bins})$ mỗi feature. Đây là nền tảng cho cả GOSS/EFB và leaf-wise growth.

> Chi tiết histogram được mô tả trong Section 3 của bản PDF NeurIPS 2017.

### 4.3. GOSS — Gradient-based One-Side Sampling (Section 4.1 trong paper)

Ý tưởng: mẫu có gradient lớn (đang sai nhiều) quan trọng hơn cho việc tính gain.

- Giữ **toàn bộ** mẫu có $|g_i|$ lớn (top $a$%).
- Lấy mẫu ngẫu nhiên $b$% từ nhóm $|g_i|$ nhỏ.
- Khi tính gain, **nhân trọng số bù** $\frac{1-a}{b}$ cho nhóm đã subsample.

Trích abstract: *"exclude a significant proportion of data instances with small gradients ... data instances with larger gradients play a more important role in the computation of information gain."*

Trong forecast bán lẻ, GOSS giúp LightGBM tập trung vào những ngày đang dự báo sai nhiều (ví dụ ngày khuyến mãi / lễ).

### 4.4. EFB — Exclusive Feature Bundling (Section 4.2)

Nhiều feature thưa hiếm khi cùng khác 0 (mutually exclusive). EFB bó các feature ít xung đột thành một feature duy nhất, giảm số feature phải duyệt. Paper chứng minh bài toán bundling tối ưu là **NP-hard** và đưa thuật toán tham lam (greedy) đạt xấp xỉ tốt.

Trong đồ án, feature dày (dense) nên EFB ít tác dụng, nhưng GOSS + histogram vẫn làm LightGBM **nhanh nhất**.

### 4.5. Leaf-wise tree growth (Section 3.1)

Khác XGBoost level-wise, LightGBM mỗi lần chỉ tách **một lá duy nhất có gain lớn nhất**, bất kể độ sâu:

```
Level-wise (XGBoost):          Leaf-wise (LightGBM):
      gốc                            gốc
     /    \                         /    \
    A      B                       A      B
   / \    / \                     / \
  C   D  E   F                   C   D
                                / \
                               E   F  ← luôn chọn lá gain max
```

- Ưu: giảm loss nhanh hơn với cùng số lá → **train nhanh, accuracy cao** khi dữ liệu đủ lớn.
- Nhược: cây có thể sâu, mất cân bằng → **dễ overfit** khi chuỗi ngắn.

Vì vậy notebook giới hạn `num_leaves=31` và `min_child_samples=20` để kìm leaf-wise — đúng khuyến nghị của paper và docs.

> Lưu ý: với `max_depth=6`, cây cân bằng tối đa có $2^6=64$ lá, nhưng ta giới hạn 31 để tránh overfit.

### 4.6. Tham số chính trong notebook

| Tham số | Ý nghĩa | Giá trị |
|---|---|---|
| `n_estimators` | Số cây | 250 |
| `num_leaves` | Số lá tối đa / cây | 31 |
| `max_depth` | Độ sâu tối đa (kìm leaf-wise) | 6 |
| `min_child_samples` | Mẫu tối thiểu / lá | 20 |
| `learning_rate` | Shrinkage | 0.05 |
| `objective` | Loss | `mae` |
| Category | Encode thủ công (shared) | `CATEGORY_MAPS` |

---

## 5. CatBoost — NeurIPS 2018

### 5.1. Bài báo gốc

> Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. "CatBoost: Unbiased Boosting with Categorical Features." *Advances in Neural Information Processing Systems 31 (NeurIPS 2018)*. arXiv: [1706.09516](https://arxiv.org/abs/1706.09516) · Bản NeurIPS: [proceedings.neurips.cc/2018 — 14491b75](https://proceedings.neurips.cc/paper_files/paper/2018/hash/14491b756b3a51daac41c2486327471-Abstract.html) · PDF: [neurips.cc/2018 — CatBoost (PDF)](https://proceedings.neurips.cc/paper_files/paper/2018/file/14491b756b3a51daac41c2486327471-Paper.pdf)

> Dorogush, A. V., Ershov, V., & Gulin, A. "CatBoost: Gradient Boosting with Categorical Features Support." *Workshop on ML Systems at NeurIPS 2017*. arXiv: [1810.11363](https://arxiv.org/abs/1810.11363) — bản workshop mô tả chi tiết ordered boosting.

Abstract NeurIPS 2018 nêu hai vấn đề CatBoost giải quyết: **prediction shift** (gradient bias do target leakage) và **xử lý categorical features** bằng ordered target statistics.

### 5.2. Vấn đề: target leakage khi encode category

Với `store_id`, `sku` là chuỗi, XGBoost/LightGBM phải gán số tùy ý (STORE_01→0, STORE_02→1) — tạo thứ tự giả. Nếu tính thống kê target theo category (mean qty theo sku) trên toàn bộ train rồi đưa vào feature, feature đã nhìn thấy target của chính dòng đó → leakage, overfit.

### 5.3. Ordered Target Statistics (Section 3.1, NeurIPS 2018)

CatBoost thay vì tính trên toàn bộ dữ liệu, tính theo **random permutation** $\sigma$:

$$\hat{x}_{\sigma_p,k} = \frac{\sum_{j < p,\; x_{\sigma_j,k}=x_{\sigma_p,k}} y_{\sigma_j} + a\cdot p}{\sum_{j < p,\; x_{\sigma_j,k}=x_{\sigma_p,k}} 1 + a}$$

- Chỉ dùng các dòng **trước** $p$ trong permutation.
- $a, p$ là prior làm mịn khi category hiếm.

Ý nghĩa: **không dòng nào được nhìn target của chính nó hoặc tương lai** → giảm leakage khi category nhiều mức (đúng trường hợp nhiều SKU/store).

### 5.4. Ordered Boosting — khắc phục prediction shift (Section 3.2)

GBDT truyền thống tính residual trên cùng dữ liệu vừa dùng để train cây → gradient **biased** (lạc quan giả). CatBoost đề xuất **Ordered Boosting**:

- Với mỗi permutation, train cây chỉ trên các dòng trước đó.
- Gradient của dòng $i$ được tính bằng model chỉ train trên dòng **trước** $i$.

Tốn kém hơn nhưng cho gradient **unbiased**, giảm overfit — đặc biệt khi nhiều category. Đây là đóng góp lý thuyết trung tâm của paper (xem Section 3, *"Prediction shift"*).

### 5.5. Cây đối xứng (Oblivious / Symmetric Trees)

CatBoost mặc định dùng oblivious trees: mọi nút ở cùng độ sâu dùng chung một feature và ngưỡng:

```
         feature A < 5 ?
        /              \
  feature B < 10 ?  feature B < 10 ?
    /      \          /      \
   lá1    lá2       lá3    lá4
```

Ưu: inference vector hóa rất nhanh, ít overfit. Nhược: kém linh hoạt hơn cây không đối xứng. Trong notebook `depth=6` điều khiển độ sâu oblivious tree.

### 5.6. Xử lý categorical native

```python
CatBoostRegressor(cat_features=['store_id', 'sku', 'category'])
```

Không cần `LabelEncoder`/`OneHotEncoder`. Trong notebook, CatBoost là model duy nhất nhận category native; XGBoost và LightGBM dùng chung bảng encode số để so sánh công bằng — đúng khuyến nghị của paper khi so sánh.

### 5.7. Tham số chính trong notebook

| Tham số | Ý nghĩa | Giá trị |
|---|---|---|
| `iterations` | Số cây | 250 |
| `depth` | Độ sâu oblivious tree | 6 |
| `learning_rate` | Shrinkage | 0.05 |
| `loss_function` | Loss | `MAE` |
| `cat_features` | Cột category native | `['store_id','sku','category']` |
| `random_seed` | Seed | 20260918 |

---

## 6. So sánh trực diện

### 6.1. Bảng tổng hợp

| Tiêu chí | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| **Paper gốc** | Chen & Guestrin, KDD 2016 — [arXiv:1603.02754](https://arxiv.org/abs/1603.02754) | Ke và cs., NeurIPS 2017 — [NeurIPS 2017](https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html) | Prokhorenkova và cs., NeurIPS 2018 — [arXiv:1706.09516](https://arxiv.org/abs/1706.09516) |
| Họ thuật toán | GBDT | GBDT | GBDT |
| Cách xây cây | Level-wise (theo tầng) | Leaf-wise (theo lá) | Oblivious + Ordered Boosting |
| Tìm ngưỡng tách | Weighted Quantile Sketch | Histogram (≤255 bins) | Histogram + Ordered TS |
| Tốc độ train | Trung bình | **Nhanh nhất** (GOSS+EFB+histogram) | Chậm nhất (ordered boosting) |
| RAM | Cao nhất | Thấp nhất | Trung bình |
| Xử lý category | Encode thủ công | Có hỗ trợ, không mạnh | **Native, mạnh nhất** |
| Chống overfit | L1/L2 ($\lambda,\alpha$) + $\gamma$ | `num_leaves` + `min_child_samples` | Ordered boosting + prior $a,p$ |
| Overfit khi chuỗi ngắn | Ít hơn | **Dễ nhất** nếu không giới hạn lá | Ít hơn |
| Cài trên Windows | Dễ | Cần `msvc-runtime` (đã fix) | Dễ |
| Vai trò trong đồ án | Mốc GBDT kinh điển | Ứng viên tốc độ | Ứng viên category |

### 6.2. Minh họa cùng một bài toán

Với 1000 dòng `(lag_7, store_id) → qty`:

- **XGBoost**: quantile sketch có trọng số $h_i$ → chọn ngưỡng `lag_7`, xây cây cân bằng theo tầng, phạt $\gamma,\lambda$.
- **LightGBM**: bin `lag_7` thành ~255 bins → histogram gradient/bin → luôn tách lá gain lớn nhất (leaf-wise) → nhanh nhất.
- **CatBoost**: permutation `store_id` → ordered TS → oblivious tree với ordered boosting → tận dụng category tốt nhất.

Kết quả đều là tập hợp cây cộng lại, nhưng **đường đi khác nhau** tạo trade-off tốc độ / category / overfit khác nhau.

### 6.3. Vì sao không thể nói trước model nào thắng?

Vì cả ba cùng họ GBDT, khác biệt là cài đặt chi tiết. Model thắng phụ thuộc vào tầm quan trọng của category, độ dài chuỗi, mức nhiễu và feature nào quan trọng nhất. Vì vậy đồ án **bắt buộc benchmark công bằng** thay vì chọn theo tên.

---

## 7. Ánh xạ vào bài toán forecast của đồ án

### 7.1. Pipeline chung (đã chạy trong notebook)

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

### 7.2. Kết quả thực chạy (synthetic data)

| Model | MAE trung bình | WAPE trung bình | train / fold |
|---|---:|---:|---:|
| **CatBoost** | **2.029** | **8.37%** | ~6.8s |
| XGBoost | 2.076 | 8.72% | ~0.85s |
| LightGBM | 2.097 | 8.82% | ~0.39s |
| Seasonal Naive | 3.252 | 13.42% | ~0s |

Diễn giải để trình bày:

1. **Cả 3 GBDT đều thắng Seasonal Naive** → có giá trị ML so với baseline đơn giản.
2. **CatBoost thắng nhẹ** → khớp kỳ vọng vì global model nhiều SKU/store, category quan trọng — đúng thế mạnh ordered TS / ordered boosting.
3. **LightGBM nhanh nhất** (~17× CatBoost) → lựa chọn thực tế khi scale lên hàng trăm SKU hoặc cần lặp hyperparameter nhanh.
4. Chênh lệch nhỏ (2.029 vs 2.076) → không tuyên bố CatBoost "luôn tốt nhất"; phải nói: *trên synthetic data này CatBoost tốt nhất; trên dữ liệu thật phải chạy lại*.

### 7.3. Quy tắc benchmark công bằng (bắt buộc)

1. Cùng file `sales_daily_synthetic.csv` (sau này cùng query PostgreSQL).
2. Cùng `build_training_features()`.
3. Cùng horizon 7 ngày, cùng 3 cutoffs.
4. Cùng metric MAE/WAPE — **không dùng MAPE** (nhiều ngày bán = 0 làm mẫu số 0; xem Hyndman & Koehler, 2006).
5. **Không random split** — phải rolling-origin theo thời gian (Tashman, 2000).
6. Recursive forecast: dự báo ngày *t+2* dùng dự báo ngày *t+1*, không dùng actual test.

### 7.4. Chuyển sang dữ liệu thật

```
Ảnh hóa đơn → Gemini Vision → receipts + receipt_items (PostgreSQL)
→ GROUP BY receipt_date, store_id, product_id → daily_sales
→ thay sales_daily_synthetic.csv bằng daily_sales thật
→ chạy lại cùng notebook → chốt model production
```

Feature engineering, backtest và API contract **không đổi**, chỉ thay nguồn dữ liệu.

---

## 8. Tài liệu tham khảo (để trích dẫn trong báo cáo)

### 8.1. Nền tảng — CART và GBDT

1. Breiman, L., Friedman, J. H., Olshen, R. A., & Stone, C. J. *Classification and Regression Trees.* Wadsworth, 1984.

2. Friedman, J. H. "Greedy Function Approximation: A Gradient Boosting Machine." *Annals of Statistics*, 29(5), 1189–1232, 2001. DOI: [10.1214/aos/1013203451](https://doi.org/10.1214/aos/1013203451) — bài gốc về Gradient Boosting; khung pseudo-residual và shrinkage.

3. Friedman, J. H. "Stochastic Gradient Boosting." *Computational Statistics & Data Analysis*, 38(4), 367–378, 2002. — subsampling cho GBDT.

### 8.2. XGBoost

4. Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proceedings of KDD 2016*, 785–794. arXiv: [1603.02754](https://arxiv.org/abs/1603.02754) · DOI: [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785) — regularized objective (§2.2), Taylor bậc 2, Weighted Quantile Sketch (§3.2, Alg. 2), sparsity-aware (§3.4), column block / cache-aware.

### 8.3. LightGBM

5. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." *Advances in NeurIPS 30*, 2017. Abstract: [NeurIPS 2017 — LightGBM](https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html) · PDF: [NeurIPS 2017 — LightGBM (PDF)](https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf) — histogram, leaf-wise (§3.1), GOSS (§4.1), EFB (§4.2), tăng tốc tới 20×.

### 8.4. CatBoost

6. Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. "CatBoost: Unbiased Boosting with Categorical Features." *Advances in NeurIPS 31*, 2018. arXiv: [1706.09516](https://arxiv.org/abs/1706.09516) · NeurIPS: [NeurIPS 2018 — CatBoost](https://proceedings.neurips.cc/paper_files/paper/2018/hash/14491b756b3a51daac41c2486327471-Abstract.html) · PDF: [NeurIPS 2018 — CatBoost (PDF)](https://proceedings.neurips.cc/paper_files/paper/2018/file/14491b756b3a51daac41c2486327471-Paper.pdf) — ordered target statistics (§3.1), ordered boosting / prediction shift (§3.2), oblivious trees.

7. Dorogush, A. V., Ershov, V., & Gulin, A. "CatBoost: Gradient Boosting with Categorical Features Support." *Workshop on ML Systems at NeurIPS 2017*. arXiv: [1810.11363](https://arxiv.org/abs/1810.11363) — bản workshop chi tiết về ordered boosting.

### 8.5. Metric và backtest cho forecast

8. Hyndman, R. J. & Koehler, A. B. "Another Look at Measures of Forecast Accuracy." *International Journal of Forecasting*, 22(4), 679–688, 2006. — vì sao dùng MAE/WAPE thay vì MAPE khi có target = 0; MASE.

9. Tashman, L. J. "Out-of-Sample Tests of Forecasting Accuracy: An Analysis and Review." *International Journal of Forecasting*, 16(4), 437–450, 2000. — cơ sở cho rolling-origin backtest.

### 8.6. Gợi ý trích dẫn nhanh cho slide

```
Gradient Boosting:  Friedman (Ann. Statist. 2001)
XGBoost:            Chen & Guestrin (KDD 2016) — arXiv:1603.02754
LightGBM:           Ke et al. (NeurIPS 2017)
CatBoost:           Prokhorenkova et al. (NeurIPS 2018) — arXiv:1706.09516
Metric/Backtest:    Hyndman & Koehler (2006); Tashman (2000)
```

---

## Phụ lục: Câu trả lời mẫu khi bảo vệ

**Hỏi: Ba model khác nhau bản chất không?**

> Không. Cả ba đều là GBDT theo Friedman (2001). Khác nhau ở cách xây cây (level-wise vs leaf-wise vs oblivious + ordered boosting), cách tìm ngưỡng tách (quantile sketch vs histogram), và cách xử lý category. Vì vậy phải benchmark trên cùng dữ liệu thay vì chọn theo tên.

**Hỏi: Vì sao CatBoost thắng trong notebook?**

> Vì notebook train global model cho 3 cửa hàng × 8 SKU, biến `store_id`/`sku`/`category` quan trọng. CatBoost xử lý category native bằng ordered target statistics và ordered boosting (Prokhorenkova et al., NeurIPS 2018) nên giảm leakage và tận dụng category tốt hơn. Trên dữ liệu thật phải chạy lại để khẳng định.

**Hỏi: Vì sao không dùng MAPE?**

> Vì nhiều ngày bán = 0 làm mẫu số MAPE = 0, metric không xác định (Hyndman & Koehler, 2006). Đồ án dùng MAE và WAPE, đều xác định với target 0.

**Hỏi: Vì sao LightGBM nhanh nhất?**

> Nhờ histogram binning + GOSS (giữ mẫu gradient lớn, subsample mẫu gradient nhỏ có bù trọng số) + EFB (Ke et al., NeurIPS 2017, §4.1–4.2) và leaf-wise growth (§3.1). Trong benchmark, LightGBM ~0.39s/fold so với CatBoost ~6.8s.

---

*Tài liệu này đi kèm `notebooks/forecast_gbdt_benchmark.ipynb` (đã execute, 18 cells, 0 error) và `data/forecast/sales_daily_synthetic.csv`. Khi có dữ liệu PostgreSQL thật, chạy lại cùng pipeline để chốt model production.*
