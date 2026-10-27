
CREATE OR REPLACE TABLE psc AS
SELECT
    company_number                                   AS CompanyNumber,
    data->>'$.kind'                                  AS kind,
    TRY_CAST(data->>'$.notified_on' AS DATE)         AS notified_on,
    TRY_CAST(data->>'$.ceased_on'   AS DATE)         AS ceased_on,
    upper(data->>'$.country_of_residence')           AS country_of_residence,
    data->>'$.statement'                             AS statement,
    CAST(data->'$.natures_of_control' AS VARCHAR)    AS natures,
    -- privacy: hash of name + birth year/month as an identity proxy; names are not stored
    md5(lower(coalesce(data->>'$.name', '')) || '|' ||
        coalesce(data->>'$.date_of_birth.year', '') || '|' ||
        coalesce(data->>'$.date_of_birth.month', ''))  AS person_id
FROM read_json(PSC_FILES, format = 'newline_delimited',
               columns = {'company_number': 'VARCHAR', 'data': 'JSON'})
WHERE company_number IS NOT NULL;   -- drops the 'totals' summary line



-- A: active rows; person id for individuals only (keeps the later join a pure equality)
CREATE OR REPLACE TABLE psc_active AS SELECT CompanyNumber, kind, statement, country_of_residence,
  CASE WHEN kind LIKE 'individual%' THEN person_id END AS ind_person_id, natures LIKE '%75-to-100%' AS owns_75
FROM psc WHERE ceased_on IS NULL;
-- B: companies per individual
CREATE OR REPLACE TABLE psc_portfolio AS SELECT ind_person_id AS person_id, COUNT(DISTINCT CompanyNumber) AS n_cos
FROM psc_active WHERE ind_person_id IS NOT NULL GROUP BY ind_person_id;
-- C1-C3, D: see 07_sql_core.ipynb cells 4-8 (psc_counts, psc_company_portfolio, psc_summary, company_psc)
