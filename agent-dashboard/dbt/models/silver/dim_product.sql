{{ config(materialized='table', schema='silver') }}
select product_id::bigint as id, product_id::text as sku,
       coalesce(nullif(trim(concat_ws(' ', nullif(brand, ''), nullif(sub_commodity_desc, ''), nullif(curr_size_of_product, ''))), ''), commodity_desc) as display_name,
       commodity_desc as category, brand, curr_size_of_product as product_size,
       {{ run_fetch_columns() }}
from {{ ref('stg_product') }}
