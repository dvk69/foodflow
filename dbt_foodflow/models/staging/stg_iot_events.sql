with raw_source as (
    select * from {{ source('raw_data', 'raw_iot_events') }}
),

cleaned as (
    select
        event_id,
        bin_id,
        cast(timestamp as timestamp) as event_timestamp,
        trim(food_category) as food_category,
        -- Replace negative or null weights with 0.0 for safety
        case 
            when weight_grams is null or weight_grams < 0 then 0.0
            else round(cast(weight_grams as double), 2)
        end as weight_grams,
        trim(disposal_reason) as disposal_reason,
        cast(_ingested_at as timestamp) as ingested_at,
        -- Deduplication logic across duplicate network retries
        row_number() over (
            partition by event_id 
            order by _ingested_at desc
        ) as dedup_idx
    from raw_source
)

select
    event_id,
    bin_id,
    event_timestamp,
    food_category,
    weight_grams,
    disposal_reason,
    ingested_at
from cleaned
where dedup_idx = 1
  -- Filter out future timestamps (sensor clock drift defect)
  and event_timestamp <= cast(current_timestamp as timestamp)