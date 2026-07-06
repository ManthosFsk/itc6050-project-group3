-- Custom singular test:
-- Ensures there are no duplicate (coin_id, date) combinations in stg_coin_history.
-- Each coin should have exactly one row per date. This mirrors the merge
-- primary key (coin_id + date) used at the ingestion layer.
-- The test passes if this query returns zero rows.

SELECT
    coin_id,
    date,
    COUNT(*) AS row_count
FROM {{ ref('stg_coin_history') }}
GROUP BY coin_id, date
HAVING COUNT(*) > 1