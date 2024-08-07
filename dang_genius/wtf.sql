SELECT DISTINCT COALESCE(win.pair, wallet.symbol || '_USD') AS c
FROM win FULL JOIN wallet ON wallet.symbol = REPLACE(win.pair, '_USD', '')
WHERE wallet.symbol != 'USD'
ORDER BY c