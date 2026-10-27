-- Q5: How many companies combine several warning signs?
SELECT risk_score, COUNT(*) AS companies,
       round(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 3) AS pct,
       round(100.0 * SUM(COUNT(*)) OVER (ORDER BY risk_score DESC ROWS UNBOUNDED PRECEDING)
             / SUM(COUNT(*)) OVER (), 3)                   AS pct_this_score_or_higher
FROM risk_flags GROUP BY risk_score ORDER BY risk_score
