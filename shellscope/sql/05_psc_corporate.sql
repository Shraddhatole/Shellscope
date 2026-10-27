
CREATE OR REPLACE TABLE psc_corporate AS
WITH raw AS (
    SELECT company_number                                                         AS CompanyNumber,
           json_extract_string(data, '$.name')                                    AS owner_name,
           upper(regexp_replace(coalesce(json_extract_string(data, '$.identification.registration_number'), ''),
                                '[^A-Za-z0-9]', '', 'g'))                           AS reg_clean,
           upper(json_extract_string(data, '$.identification.country_registered')) AS country_registered
    FROM read_json(PSC_FILES, format = 'newline_delimited',
                   columns = {'company_number': 'VARCHAR', 'data': 'JSON'})
    WHERE company_number IS NOT NULL
      AND json_extract_string(data, '$.kind') LIKE 'corporate%'
      AND json_extract_string(data, '$.ceased_on') IS NULL)
SELECT CompanyNumber, owner_name, country_registered,
       CASE WHEN regexp_matches(reg_clean, '^[0-9]{1,8}$') THEN lpad(reg_clean, 8, '0')
            ELSE NULLIF(reg_clean, '') END AS owner_number
FROM raw;
