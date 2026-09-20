{{ config(materialized='table', schema='silver') }}
select store_id::bigint as id, store_id::text as source_code, 'Store ' || store_id::text as store_name,
       {{ run_fetch_columns() }}
from {{ ref('stg_transaction') }}
group by store_id
