WITH current_coins AS (

    -- Only coins currently in the top-50 snapshot. coin_history accumulates
    -- history for every coin that has EVER been in the top 50 across past
    -- runs (thanks to the merge load), but stg_coins only ever holds the
    -- CURRENT top 50 (replace load). Without this filter, a coin that has
    -- since dropped out of the top 50 would still appear here with a valid
    -- coin_id but no matching name/symbol/image in stg_coins, showing up
    -- as "nan" wherever the dashboard joins on coin metadata.
    SELECT id AS coin_id
    FROM {{ ref('stg_coins') }}

),

last_90_days AS (

    -- Restrict to a genuine trailing 90-calendar-day window, measured from
    -- the most recent date actually loaded in the table. Without this
    -- filter, all metrics below would be computed over the entire
    -- accumulated history in raw.coin_history, which grows past 90 days
    -- as the merge-loaded pipeline is run on different days.
    SELECT
        h.coin_id,
        h.date,
        h.price
    FROM {{ ref('stg_coin_history') }} h
    INNER JOIN current_coins c
        ON h.coin_id = c.coin_id
    WHERE h.date >= (
        SELECT MAX(date) - INTERVAL '89 days'
        FROM {{ ref('stg_coin_history') }}
    )

),

rolling AS (

    -- The 7-day rolling average is computed from the FULL history table
    -- (not last_90_days), so that the earliest rows of the 90-day window
    -- still have 6 prior days of context to average over. It is then
    -- restricted to the 90-day window (and current coins) in the final
    -- SELECT below.
    SELECT
        h.coin_id,
        h.date,
        h.price,
        AVG(h.price) OVER (
            PARTITION BY h.coin_id
            ORDER BY h.date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS price_7d_rolling_avg
    FROM {{ ref('stg_coin_history') }} h
    INNER JOIN current_coins c
        ON h.coin_id = c.coin_id

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
    FROM last_90_days

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
JOIN last_90_days d
    ON r.coin_id = d.coin_id
    AND r.date = d.date
JOIN volatility v
    ON r.coin_id = v.coin_id