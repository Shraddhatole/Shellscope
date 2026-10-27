# ShellScope data dictionary

Source: Companies House Basic Company Data (live register), snapshot 2026-10-01. Table `companies` in `data/shellscope.duckdb` (5,704,711 rows).

| column | type | example | approx. distinct | % missing | meaning | quirks |
|---|---|---|---|---|---|---|
| `CompanyName` | VARCHAR | ! LTD | 6,848,663 | 0.0 | Registered company name |  |
| `CompanyNumber` | VARCHAR | 08209948 | 5,055,648 | 0.0 | Unique company ID (8 characters; prefixes e.g. SC = Scotland, NI = Northern Ireland, OC = LLP) | Must stay TEXT: numeric types drop the leading zeros. Raw CSV header had a leading space. |
| `RegAddress.AddressLine1` | VARCHAR | 9 PRINCES SQUARE | 1,761,196 | 1.11 | First line of the registered office address | Messy: '3RD FLOOR' alone (many buildings), 'C/O ...', ST vs STREET; ~1.1% missing. |
| `RegAddress.PostTown` | VARCHAR | HARROGATE | 49,599 | 1.66 | Post town of the registered office | ~1.7% missing. |
| `RegAddress.PostCode` | VARCHAR | HG1 1ND | 1,126,554 | 1.6 | Postcode of the registered office (raw) | ~1.6% missing; inconsistent spacing (use postcode_clean). |
| `CompanyCategory` | VARCHAR | Private Limited Company | 26 | 0.0 | Legal type (private limited, LLP, limited partnership, ...) | 92.5% are Private Limited Company. |
| `CompanyStatus` | VARCHAR | Active | 16 | 0.0 | Current status (Active, Proposal to Strike off, Liquidation, ...) | No 'Dissolved' status: live register only, so closed companies are missing (survivorship bias). |
| `IncorporationDate` | TIMESTAMP | 2012-09-11 00:00:00 | 33,276 | 0.0 | Date the company was set up | Raw format dd/mm/yyyy. Min 1327-01-01 (royal charter bodies). Oct 2026 incomplete (snapshot day). |
| `Accounts.NextDueDate` | TIMESTAMP | 2027-06-30 00:00:00 | 7,851 | 3.04 | Date the next annual accounts are due |  |
| `Accounts.AccountCategory` | VARCHAR | DORMANT | 15 | 0.0 | Type of the last accounts filed (e.g. micro-entity, dormant, no accounts filed) |  |
| `SICCode.SicText_1` | VARCHAR | 99999 - Dormant Company | 1,144 | 0.0 | First industry code with its description |  |
| `ConfStmtNextDueDate` | TIMESTAMP | 2027-09-25 00:00:00 | 5,582 | 1.37 | Date the next confirmation statement is due |  |
| `in_scope` | BOOLEAN | True | 2 | 0.0 | Derived: company must file accounts at Companies House (Part 1 scope rule) |  |
| `company_age_years` | DOUBLE | 14.053388090349076 | 37,059 | 0.0 | Derived: years from IncorporationDate to the snapshot date (2026-10-01) | Right-skewed; use the median or a log scale. |
| `accounts_overdue` | BOOLEAN | False | 2 | 0.0 | Derived: Accounts.NextDueDate is before the snapshot date | Only meaningful for in_scope AND is_active companies. |
| `confstmt_overdue` | BOOLEAN | False | 2 | 0.0 | Derived: ConfStmtNextDueDate is before the snapshot date |  |
| `is_active` | BOOLEAN | True | 2 | 0.0 | Derived: company is active (see the exact rule in 01_explore) |  |
| `strike_off_proposal` | BOOLEAN | False | 2 | 0.0 | Derived: status is 'Active - Proposal to Strike off' |  |
| `sic_code` | VARCHAR | 99999 | 743 | 4.34 | Derived: 5-digit SIC code taken from SICCode.SicText_1 |  |
| `sic_section` | VARCHAR | Dormant | 21 | 0.0 | Derived: SIC 2007 section letter A-U, plus 'None supplied' and 'Dormant' | 'None supplied' (247,820 rows) and 'Dormant' (104,507) are not industries; 'None supplied' has a 10.4% overdue rate. |
| `postcode_clean` | VARCHAR | HG11ND | 840,066 | 1.6 | Derived: postcode in upper case without spaces |  |
| `postcode_area` | VARCHAR | HG | 262 | 1.7 | Derived: letters before the first digit of the postcode (G = Glasgow) |  |
| `glasgow` | BOOLEAN | False | 2 | 0.0 | Derived: postcode_area == 'G' |  |