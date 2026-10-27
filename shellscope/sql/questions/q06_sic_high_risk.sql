-- Q6: Which industries (SIC sections) have the largest share of companies with 3+ warning signs?
SELECT sic_section, COUNT(*) AS n,
       COUNT(*) FILTER (WHERE risk_score >= 3)                              AS n_score_3plus,
       round(100.0 * COUNT(*) FILTER (WHERE risk_score >= 3) / COUNT(*), 2) AS pct_score_3plus
FROM risk_flags GROUP BY sic_section ORDER BY pct_score_3plus DESC
