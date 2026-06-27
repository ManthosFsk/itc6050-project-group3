-- Test: current_price must be greater than 0
SELECT *
FROM {{ ref('stg_coins') }}
WHERE current_price <= 0