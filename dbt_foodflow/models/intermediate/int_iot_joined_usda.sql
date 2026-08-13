with iot as (
    select * from {{ ref('stg_iot_events') }}
),

usda as (
    select * from {{ ref('stg_usda_foodkeeper') }}
)

select
    iot.event_id,
    iot.bin_id,
    iot.event_timestamp,
    cast(iot.event_timestamp as date) as waste_date,
    iot.food_category,
    iot.weight_grams,
    round(iot.weight_grams / 1000.0, 4) as weight_kg,
    iot.disposal_reason,
    usda.item_id,
    usda.item_name,
    coalesce(usda.perishability_tier, 'Unknown') as perishability_tier,
    coalesce(usda.refrigerate_shelf_life_days, 7) as refrigerate_shelf_life_days
from iot
left join usda 
  on lower(iot.food_category) = lower(usda.food_category)