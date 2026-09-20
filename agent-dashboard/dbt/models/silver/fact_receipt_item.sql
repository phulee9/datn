{{ config(materialized='table', schema='silver') }}
{% set top_stores = var('top_stores', 15) %}
{% set top_skus = var('top_skus', 150) %}
with ranked_stores as (
    select store_id from {{ ref('stg_transaction') }}
    group by store_id order by count(distinct basket_id) desc limit {{ top_stores }}
),
ranked_skus as (
    select product_id from {{ ref('stg_transaction') }}
    group by product_id order by sum(quantity) desc limit {{ top_skus }}
),
dunnhumby_items as (
    select receipt.id as receipt_id, transaction.product_id::bigint as product_id,
           transaction.product_id::text as raw_item_name, transaction.quantity,
           case when transaction.quantity <> 0 then (transaction.sales_value / transaction.quantity)::numeric(14,2) end as unit_price,
           transaction.sales_value as line_total,
           transaction.dih_fetch_day, transaction.dih_fetch_month, transaction.dih_fetch_year
    from {{ ref('stg_transaction') }} transaction
    join {{ ref('fact_receipt') }} receipt
      on receipt.source_type = 'dunnhumby' and receipt.source_receipt_id = transaction.basket_id::text
    where transaction.store_id in (select store_id from ranked_stores)
      and transaction.product_id in (select product_id from ranked_skus)
),
gemini_items as (
    select receipt.id as receipt_id, item.product_id, item.raw_item_name, item.quantity, item.unit_price, item.line_total,
           item.dih_fetch_day, item.dih_fetch_month, item.dih_fetch_year
    from {{ ref('stg_receipt_item') }} item
    join {{ ref('fact_receipt') }} receipt on receipt.staging_receipt_id = item.receipt_id
    where item.product_id is not null
),
all_items as (
    select * from dunnhumby_items union all select * from gemini_items
)
select row_number() over (order by receipt_id, raw_item_name)::bigint as id, *
from all_items
