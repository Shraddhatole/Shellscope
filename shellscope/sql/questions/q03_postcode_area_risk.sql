-- Q3: Which postcode areas have the highest average risk score? (areas with 1,000+ companies)
SELECT postcode_area, COUNT(*) AS n,
       round(AVG(risk_score), 3)                                      AS avg_risk_score,
       round(100.0 * COUNT(*) FILTER (WHERE risk_score >= 3) / COUNT(*), 2) AS pct_score_3plus
FROM risk_flags
WHERE postcode_area IS NOT NULL
GROUP BY postcode_area HAVING COUNT(*) >= 1000
ORDER BY avg_risk_score DESC LIMIT 15
