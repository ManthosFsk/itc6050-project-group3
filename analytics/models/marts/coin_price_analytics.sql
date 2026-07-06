WITH rolling AS (

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

with_prev_price AS (

    SELECT
        coin_id,
        date,
        price,
        LAG(price) OVER (
            PARTITION BY coin_id
            ORDER BY date
        ) AS prev_price
    FROM {{ ref('stg_coin_history') }}

),

with_pct_change AS (

    SELECT
        coin_id,
        price,
        CASE
            WHEN prev_price IS NOT NULL AND prev_price != 0
            THEN (price - prev_price) / prev_price * 100
            ELSE NULL
        END AS price_change_pct
    FROM with_prev_price

),

volatility AS (

    SELECT
        coin_id,
        STDDEV(price)            AS volatility_score,
        STDDEV(price_change_pct) AS volatility_pct,
        AVG(price)               AS avg_price_90d
    FROM with_pct_change
    GROUP BY coin_id

)

SELECT
    r.coin_id,
    r.date,
    r.price,
    r.price_7d_rolling_avg,
    v.volatility_score,
    v.volatility_pct,
    v.avg_price_90d
FROM rolling r
JOIN volatility v USING (coin_id)