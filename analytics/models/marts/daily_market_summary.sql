WITH all_coins AS (

    SELECT
        CAST(last_updated AS DATE) AS date,
        name,
        market_cap,
        total_volume
    FROM {{ ref('stg_coins') }}

),

top10 AS (

    SELECT
        CAST(last_updated AS DATE) AS date,
        price_change_percentage_24h
    FROM {{ ref('stg_coins') }}
    WHERE market_cap_rank <= 10

),

market_summary AS (

    SELECT

        date,

        SUM(market_cap) AS total_market_cap,

        (
            ARRAY_AGG(name ORDER BY total_volume DESC)
        )[1] AS top_coin_by_volume

    FROM all_coins

    GROUP BY date

),

price_change AS (

    SELECT

        date,

        AVG(price_change_percentage_24h) AS avg_price_change_top10

    FROM top10

    GROUP BY date

)

SELECT

    m.date,
    m.total_market_cap,
    m.top_coin_by_volume,
    p.avg_price_change_top10

FROM market_summary m

JOIN price_change p
USING (date)