select id, image_hash, image_uri, source_type, source_receipt_id, store_id, store_name_guess,
       receipt_date, total_amount, confidence_score, status, raw_json, error_message, assigned_to,
       dih_fetch_day, dih_fetch_month, dih_fetch_year
from {{ source('landing', 'receipt') }}
