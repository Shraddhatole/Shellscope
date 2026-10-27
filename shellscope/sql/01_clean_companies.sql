
-- clean_companies: one row per company with cleaned + derived columns.
-- Snapshot date 2026-10-01. Source table: companies.
CREATE OR REPLACE VIEW clean_companies_v AS
WITH base AS (
    SELECT
        CompanyNumber,
        trim(CompanyName)                         AS company_name,
        CompanyCategory,
        CompanyStatus,
        CAST("IncorporationDate" AS DATE)            AS incorporation_date,
        CAST("Accounts.NextDueDate" AS DATE)         AS accounts_next_due,
        CAST("ConfStmtNextDueDate" AS DATE)          AS confstmt_next_due,
        "RegAddress.AddressLine1"                 AS address_line1,
        upper(trim("RegAddress.PostTown"))        AS post_town,
        "SICCode.SicText_1"                       AS sic_text,
        NULLIF(regexp_replace(upper(trim("RegAddress.PostCode")), '[^A-Z0-9]', '', 'g'), '') AS postcode
    FROM companies
),
step2 AS (
    SELECT *,
        NULLIF(regexp_extract(postcode, '^[A-Z]{1,2}'), '')                AS postcode_area,
        NULLIF(regexp_extract(sic_text, '^\s*([0-9]{5})', 1), '')         AS sic_code,
        TRY_CAST(substr(regexp_extract(sic_text, '^\s*([0-9]{5})', 1), 1, 2) AS INTEGER) AS sic_division,
        regexp_replace(regexp_replace(
            trim(regexp_replace(regexp_replace(
                regexp_replace(upper(address_line1), '^C/O\.?\s*', ''),
            '[^A-Z0-9\s/-]', ' ', 'g'), '\s+', ' ', 'g')),
        ' ST$', ' STREET'), ' RD$', ' ROAD')                                AS line1_clean
    FROM base
)
SELECT
    *,
    line1_clean || ' | ' || postcode                                     AS address_key,
    date_diff('day', incorporation_date, DATE '2026-10-01') / 365.25     AS company_age_years,
    CASE WHEN accounts_next_due < DATE '2026-10-01' THEN 1 ELSE 0 END     AS accounts_overdue,
    CASE WHEN confstmt_next_due < DATE '2026-10-01' THEN 1 ELSE 0 END     AS confstmt_overdue,
    postcode_area = 'G'                                                  AS glasgow,
    CASE
        WHEN sic_text IS NULL OR upper(trim(sic_text)) LIKE 'NONE SUPPLIED%' THEN 'None supplied'
        WHEN sic_code = '99999'               THEN 'Dormant'
        WHEN sic_division BETWEEN 1  AND 3    THEN 'A'
        WHEN sic_division BETWEEN 5  AND 9    THEN 'B'
        WHEN sic_division BETWEEN 10 AND 33   THEN 'C'
        WHEN sic_division = 35                THEN 'D'
        WHEN sic_division BETWEEN 36 AND 39   THEN 'E'
        WHEN sic_division BETWEEN 41 AND 43   THEN 'F'
        WHEN sic_division BETWEEN 45 AND 47   THEN 'G'
        WHEN sic_division BETWEEN 49 AND 53   THEN 'H'
        WHEN sic_division BETWEEN 55 AND 56   THEN 'I'
        WHEN sic_division BETWEEN 58 AND 63   THEN 'J'
        WHEN sic_division BETWEEN 64 AND 66   THEN 'K'
        WHEN sic_division = 68                THEN 'L'
        WHEN sic_division BETWEEN 69 AND 75   THEN 'M'
        WHEN sic_division BETWEEN 77 AND 82   THEN 'N'
        WHEN sic_division = 84                THEN 'O'
        WHEN sic_division = 85                THEN 'P'
        WHEN sic_division BETWEEN 86 AND 88   THEN 'Q'
        WHEN sic_division BETWEEN 90 AND 93   THEN 'R'
        WHEN sic_division BETWEEN 94 AND 96   THEN 'S'
        WHEN sic_division BETWEEN 97 AND 98   THEN 'T'
        WHEN sic_division = 99                THEN 'U'
        ELSE 'Unknown'
    END                                                                  AS sic_section
FROM step2;

-- materialise: store the cleaned result once so later queries are fast
CREATE OR REPLACE TABLE clean_companies AS SELECT * FROM clean_companies_v;
