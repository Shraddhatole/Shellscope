-- Q2: Are companies at mass addresses more often overdue?
SELECT at_mass_address, COUNT(*) AS n,
       round(100 * AVG(accounts_overdue), 2) AS accounts_overdue_pct,
       round(100 * AVG(confstmt_overdue), 2) AS confstmt_overdue_pct,
       round(median(company_age_years), 2)   AS median_age_years
FROM risk_flags GROUP BY at_mass_address ORDER BY at_mass_address DESC
