select
    item_id,
    item_name,
    food_category,
    pantry_shelf_life_days,
    refrigerate_shelf_life_days,
    perishability_tier
from {{ ref('stg_usda_foodkeeper') }}