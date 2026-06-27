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

volatility AS (

    SELECT
        coin_id,
        STDDEV(price) AS volatility_score,
        AVG(price)    AS avg_price_90d
    FROM {{ ref('stg_coin_history') }}
    GROUP BY coin_id

)

SELECT
    r.coin_id,
    r.date,
    r.price,
    r.price_7d_rolling_avg,
    v.volatility_score,
    v.avg_price_90d
FROM rolling r
JOIN volatility v USING (coin_id)