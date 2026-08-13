with raw_source as (
    select * from {{ source('raw_data', 'raw_epa_baselines') }}
)

select
    trim(sector) as business_sector,
    cast(expected_daily_waste_kg as double) as expected_daily_waste_kg,
    cast(normal_variance_pct as double) as normal_variance_pct
from raw_source