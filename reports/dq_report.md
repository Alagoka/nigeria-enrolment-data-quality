# Data-quality report: Nigeria primary school enrolment, 2015-2016

Rows in file (after metadata): 150. States found: 37.

| Check | Result | Detail |
|---|---|---|
| Missing values in any cell | PASS | 0 missing cells |
| Expected number of states (36 + FCT) | PASS | 37 found, 37 expected |
| Row count for states (states x years x sexes) | FAIL | 146 rows found, 148 expected |
| State/year/sex combinations missing | FAIL | Borno 2015 Female; Borno 2015 Male |
| Duplicate state/year/sex rows | PASS | 0 duplicates |
| Unexpected gender labels | PASS | none |
| Unexpected years | PASS | none |
| State names with stray spaces | PASS | none |
| Zero or negative totals | PASS | 0 rows |
| National total equals sum of states | PASS | difference by year/sex: 2015 Female: 0, 2015 Male: 0, 2016 Female: 0, 2016 Male: 0 |
| State/sex with year-on-year change over 40% | REVIEW | 20 state/sex rows across 10 states: Abia, Akwa Ibom, Benue, Cross River, Kaduna, Kwara, Ondo, Osun, Sokoto, Taraba |
| Female share outside 35%-55% of a state's enrolment | REVIEW | 4 state-years: Abia, Kebbi, Zamfara |
| File title matches the values | FAIL | Title says 'Percentage Distribution' but values are counts up to 3,260,109 |
