
-- risk_flags: one row per company, six 0/1 warning flags + risk_score (0-6).
CREATE OR REPLACE TABLE risk_flags AS
WITH mass AS (                         -- step 1: the top-1% addresses (one row each: no fan-out)
    SELECT address_key FROM mass_registration_addresses
),
flags AS (                             -- step 2: one row per company with the flags
    SELECT p.CompanyNumber, p.CompanyStatus, p.CompanyCategory,
           p.postcode_area, COALESCE(p.glasgow, false) AS glasgow,
           p.sic_section, p.address_key, p.incorporation_date, p.company_age_years,
           CASE WHEN m.address_key IS NOT NULL THEN 1 ELSE 0 END AS at_mass_address,
           p.accounts_overdue,
           p.confstmt_overdue,
           CASE WHEN p.n_corporate        > 0 THEN 1 ELSE 0 END AS corporate_psc,
           CASE WHEN p.n_foreign_resident > 0 THEN 1 ELSE 0 END AS psc_abroad,
           CASE WHEN p.n_active_psc       = 0 THEN 1 ELSE 0 END AS no_psc_named
    FROM company_psc p
    LEFT JOIN mass m ON p.address_key = m.address_key
)
SELECT *,                               -- step 3: add the score
       at_mass_address + accounts_overdue + confstmt_overdue
     + corporate_psc + psc_abroad + no_psc_named AS risk_score
FROM flags;
