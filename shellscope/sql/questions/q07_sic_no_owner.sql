-- Q7: Which SIC sections have the most companies with no named owner?
SELECT sic_section, COUNT(*) AS n,
       COUNT(*) FILTER (WHERE no_psc_named = 1)                              AS n_no_psc_named,
       round(100.0 * COUNT(*) FILTER (WHERE no_psc_named = 1) / COUNT(*), 2) AS pct_no_psc_named
FROM risk_flags GROUP BY sic_section ORDER BY n_no_psc_named DESC
