-- Q10: Which flags occur together most often? (companies with 2+ flags)
SELECT concat_ws(' + ',
           CASE WHEN at_mass_address  = 1 THEN 'mass address' END,
           CASE WHEN accounts_overdue = 1 THEN 'accounts overdue' END,
           CASE WHEN confstmt_overdue = 1 THEN 'conf. stmt overdue' END,
           CASE WHEN corporate_psc    = 1 THEN 'corporate PSC' END,
           CASE WHEN psc_abroad       = 1 THEN 'PSC abroad' END,
           CASE WHEN no_psc_named     = 1 THEN 'no PSC named' END) AS flag_combination,
       COUNT(*) AS companies,
       round(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_flagged
FROM risk_flags WHERE risk_score >= 2
GROUP BY flag_combination ORDER BY companies DESC LIMIT 10
