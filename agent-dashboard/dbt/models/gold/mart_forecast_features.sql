{{ config(materialized='incremental', unique_key=['business_date', 'store_id', 'product_id'], incremental_strategy='merge', schema='gold') }}
with daily as (
    select business_date, store_id, product_id, sku, category, sum(quantity) as quantity
    from {{ ref('mart_daily_sales') }} group by 1,2,3,4,5
),
series as (
    select store_id, product_id, max(sku) as sku, max(category) as category, min(business_date) as start_date, max(business_date) as end_date
    from daily group by store_id, product_id
),
calendar as (
    select store_id, product_id, sku, category, business_date
    from series
    cross join lateral generate_series(start_date, end_date, interval '1 day')::date as business_date
),
dense as (
    select c.business_date, c.store_id, c.product_id, c.sku, c.category, coalesce(d.quantity,0) as quantity
    from calendar c left join daily d on d.business_date=c.business_date and d.store_id=c.store_id and d.product_id=c.product_id
)
select business_date, store_id, product_id, sku, category, quantity,
       lag(quantity,1) over (partition by store_id, product_id order by business_date) as lag_1,
       lag(quantity,7) over (partition by store_id, product_id order by business_date) as lag_7,
       lag(quantity,14) over (partition by store_id, product_id order by business_date) as lag_14,
       avg(quantity) over (partition by store_id, product_id order by business_date rows between 7 preceding and 1 preceding) as rolling_mean_7,
       stddev_samp(quantity) over (partition by store_id, product_id order by business_date rows between 7 preceding and 1 preceding) as rolling_std_7,
       extract(dow from business_date)::smallint as weekday,
       case when extract(dow from business_date) in (0,6) then 1 else 0 end::smallint as is_weekend,
       {{ run_fetch_columns() }}
from dense
