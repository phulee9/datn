{{ config(materialized='incremental', unique_key=['business_date', 'store_id', 'product_id'], incremental_strategy='merge', schema='gold') }}
select receipt.receipt_date as business_date,
       receipt.store_id, receipt_item.product_id,
       product.sku, product.category,
       sum(receipt_item.quantity) as quantity,
       sum(receipt_item.line_total) as amount,
       max(receipt.dih_fetch_day) as dih_fetch_day,
       max(receipt.dih_fetch_month) as dih_fetch_month,
       max(receipt.dih_fetch_year) as dih_fetch_year
from {{ ref('fact_receipt') }} receipt
join {{ ref('fact_receipt_item') }} receipt_item on receipt_item.receipt_id = receipt.id
join {{ ref('dim_product') }} product on product.id = receipt_item.product_id
group by receipt.receipt_date, receipt.store_id, receipt_item.product_id, product.sku, product.category
