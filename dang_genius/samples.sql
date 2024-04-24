SELECT
  SUM(CASE WHEN UPPER(order_locator) LIKE '%COINBASE%' THEN 1 ELSE 0 END) AS count_Coinbase,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%KRAKEN%' THEN 1 ELSE 0 END) AS count_Kraken,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%GEMINI%' THEN 1 ELSE 0 END) AS count_Gemini,
  SUM(CASE WHEN UPPER(order_locator) LIKE '%BITSTAMP%' THEN 1 ELSE 0 END) AS count_Bitstamp,
  SUM(completed) AS done
FROM win
