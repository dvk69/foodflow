with raw_source as (
    select * from {{ source('raw_data', 'raw_instacart_orders') }}
)

select
    cast(order_id as integer) as order_id,
    trim(user_id) as user_id,
    cast(add_to_cart_order as integer) as add_to_cart_order,
    cast(item_id as integer) as item_id,
    trim(item_name) as item_name,
    trim(category) as food_category
from raw_source