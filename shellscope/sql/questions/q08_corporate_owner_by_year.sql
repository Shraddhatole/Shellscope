-- Q8: How has the share of corporate owners changed by incorporation year?
SELECT year(incorporation_date) AS inc_year, COUNT(*) AS n,
       round(100 * AVG(corporate_psc), 2) AS corporate_psc_pct
FROM risk_flags
WHERE incorporation_date >= DATE '2000-01-01' AND incorporation_date < DATE '2026-10-01'
GROUP BY inc_year ORDER BY inc_year
