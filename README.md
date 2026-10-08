# ShellScope: UK company risk radar

**Question:** Which UK companies show shell-company *risk indicators*, such as mass-registration
addresses, overdue accounts and strike-off proposals, and how did new incorporations change after
identity verification became mandatory at Companies House on 18 Nov 2025?

> Risk indicators, not evidence of wrongdoing. Shared registered addresses are a legal, common
> service. No individual companies or people are named in this analysis.

## Data
- **Companies House Free Company Data Product** (BasicCompanyDataAsOneFile, snapshot 2026-10-01):
  5,704,711 entities on the live register. Source: download.companieshouse.gov.uk.
  Licence: Open Government Licence v3.0 (check the wording on the download page).
- Raw data is not stored in this repo (see "Reproduce").

## Method (notebooks)
| Notebook | What it does |
|---|---|
| `01_explore.ipynb` | Load 5.7M rows with dtypes/categories, missing values, scope rule, features (age, overdue flags, SIC section, Glasgow flag), save Parquet |
| `02_addresses_tests.ipynb` | Address key (cleaned line 1 + postcode), companies per address, size bands, age-stratified tests, chi-square, cluster bootstrap, Mann-Whitney |
| `04_trends_report.ipynb` | Monthly incorporations since 2000, 12-month rolling mean, YoY, before/after 18 Nov 2025, rates by industry and Glasgow vs UK |

**Outcomes:** (1) accounts overdue among active companies that must file accounts (baseline 1.88%);
(2) strike-off proposal among companies that must file accounts (baseline 7.65%).

## Key findings
1. **Concentration:** 351 addresses (0.01% of addresses) hold 11% of all companies; the largest holds 87,403.
2. **No simple "big address = risky" pattern.** Strike-off is *highest* for companies alone at their
   address (1.28× baseline). Address band and strike-off are linked but weakly
   (χ² = 28,424, df = 5, p < 0.001, Cramér's V = 0.07).
3. **Overdue accounts, age-adjusted (Simpson's paradox):** within every age group, companies at
   1,000+ addresses are more often overdue: 1.19× (<2 years) up to 1.67× (10+ years), Holm-adjusted
   p < 0.001; absolute gap ≤ 1.2 percentage points. This is hidden in the raw totals because
   mass-address companies are much younger (median 2.6 vs 5.4 years; Mann-Whitney p < 0.001).
4. **Honest uncertainty:** companies cluster by registration agent. A cluster bootstrap over addresses
   gives a 10+ year ratio of 1.63 (95% CI 1.16–2.40), about 7× wider than the naive interval.
5. **Heterogeneity:** most large addresses look ordinary; a few have extreme strike-off rates (>70%).
   The useful signal is *unusual* addresses, not *big* addresses.
6. **Incorporations and the 18 Nov 2025 rule:** year-on-year growth was +55–71% in Aug–Oct 2025,
   slowed after the rule and turned negative by Aug–Sep 2026 (−4% to −8%). No sharp break on the rule
   date. Daily incorporations after the rule were −7.2% vs the previous 6 months but +26.5% vs the same
   months a year earlier; both comparisons are biased (see limitations), so no causal claim is made.
7. **Industry and Glasgow:** [fill in: highest/lowest strike-off industries from Cell 6; Glasgow's
   overall rates vs UK from Cell 5; whether Glasgow's ratio stays above 1 within industries, Cell 7].

![Monthly incorporations](reports/figures/01_monthly_incorporations.png)
![Strike-off by industry](reports/figures/02_strikeoff_by_sic.png)

## Limitations
- **Survivorship bias:** the file contains only companies still on the register (no dissolved
  companies), so older periods are undercounted and YoY growth is biased upwards.
- **Address matching:** text cleaning can't merge every variant (e.g. one building under several
  street numbers); postcode-level counts are used as a robustness check.
- **Non-independence:** companies sharing an agent aren't independent; naive p-values overstate
  certainty (hence the cluster bootstrap).
- **Proxies:** overdue accounts and strike-off measure neglect as much as shell activity.
- **Base rates:** genuine shell companies are rare, so any indicator flags mostly legitimate businesses.

## Next steps
- Part 3: merge Persons with Significant Control (PSC) data (corporate/overseas owners, missing PSC)
  and fit a logistic regression with age as a control (odds ratios).
- Interrupted time series / official incorporation statistics to estimate the 18 Nov 2025 rule's effect.

## Reproduce
1. Download BasicCompanyDataAsOneFile from download.companieshouse.gov.uk into `data/raw/`.
2. `pip install -r requirements.txt`
3. Run the notebooks in order (01 → 02 → 04). Set `ROOT` in each notebook's first cell.