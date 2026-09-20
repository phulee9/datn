select household_key, basket_id, day, product_id, quantity, sales_value, store_id,
       retail_disc, trans_time, week_no, coupon_disc, coupon_match_disc,
       dih_fetch_day, dih_fetch_month, dih_fetch_year
from {{ source('landing', 'transaction') }}
