with daily_iot as (
    select
        waste_date,
        food_category,
        count(distinct bin_id) as active_bins,
        sum(weight_kg) as total_daily_waste_kg,
        avg(weight_kg) as avg_bin_waste_kg
    from {{ ref('int_iot_joined_usda') }}
    group by 1, 2
),

epa as (
    select * from {{ ref('stg_epa_baselines') }}
)

select
    daily.waste_date,
    daily.food_category,
    daily.active_bins,
    round(daily.total_daily_waste_kg, 2) as total_daily_waste_kg,
    round(daily.avg_bin_waste_kg, 2) as avg_bin_waste_kg,
    -- Default sector benchmark comparison (Grocery/Retail)
    coalesce(epa.expected_daily_waste_kg, 450.0) as epa_benchmark_kg,
    case 
        when daily.total_daily_waste_kg > (coalesce(epa.expected_daily_waste_kg, 450.0) * 1.20) 
        then true 
        else false 
    end as is_sector_anomaly
from daily_iot daily
left join epa 
  on epa.business_sector = 'Grocery/Retail'