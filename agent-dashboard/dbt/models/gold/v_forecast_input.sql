{{ config(materialized='view', schema='gold') }}
select business_date, store_id, product_id, sku, category, quantity,
       lag_1, lag_7, lag_14, rolling_mean_7, rolling_std_7, weekday, is_weekend
from {{ ref('mart_forecast_features') }}
where lag_1 is not null and lag_7 is not null and lag_14 is not null
  and rolling_mean_7 is not null and rolling_std_7 is not null
