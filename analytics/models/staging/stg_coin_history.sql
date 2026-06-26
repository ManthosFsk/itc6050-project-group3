SELECT
    coin_id,
    date,
    price,
    market_cap,
    total_volume

FROM {{ source('raw', 'coin_history') }}