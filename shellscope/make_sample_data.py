"""
Builds a small SYNTHETIC file shaped like Companies House 'BasicCompanyDataAsOneFile'
so the pipeline can be tested without the 471 MB download.
Same header (including leading spaces), dd/mm/yyyy dates, quoted names with commas,
'None Supplied' SIC codes, a mass-registration address, and one malformed row.
Every company in it is fictional.
"""
import csv, io, zipfile
import numpy as np

rng = np.random.default_rng(2026)
N = 20_000
SNAPSHOT = np.datetime64("2026-10-01")

prev = []
for i in range(1, 11):
    prev += [f"PreviousName_{i}.CONDATE", f" PreviousName_{i}.CompanyName"]
HEADER = (["CompanyName", " CompanyNumber", "RegAddress.CareOf", "RegAddress.POBox",
           "RegAddress.AddressLine1", " RegAddress.AddressLine2", "RegAddress.PostTown",
           "RegAddress.County", "RegAddress.Country", "RegAddress.PostCode",
           "CompanyCategory", "CompanyStatus", "CountryOfOrigin", "DissolutionDate",
           "IncorporationDate", "Accounts.AccountRefDay", "Accounts.AccountRefMonth",
           "Accounts.NextDueDate", "Accounts.LastMadeUpDate", "Accounts.AccountCategory",
           "Returns.NextDueDate", "Returns.LastMadeUpDate", "Mortgages.NumMortCharges",
           "Mortgages.NumMortOutstanding", "Mortgages.NumMortPartSatisfied",
           "Mortgages.NumMortSatisfied", "SICCode.SicText_1", "SICCode.SicText_2",
           "SICCode.SicText_3", "SICCode.SicText_4", "LimitedPartnerships.NumGenPartners",
           "LimitedPartnerships.NumLimPartners", "URI"] + prev +
          ["ConfStmtNextDueDate", " ConfStmtLastMadeUpDate"])

def pick(options, p, n):
    return rng.choice(np.array(options, dtype=object), size=n, p=np.array(p) / sum(p))

categories = pick(["Private Limited Company",
                   "PRI/LTD BY GUAR/NSC (Private, limited by guarantee, no share capital)",
                   "Limited Liability Partnership", "Public Limited Company",
                   "Community Interest Company", "Limited Partnership",
                   "Scottish Partnership", "Overseas Entity"],
                  [88, 4, 2.5, 0.5, 1.5, 1.5, 1, 1], N)
statuses = pick(["Active", "Active - Proposal to Strike off", "Liquidation",
                 "In Administration", "Voluntary Arrangement"],
                [90, 7, 2, 0.6, 0.4], N)
sic = pick(["62020 - Information technology consultancy activities",
            "68209 - Other letting and operating of own or leased real estate",
            "70229 - Management consultancy activities other than financial management",
            "82990 - Other business support service activities n.e.c.",
            "47910 - Retail sale via mail order houses or via Internet",
            "56101 - Licensed restaurants", "41100 - Development of building projects",
            "96090 - Other service activities n.e.c.",
            "99999 - Dormant Company", "64209 - Activities of other holding companies n.e.c.",
            "01110 - Growing of cereals (except rice), leguminous crops and oil seeds",
            "None Supplied"],
           [14, 10, 10, 7, 6, 4, 5, 6, 6, 4, 2, 4], N)
acc_cat = pick(["MICRO ENTITY", "TOTAL EXEMPTION FULL", "DORMANT", "UNAUDITED ABRIDGED",
                "NO ACCOUNTS FILED", "SMALL", "FULL", "GROUP"],
               [45, 20, 10, 8, 10, 4, 2, 1], N)

# Postcode areas: Glasgow 'G' plus look-alikes GL (Gloucester), GU (Guildford)
areas = pick(["G", "GL", "GU", "EH", "PA", "M", "B", "EC", "N", "LS", "AB", "KA"],
             [9, 3, 3, 6, 2, 10, 10, 15, 12, 8, 4, 3], N)
def postcode(area):
    d = rng.integers(1, 30)
    tail = f"{rng.integers(1, 9)}{chr(65 + rng.integers(0, 26))}{chr(65 + rng.integers(0, 26))}"
    return f"{area}{d} {tail}"
postcodes = np.array([postcode(a) for a in areas], dtype=object)
towns = {"G": "GLASGOW", "GL": "GLOUCESTER", "GU": "GUILDFORD", "EH": "EDINBURGH",
         "PA": "PAISLEY", "M": "MANCHESTER", "B": "BIRMINGHAM", "EC": "LONDON",
         "N": "LONDON", "LS": "LEEDS", "AB": "ABERDEEN", "KA": "KILMARNOCK"}

# Incorporation: skewed towards recent years
age_days = rng.exponential(scale=9 * 365, size=N).astype(int) + 30
inc = SNAPSHOT - age_days.astype("timedelta64[D]")

# Next accounts due: most in the future, some overdue (more for strike-off status)
p_overdue = np.where(statuses == "Active - Proposal to Strike off", 0.6, 0.08)
overdue = rng.random(N) < p_overdue
acc_due = np.where(overdue,
                   SNAPSHOT - rng.integers(1, 700, N).astype("timedelta64[D]"),
                   SNAPSHOT + rng.integers(1, 300, N).astype("timedelta64[D]"))
cs_overdue = rng.random(N) < np.where(overdue, 0.5, 0.04)
cs_due = np.where(cs_overdue,
                  SNAPSHOT - rng.integers(1, 400, N).astype("timedelta64[D]"),
                  SNAPSHOT + rng.integers(1, 360, N).astype("timedelta64[D]"))
young = age_days < 400                                   # too new to have filed accounts
last_acc = np.where(young, np.datetime64("NaT", "D"), acc_due - np.timedelta64(456, "D"))

# A 'mass-registration' address shared by 600 companies (a formation-agent style address)
mass_set = set(rng.choice(N, size=600, replace=False).tolist())

def fmt(d):
    return "" if np.isnat(d) else str(d.astype("datetime64[D]").item().strftime("%d/%m/%Y"))

words = ["NORTH", "CLYDE", "APEX", "BRIGHT", "STONE", "RIVER", "OAK", "NOVA", "PEAK",
         "HARBOUR", "SILVER", "THISTLE", "LINK", "CORE", "SUMMIT", "FERN", "ORBIT"]
suffix = {"Limited Liability Partnership": "LLP", "Public Limited Company": "PLC",
          "Limited Partnership": "LP", "Scottish Partnership": "LP"}

uniq = rng.choice(10**6, size=N, replace=False)   # unique company numbers
buf = io.StringIO()
w = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
w.writerow(HEADER)
for i in range(N):
    a, b = rng.choice(words, 2, replace=False)
    name = f"{a} {b} {'& CO, ' if rng.random() < 0.03 else ''}{suffix.get(categories[i], 'LTD')}"
    prefix = "SC" if areas[i] in ("G", "EH", "PA", "AB", "KA") and rng.random() < 0.9 else ""
    num = f"SC{uniq[i]:06d}" if prefix else f"{uniq[i]:08d}"
    if i in mass_set:
        line1, line2, town, pc = "SUITE 1", "100 FORMATION STREET", "LONDON", "EC1V 2NX"
    else:
        line1 = f"{rng.integers(1, 400)} {rng.choice(['HIGH', 'MAIN', 'KING', 'STATION', 'MILL'])} STREET"
        line2, town, pc = "", towns[areas[i]], postcodes[i]
    sics = [sic[i], "", "", ""]
    if rng.random() < 0.15 and sic[i] != "None Supplied":
        sics[1] = "70229 - Management consultancy activities other than financial management"
    row = ([name, num, "", "", line1, line2, town, "", "UNITED KINGDOM", pc,
            categories[i], statuses[i], "United Kingdom", "", fmt(inc[i]),
            str(rng.integers(1, 29)), str(rng.integers(1, 13)), fmt(acc_due[i]),
            fmt(last_acc[i]), acc_cat[i] if not young[i] else "NO ACCOUNTS FILED",
            "", "", str(rng.poisson(0.3)), "0", "0", "0"] + sics +
           ["0", "0", f"http://business.data.gov.uk/id/company/{num}"] + [""] * 20 +
           [fmt(cs_due[i]), fmt(cs_due[i] - np.timedelta64(365, "D"))])
    w.writerow(row)
    if i == 777:                                   # one malformed row: 2 extra fields
        w.writerow(row + ["STRAY", "FIELD"])

csv_text = buf.getvalue()
out = "data/raw/BasicCompanyDataAsOneFile-2026-10-01-SAMPLE.zip"
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("BasicCompanyDataAsOneFile-2026-10-01-SAMPLE.csv", csv_text)
print("wrote", out, "rows:", N + 1, "(1 malformed)")
