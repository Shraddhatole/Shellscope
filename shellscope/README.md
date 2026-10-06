# ShellScope: UK company risk radar

**Question:** which UK companies show shell-company *risk indicators* in public Companies House data?

> Risk indicators, not evidence of wrongdoing. A flag means "worth a closer look", nothing more.
> No individuals are named or profiled in this project.

## Data

| Source | What | Licence |
|---|---|---|
| [Companies House Free Company Data Product](https://download.companieshouse.gov.uk/en_output.html) | Basic company data for every live company on the register, one CSV per monthly snapshot | Open Government Licence v3.0 |

Download `BasicCompanyDataAsOneFile-YYYY-MM-DD.zip` into `data/raw/` (no need to unzip).

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1 | `01_load_clean_features.py`: load, clean, build features | `data/processed/companies_YYYY-MM-DD.parquet` |

`make_sample_data.py` builds a small synthetic file with the same layout for testing without the full download.

## Features so far

| Feature | Definition |
|---|---|
| `company_age_years` | Years from incorporation to the snapshot date |
| `accounts_overdue` | Next accounts due date is before the snapshot date |
| `days_accounts_overdue` | Days past the accounts due date (0 if not overdue) |
| `conf_stmt_overdue` | Next confirmation statement due date is before the snapshot date |
| `never_filed_accounts` | No accounts ever filed and older than 2 years |
| `sic_code`, `sic_division`, `sic_section` | From the first SIC code (UK SIC 2007 sections A-U, plus Dormant / None supplied) |
| `postcode_area`, `is_glasgow` | Leading letters of the registered office postcode; Glasgow = area `G` (not GL or GU) |
| `proposal_to_strike_off` | Status is "Active - Proposal to Strike off" |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python 01_load_clean_features.py
```

## Status

Work in progress (MSc Data Science portfolio project).
