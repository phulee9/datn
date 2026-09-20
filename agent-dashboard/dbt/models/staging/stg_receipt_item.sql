select id, receipt_id, product_id, raw_item_name, quantity, unit_price, line_total,
       match_method, match_score, dih_fetch_day, dih_fetch_month, dih_fetch_year
from {{ source('landing', 'receipt_item') }}
