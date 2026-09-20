{{ config(materialized='table', schema='silver') }}
{% set seed_base_date = var('seed_base_date', '2024-10-11') %}
{% set top_stores = var('top_stores', 15) %}
{% set top_skus = var('top_skus', 150) %}
with ranked_stores as (
    select store_id
    from {{ ref('stg_transaction') }}
    group by store_id
    order by count(distinct basket_id) desc
    limit {{ top_stores }}
),
ranked_skus as (
    select product_id
    from {{ ref('stg_transaction') }}
    group by product_id
    order by sum(quantity) desc
    limit {{ top_skus }}
),
dunnhumby_receipts as (
    select
        'dunnhumby'::text as source_type,
        basket_id::text as source_receipt_id,
        store_id::bigint as store_id,
        date '{{ seed_base_date }}' + (day - 1) as receipt_date,
        sum(sales_value)::numeric(14,2) as total_amount,
        1.000::numeric(4,3) as confidence_score,
        jsonb_build_object('source', 'dunnhumby', 'basket_id', basket_id) as raw_json,
        {{ run_fetch_columns() }}
    from {{ ref('stg_transaction') }}
    where store_id in (select store_id from ranked_stores)
      and product_id in (select product_id from ranked_skus)
    group by basket_id, store_id, day
),
gemini_receipts as (
    select
        source_type, source_receipt_id, store_id, receipt_date, total_amount, confidence_score, raw_json,
        dih_fetch_day, dih_fetch_month, dih_fetch_year
    from {{ ref('stg_receipt') }}
    where status = 'confirmed' and source_type = 'gemini_upload' and receipt_date is not null
),
all_receipts as (
    select * from dunnhumby_receipts union all select * from gemini_receipts
)
select
    row_number() over (order by source_type, source_receipt_id)::bigint as id,
    case when source_type = 'gemini_upload' then source_receipt_id::bigint end as staging_receipt_id,
    store_id, source_type, source_receipt_id, receipt_date, total_amount, confidence_score, raw_json,
    dih_fetch_day, dih_fetch_month, dih_fetch_year
from all_receipts
