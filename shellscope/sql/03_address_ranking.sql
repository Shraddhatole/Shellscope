
CREATE OR REPLACE TABLE address_rank AS
WITH a AS (
    SELECT address_key,
           any_value(postcode_area)                                         AS postcode_area,
           COUNT(*)                                                         AS n_companies,
           AVG(accounts_overdue)                                            AS overdue_rate,
           AVG(CASE WHEN CompanyStatus ILIKE '%strike%' THEN 1 ELSE 0 END)   AS strike_rate
    FROM clean_companies
    WHERE address_key IS NOT NULL
    GROUP BY address_key)
SELECT *,
    RANK()         OVER (ORDER BY n_companies DESC)                                   AS rank_n,
    PERCENT_RANK() OVER (ORDER BY n_companies DESC)                                   AS pct_rank,
    CAST(SUM(n_companies) OVER (ORDER BY n_companies DESC ROWS UNBOUNDED PRECEDING) AS DOUBLE)
      / CAST(SUM(n_companies) OVER () AS DOUBLE)                                       AS cum_share
FROM a;

-- the top 1% of addresses by number of companies
CREATE OR REPLACE TABLE mass_registration_addresses AS
SELECT * FROM address_rank WHERE pct_rank <= 0.01;

CREATE OR REPLACE TABLE address_window_features AS
WITH d AS (
    SELECT CompanyNumber, address_key, incorporation_date,
           date_diff('day', DATE '1300-01-01', incorporation_date) AS day_no
    FROM clean_companies
    WHERE address_key IS NOT NULL AND incorporation_date IS NOT NULL)
SELECT CompanyNumber, address_key, incorporation_date,
    ROW_NUMBER() OVER (PARTITION BY address_key ORDER BY incorporation_date, CompanyNumber)   AS arrival_no,
    COUNT(*)     OVER (PARTITION BY address_key ORDER BY day_no
                       RANGE BETWEEN 30 PRECEDING AND CURRENT ROW)                            AS same_addr_30d,
    day_no - LAG(day_no) OVER (PARTITION BY address_key ORDER BY day_no)                      AS days_since_prev
FROM d;
