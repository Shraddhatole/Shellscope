## SQL analysis (DuckDB)

Cleaned in SQL (`sql/01_clean_companies.sql`), joined to PSC ownership data (`sql/02_psc.sql`), addresses ranked with window functions (`sql/03_address_ranking.sql`), and six warning flags combined into `risk_flags` (`sql/04_risk_flags.sql`). Snapshot 2026-10-01; risk indicators, not proof.

| # | Question | Answer | SQL |
|---|---|---|---|
| 01 | How many companies sit at the top 1% of addresses? | _fill in, with a number_ | [q01_mass_address_companies.sql](sql/questions/q01_mass_address_companies.sql) |
| 02 | Are companies at mass addresses more often overdue? | _fill in, with a number_ | [q02_mass_vs_rest_overdue.sql](sql/questions/q02_mass_vs_rest_overdue.sql) |
| 03 | Which postcode areas have the highest average risk score? (areas with 1,000+ companies) | _fill in, with a number_ | [q03_postcode_area_risk.sql](sql/questions/q03_postcode_area_risk.sql) |
| 04 | Is Glasgow above or below the UK average? | _fill in, with a number_ | [q04_glasgow_vs_uk.sql](sql/questions/q04_glasgow_vs_uk.sql) |
| 05 | How many companies combine several warning signs? | _fill in, with a number_ | [q05_risk_score_distribution.sql](sql/questions/q05_risk_score_distribution.sql) |
| 06 | Which industries (SIC sections) have the largest share of companies with 3+ warning signs? | _fill in, with a number_ | [q06_sic_high_risk.sql](sql/questions/q06_sic_high_risk.sql) |
| 07 | Which SIC sections have the most companies with no named owner? | _fill in, with a number_ | [q07_sic_no_owner.sql](sql/questions/q07_sic_no_owner.sql) |
| 08 | How has the share of corporate owners changed by incorporation year? | _fill in, with a number_ | [q08_corporate_owner_by_year.sql](sql/questions/q08_corporate_owner_by_year.sql) |
| 09 | Which 20 addresses (20+ companies) have the highest average risk score? | _fill in, with a number_ | [q09_top_risk_addresses.sql](sql/questions/q09_top_risk_addresses.sql) |
| 10 | Which flags occur together most often? (companies with 2+ flags) | _fill in, with a number_ | [q10_flag_combinations.sql](sql/questions/q10_flag_combinations.sql) |
