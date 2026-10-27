
CREATE OR REPLACE TABLE address_rank AS
WITH a AS (
    SELECT address_key,
           any_value(postcode_area)        AS postcode_area,
           COUNT(*)                        AS n_companies,
           AVG(accounts_overdue)           AS overdue_rate,
           AVG(CASE WHEN CompanyStatus ILIKE '%strike%' THEN 1 ELSE 0 END) AS strike_rate
    FROM clean_companies
    WHERE address_key IS NOT NULL
    GROUP BY address_key)
SELECT *,
    RANK()         OVER (ORDER BY n_companies DESC)                              AS rank_n,
    PERCENT_RANK() OVER (ORDER BY n_companies DESC)                              AS pct_rank,
    SUM(n_companies) OVER (ORDER BY n_companies DESC ROWS UNBOUNDED PRECEDING)
        * 1.0 / SUM(n_companies) OVER ()                                         AS cum_share
FROM a;

CREATE OR REPLACE TABLE address_window_features AS
SELECT CompanyNumber, address_key, incorporation_date,
    ROW_NUMBER() OVER (PARTITION BY address_key ORDER BY incorporation_date, CompanyNumber) AS arrival_no,
    COUNT(*)     OVER (PARTITION BY address_key ORDER BY incorporation_date
                       RANGE BETWEEN INTERVAL 30 DAYS PRECEDING AND CURRENT ROW)      AS same_addr_30d,
    incorporation_date - LAG(incorporation_date) OVER (PARTITION BY address_key
                                                       ORDER BY incorporation_date)   AS days_since_prev
FROM clean_companies
WHERE address_key IS NOT NULL AND incorporation_date IS NOT NULL;
