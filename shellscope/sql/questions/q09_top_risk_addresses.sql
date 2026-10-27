-- Q9: Which 20 addresses (20+ companies) have the highest average risk score?
SELECT address_key, any_value(postcode_area) AS postcode_area, COUNT(*) AS n,
       round(AVG(risk_score), 2)             AS avg_risk_score,
       round(100 * AVG(accounts_overdue), 1) AS overdue_pct,
       round(100 * AVG(no_psc_named), 1)     AS no_psc_named_pct
FROM risk_flags
WHERE address_key IS NOT NULL
GROUP BY address_key HAVING COUNT(*) >= 20
ORDER BY avg_risk_score DESC, n DESC LIMIT 20
