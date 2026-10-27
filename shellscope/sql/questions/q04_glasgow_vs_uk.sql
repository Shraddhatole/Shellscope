-- Q4: Is Glasgow above or below the UK average?
SELECT CASE WHEN GROUPING(glasgow) = 1 THEN 'UK total'
            WHEN glasgow THEN 'Glasgow (G)' ELSE 'Rest of UK' END AS area,
       COUNT(*) AS n,
       round(AVG(risk_score), 3)              AS avg_risk_score,
       round(100 * AVG(at_mass_address), 2)   AS mass_address_pct,
       round(100 * AVG(accounts_overdue), 2)  AS accounts_overdue_pct,
       round(100 * AVG(corporate_psc), 2)     AS corporate_psc_pct,
       round(100 * AVG(psc_abroad), 2)        AS psc_abroad_pct,
       round(100 * AVG(no_psc_named), 2)      AS no_psc_named_pct
FROM risk_flags
GROUP BY ROLLUP (glasgow)
ORDER BY 1      -- alphabetical: Glasgow (G), Rest of UK, UK total
