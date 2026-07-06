WITH history_with_rank AS (

    SELECT
        h.coin_id,
        h.date,
        h.price,
        h.market_cap,
        h.total_volume,
        RANK() OVER (
            PARTITION BY h.date
            ORDER BY h.market_cap DESC
        ) AS market_cap_rank,
        LAG(h.price) OVER (
            PARTITION BY h.coin_id
            ORDER BY h.date
        ) AS prev_price
    FROM {{ ref('stg_coin_history') }} h

),

with_price_change AS (

    SELECT
        *,
        CASE
            WHEN prev_price IS NOT NULL AND prev_price != 0
            THEN (price - prev_price) / prev_price * 100
            ELSE NULL
        END AS price_change_pct
    FROM history_with_rank

),

coin_names AS (

    SELECT
        id AS coin_id,
        name
    FROM {{ ref('stg_coins') }}

),

market_summary AS (

    SELECT
        wpc.date,
        SUM(wpc.market_cap) AS total_market_cap,
        (
            ARRAY_AGG(cn.name ORDER BY wpc.total_volume DESC)
        )[1] AS top_coin_by_volume
    FROM with_price_change wpc
    JOIN coin_names cn
        ON wpc.coin_id = cn.coin_id
    GROUP BY wpc.date

),

price_change_top10 AS (

    SELECT
        date,
        AVG(price_change_pct) AS avg_price_change_top10
    FROM with_price_change
    WHERE market_cap_rank <= 10
    GROUP BY date

)

SELECT
    m.date,
    m.total_market_cap,
    m.top_coin_by_volume,
    p.avg_price_change_top10
FROM market_summary m
JOIN price_change_top10 p
    USING (date)
ORDER BY m.date