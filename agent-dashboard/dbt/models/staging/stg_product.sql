select product_id, department, commodity_desc, sub_commodity_desc, manufacturer, brand,
       curr_size_of_product, dih_fetch_day, dih_fetch_month, dih_fetch_year
from {{ source('landing', 'product') }}
