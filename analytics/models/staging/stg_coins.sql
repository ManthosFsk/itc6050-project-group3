WITH source AS (

    SELECT *
    FROM {{ source('raw', 'coins') }}

),

renamed AS (

    SELECT

        id,
        symbol,
        name,
        current_price,
        market_cap,
        market_cap_rank,
        total_volume,
        CAST(last_updated AS TIMESTAMP) AS last_updated,
        price_change_percentage_24h

    FROM source

    WHERE current_price IS NOT NULL

)

SELECT *
FROM renamed