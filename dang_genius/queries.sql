SELECT datetime(minute_stamp, 'localtime') AS timestamp,
       datetime(minute_stamp) AS parsed_datetime,
       delta AS value FROM price_history
       WHERE pair == 'BTC_USD'
       ORDER BY id LIMIT 10
