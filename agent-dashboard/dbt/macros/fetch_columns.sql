{% macro run_fetch_columns() %}
extract(day from current_date)::smallint as dih_fetch_day,
extract(month from current_date)::smallint as dih_fetch_month,
extract(year from current_date)::smallint as dih_fetch_year
{% endmacro %}
