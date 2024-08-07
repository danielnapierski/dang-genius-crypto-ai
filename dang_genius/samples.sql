SELECT
  pair,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%COINBASE%' THEN 1 ELSE 0 END) AS Coinbase_WINS,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%KRAKEN%' THEN 1 ELSE 0 END) AS Kraken_WINS,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%GEMINI%' THEN 1 ELSE 0 END) AS Gemini_WINS,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%BITSTAMP%' THEN 1 ELSE 0 END) AS Bitstamp_WINS,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%D%' THEN 1 ELSE 0 END) AS WINS,
  SUM(completed) + SUM(in_progress) - SUM(CASE WHEN UPPER(order_locator) LIKE '%D%' THEN 1 ELSE 0 END) AS LOSSES,
  COUNT(*)
FROM win
group by pair order by WINS desc, LOSSES, pair
