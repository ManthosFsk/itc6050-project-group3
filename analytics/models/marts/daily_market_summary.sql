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
        (ARRAY_AGG(name ORDER BY total_volume DESC))[1] AS top_coin_by_volume
    FROM all_coins
    GROUP BY date

),

price_change AS (

    SELECT
        date,
        AVG(price_change_percentage_24h) AS avg_price_change_top10
    FROM top10
    GROUP BY date

),

-- 7-day rolling average price per coin
rolling_avg AS (

    SELECT
        coin_id,
        date,
        price,
        AVG(price) OVER (
            PARTITION BY coin_id
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS price_7d_rolling_avg
    FROM {{ ref('stg_coin_history') }}

),

-- Volatility: std dev of daily price change per coin (last 90 days)
volatility AS (

    SELECT
        coin_id,
        STDDEV(price) AS volatility_score,
        AVG(price) AS avg_price_90d