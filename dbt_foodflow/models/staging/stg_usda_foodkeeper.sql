with raw_source as (
    select * from {{ source('raw_data', 'raw_usda_foodkeeper') }}
)

select
    cast(item_id as integer) as item_id,
    trim(name) as item_name,
    trim(category) as food_category,
    cast(pantry_days as integer) as pantry_shelf_life_days,
    cast(refrigerate_days as integer) as refrigerate_shelf_life_days,
    trim(perishability_tier) as perishability_tier
from raw_source