# %% [markdown]
# # ShellScope 01: load, clean and build features from Companies House basic company data
#
# Input : data/raw/BasicCompanyDataAsOneFile-YYYY-MM-DD.zip  (free, monthly, ~471 MB zipped)
# Output: data/processed/companies_YYYY-MM-DD.parquet
#
# Run the whole file:  python 01_load_clean_features.py
# Or run cell by cell in VS Code / Jupyter (each "# %%" line starts a cell).

# %% 0. Imports and settings
import csv
import io
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 30)

# Point this at the real file once downloaded. By default it picks the newest zip in data/raw.
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

candidates = sorted(RAW_DIR.glob("BasicCompanyDataAsOneFile-*.zip"))
if not candidates:
    sys.exit(f"No BasicCompanyDataAsOneFile-*.zip found in {RAW_DIR.resolve()}")
DATA_PATH = candidates[-1]

# The snapshot date is in the file name: everything is judged "as at" this date
match = re.search(r"(\d{4}-\d{2}-\d{2})", DATA_PATH.name)
SNAPSHOT = pd.Timestamp(match.group(1))
print("File:", DATA_PATH.name, "| snapshot:", SNAPSHOT.date())

# %% 1. Peek at the header before loading anything
header = pd.read_csv(DATA_PATH, nrows=0)
raw_cols = list(header.columns)
print(len(raw_cols), "columns")
print([c for c in raw_cols if c != c.strip()])       # names with stray spaces

# Map cleaned name -> raw name, so we can refer to columns by their clean names
clean_to_raw = {c.strip(): c for c in raw_cols}

# %% 1b. Pre-scan for malformed rows
# pandas skips rows with the wrong number of fields ONLY when it parses every column.
# With usecols (which we need for memory), bad rows slip in silently with shifted values.
# So find them first with the csv module, streaming the zip (low memory), then skip them.
def find_bad_lines(path, expected_fields):
    bad = []
    with zipfile.ZipFile(path) as z, z.open(z.namelist()[0]) as f:
        text = io.TextIOWrapper(f, encoding="utf-8", errors="replace", newline="")
        reader = csv.reader(text)
        next(reader)                                   # skip header
        for row in reader:
            if len(row) != expected_fields:
                bad.append(reader.line_num - 1)        # 0-indexed line, header = line 0
    return bad

BAD_LINES = find_bad_lines(DATA_PATH, len(raw_cols))
print(f"{len(BAD_LINES)} malformed rows at lines {BAD_LINES[:10]}")

# %% 2. Decide what to load
WANTED = [
    "CompanyName", "CompanyNumber",
    "RegAddress.AddressLine1", "RegAddress.PostTown", "RegAddress.PostCode",
    "CompanyCategory", "CompanyStatus", "CountryOfOrigin",
    "IncorporationDate",
    "Accounts.NextDueDate", "Accounts.LastMadeUpDate", "Accounts.AccountCategory",
    "Mortgages.NumMortCharges",
    "SICCode.SicText_1", "SICCode.SicText_2",
    "ConfStmtNextDueDate", "ConfStmtLastMadeUpDate",
]
CATEGORY_COLS = ["CompanyCategory", "CompanyStatus", "CountryOfOrigin",
                 "Accounts.AccountCategory", "RegAddress.PostTown"]
DATE_COLS = ["IncorporationDate", "Accounts.NextDueDate", "Accounts.LastMadeUpDate",
             "ConfStmtNextDueDate", "ConfStmtLastMadeUpDate"]

missing = [c for c in WANTED if c not in clean_to_raw]
assert not missing, f"Columns not found in this file: {missing}"

dtypes = {clean_to_raw[c]: "category" for c in CATEGORY_COLS}
dtypes[clean_to_raw["CompanyNumber"]] = "str"          # keep leading zeros and SC prefixes
dtypes[clean_to_raw["Mortgages.NumMortCharges"]] = "Int16"   # nullable small integer

# %% 3. Memory: naive load vs optimised load (on the first 200,000 rows)
SAMPLE_ROWS = 200_000

naive = pd.read_csv(DATA_PATH, nrows=SAMPLE_ROWS, low_memory=False, on_bad_lines="skip")
optim = pd.read_csv(
    DATA_PATH,
    nrows=SAMPLE_ROWS,
    usecols=lambda c: c.strip() in WANTED,
    dtype=dtypes,
    parse_dates=[clean_to_raw[c] for c in DATE_COLS],
    date_format="%d/%m/%Y",
    skiprows=BAD_LINES,
)
mb = lambda d: d.memory_usage(deep=True).sum() / 1e6
print(f"naive:     {naive.shape}  {mb(naive):8.1f} MB")
print(f"optimised: {optim.shape}  {mb(optim):8.1f} MB  ({mb(naive) / mb(optim):.1f}x smaller)")
print(optim.memory_usage(deep=True).div(1e6).round(2).sort_values(ascending=False).head(8))
del naive, optim

# %% 4. Full optimised load
df = pd.read_csv(
    DATA_PATH,
    usecols=lambda c: c.strip() in WANTED,
    dtype=dtypes,
    parse_dates=[clean_to_raw[c] for c in DATE_COLS],
    date_format="%d/%m/%Y",
    skiprows=BAD_LINES,             # drop the malformed rows found in the pre-scan
    on_bad_lines="warn",            # belt and braces: warn about anything else odd
    encoding="utf-8",
    encoding_errors="replace",
)

# Clean column names: strip the stray spaces, then give short snake_case names
RENAME = {
    "CompanyName": "company_name", "CompanyNumber": "company_number",
    "RegAddress.AddressLine1": "address_line1", "RegAddress.PostTown": "post_town",
    "RegAddress.PostCode": "postcode", "CompanyCategory": "company_category",
    "CompanyStatus": "company_status", "CountryOfOrigin": "country_of_origin",
    "IncorporationDate": "incorporation_date",
    "Accounts.NextDueDate": "accounts_next_due", "Accounts.LastMadeUpDate": "accounts_last_made_up",
    "Accounts.AccountCategory": "accounts_category", "Mortgages.NumMortCharges": "num_mort_charges",
    "SICCode.SicText_1": "sic_text_1", "SICCode.SicText_2": "sic_text_2",
    "ConfStmtNextDueDate": "conf_stmt_next_due", "ConfStmtLastMadeUpDate": "conf_stmt_last_made_up",
}
df.columns = df.columns.str.strip()
df = df.rename(columns=RENAME)
print(df.shape)
print(list(df.columns))

# %% 5. First look
df.info(memory_usage="deep")

# %%
print(df.head(3).T)

# %%
print(df.describe())                                   # numeric + datetime columns
print(df.describe(include="category").T)               # count / unique / top / freq

# %%
print(df.isna().sum().sort_values(ascending=False))

# %% 6. What's in the register? value_counts(normalize=True)
print(df["company_status"].value_counts(normalize=True).round(4))
print(df["company_category"].value_counts(normalize=True).head(8).round(4))
print(df["accounts_category"].value_counts(normalize=True, dropna=False).round(4))
print(df["sic_text_1"].value_counts(normalize=True).head(15).round(4))

# %% 7. Selecting rows: .loc vs .query (same result, two styles)
recent_loc = df.loc[
    (df["incorporation_date"] >= "2025-01-01") & (df["company_status"] == "Active"),
    ["company_name", "incorporation_date", "postcode"],
]
recent_q = df.query("incorporation_date >= '2025-01-01' and company_status == 'Active'")[
    ["company_name", "incorporation_date", "postcode"]
]
assert recent_loc.equals(recent_q)
print(len(recent_loc), "active companies incorporated since 1 Jan 2025")

cutoff = SNAPSHOT - pd.DateOffset(years=1)
print(len(df.query("incorporation_date >= @cutoff")), "incorporated in the last year")

# %% 8. Feature engineering

# 8a. Company age in years at the snapshot date
df["company_age_years"] = (SNAPSHOT - df["incorporation_date"]).dt.days / 365.25

# 8b. Accounts overdue: next due date already passed at the snapshot
df["accounts_overdue"] = df["accounts_next_due"] < SNAPSHOT
df["days_accounts_overdue"] = (
    (SNAPSHOT - df["accounts_next_due"]).dt.days.clip(lower=0)
)

# 8c. Confirmation statement overdue
df["conf_stmt_overdue"] = df["conf_stmt_next_due"] < SNAPSHOT

# 8d. Never filed accounts (and old enough that it should have)
df["never_filed_accounts"] = df["accounts_last_made_up"].isna() & (
    df["company_age_years"] > 2
)

# 8e. SIC code -> 5-digit code, 2-digit division, section letter
df["sic_code"] = df["sic_text_1"].str.extract(r"^(\d{5})", expand=False)
df["sic_division"] = pd.to_numeric(df["sic_code"].str[:2], errors="coerce").astype("Int8")

SECTION_BOUNDS = [  # (first division, last division, section)
    (1, 3, "A"), (5, 9, "B"), (10, 33, "C"), (35, 35, "D"), (36, 39, "E"),
    (41, 43, "F"), (45, 47, "G"), (49, 53, "H"), (55, 56, "I"), (58, 63, "J"),
    (64, 66, "K"), (68, 68, "L"), (69, 75, "M"), (77, 82, "N"), (84, 84, "O"),
    (85, 85, "P"), (86, 88, "Q"), (90, 93, "R"), (94, 96, "S"), (97, 98, "T"),
    (99, 99, "U"),
]
division_to_section = {d: s for lo, hi, s in SECTION_BOUNDS for d in range(lo, hi + 1)}
df["sic_section"] = df["sic_division"].map(division_to_section)
df.loc[df["sic_code"] == "99999", "sic_section"] = "Dormant"
df.loc[df["sic_text_1"] == "None Supplied", "sic_section"] = "None supplied"
df["sic_section"] = df["sic_section"].astype("category")
df["n_sic_codes"] = df[["sic_text_1", "sic_text_2"]].notna().sum(axis=1)

# 8f. Postcode area and Glasgow flag (area 'G' only: not GL or GU)
pc = df["postcode"].str.upper().str.strip()
df["postcode_area"] = pc.str.extract(r"^([A-Z]{1,2})\d", expand=False).astype("category")
df["is_glasgow"] = df["postcode_area"] == "G"
print(df.loc[df["postcode"].str.startswith("G"), "postcode_area"]
        .value_counts().loc[lambda s: s > 0])            # G vs GL vs GU kept apart

# 8g. Status flags
df["proposal_to_strike_off"] = df["company_status"] == "Active - Proposal to Strike off"
df["is_scottish_number"] = df["company_number"].str.startswith("SC")

# %% 9. Sanity checks: fail loudly if something is off
assert df["company_number"].is_unique, "duplicate company numbers"
assert df["company_number"].str.len().eq(8).all(), "company numbers should be 8 characters"
assert (df["company_age_years"].dropna() >= 0).all(), "incorporated after snapshot?"
assert not df.loc[df["postcode_area"].isin(["GL", "GU"]), "is_glasgow"].any(), \
    "GL/GU wrongly flagged as Glasgow"
print("all checks passed")

# %% 10. A first look at the features
features = ["accounts_overdue", "conf_stmt_overdue", "never_filed_accounts",
            "proposal_to_strike_off", "is_glasgow"]
print(df[features].mean().round(4))                         # rate of each flag

print(df.groupby("is_glasgow")[["accounts_overdue", "conf_stmt_overdue"]].mean().round(4))

print(df.groupby("sic_section", observed=True)["accounts_overdue"]
        .agg(n="size", overdue_rate="mean")
        .sort_values("n", ascending=False).head(10).round(4))

print(df["company_age_years"].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).round(2))

# %% 11. Save
out = PROCESSED_DIR / f"companies_{SNAPSHOT.date()}.parquet"
try:
    df.to_parquet(out, index=False)
    print("saved", out, f"{out.stat().st_size / 1e6:.1f} MB")
    check = pd.read_parquet(out)
    assert check.shape == df.shape
    print("re-read OK, dtypes kept:", check["company_status"].dtype, check["incorporation_date"].dtype)
except ImportError:
    fallback = out.with_suffix(".pkl")
    df.to_pickle(fallback)
    print("pyarrow not installed: run  pip install pyarrow  to save Parquet.",
          "Saved a pickle instead:", fallback)
