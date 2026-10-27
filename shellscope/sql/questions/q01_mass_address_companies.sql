-- Q1: How many companies sit at the top 1% of addresses?
SELECT COUNT(*) FILTER (WHERE at_mass_address = 1)                              AS companies_at_mass_addresses,
       round(100.0 * COUNT(*) FILTER (WHERE at_mass_address = 1) / COUNT(*), 2) AS pct_of_all_companies,
       (SELECT COUNT(*) FROM mass_registration_addresses)                         AS mass_addresses
FROM risk_flags
