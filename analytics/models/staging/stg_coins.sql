WITH source AS (

    SELECT *
    FROM {{ source('raw', 'coins') }}

),

renamed AS (

    SELECT

        id,
        symbol,
        name,
        image,
        current_price,
        market_cap,
        RANK() OVER (ORDER BY market_cap DESC) AS market_cap_rank,
        total_volume,
        CAST(last_updated AS TIMESTAMP) AS last_updated,
        price_change_24h,
        price_change_percentage_24h

    FROM source

    WHERE current_price > 0

)

SELECT *
FROM renamed