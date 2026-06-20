WITH highs AS
(
    SELECT
        listing_id,
        MAX(high_price) AS high_52w
    FROM daily_prices
    WHERE trade_date >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY listing_id
)

SELECT
    l.symbol,

    dp.close_price,

    h.high_52w,

    ROUND(
        (dp.close_price / h.high_52w) * 100,
        2
    ) AS score

FROM daily_prices dp

JOIN highs h
  ON h.listing_id = dp.listing_id

JOIN listings l
  ON l.id = dp.listing_id

WHERE dp.trade_date =
(
    SELECT MAX(trade_date)
    FROM daily_prices
)

AND dp.close_price >= h.high_52w * 0.97

ORDER BY score DESC

LIMIT 10;