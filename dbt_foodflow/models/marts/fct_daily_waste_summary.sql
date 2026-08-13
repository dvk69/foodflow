select
    cast(waste_date as varchar) || '_' || lower(replace(food_category, ' ', '_')) as daily_waste_pk,
    waste_date,
    food_category,
    active_bins,
    total_daily_waste_kg,
    avg_bin_waste_kg,
    epa_benchmark_kg,
    is_sector_anomaly,
    cast(current_timestamp as timestamp) as mart_refreshed_at
from {{ ref('int_daily_waste_by_sector') }}