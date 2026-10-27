"""
Data-quality checks for Nigeria primary school enrolment by state, year and sex, 2015-2016.
Source: National Bureau of Statistics (2018), via Open Africa.
Run from the repo root:  python src/dq_checks.py
Outputs: reports/dq_report.md and reports/flagged_rows.csv
"""
import os
import sys
import pandas as pd

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/primary_school_enrollment_2015_2016.csv"
YOY_THRESHOLD = 0.40        # flag state/gender year-on-year change above 40%
GENDER_SHARE_RANGE = (0.35, 0.55)   # plausible female share of a state's enrolment
EXPECTED_STATES = 37        # 36 states + FCT (national row 'Nigeria' excluded)
EXPECTED_YEARS = [2015, 2016]
EXPECTED_GENDERS = {"Female", "Male"}

df = pd.read_csv(PATH, skiprows=6)          # first 6 lines are metadata
results, flags = [], []

def record(name, status, detail):
    results.append((name, status, detail))

# 1. Completeness
nulls = int(df.isna().sum().sum())
record("Missing values in any cell", "PASS" if nulls == 0 else "FAIL", f"{nulls} missing cells")

states = df[df.state != "Nigeria"]
n_states = states.state.nunique()
record("Expected number of states (36 + FCT)", "PASS" if n_states == EXPECTED_STATES else "FAIL",
       f"{n_states} found, {EXPECTED_STATES} expected")

expected_rows = EXPECTED_STATES * len(EXPECTED_YEARS) * len(EXPECTED_GENDERS)
got_rows = len(states)
record("Row count for states (states x years x sexes)", "PASS" if got_rows == expected_rows else "FAIL",
       f"{got_rows} rows found, {expected_rows} expected")

full = pd.MultiIndex.from_product([sorted(states.state.unique()), EXPECTED_YEARS, sorted(EXPECTED_GENDERS)],
                                  names=["state", "year", "gender"])
have = pd.MultiIndex.from_frame(states[["state", "year", "gender"]])
missing = full.difference(have)
for s, y, g in missing:
    flags.append({"check": "Missing record", "state": s, "year": y, "gender": g, "value": None,
                  "note": "No row for this state/year/sex"})
record("State/year/sex combinations missing", "PASS" if len(missing) == 0 else "FAIL",
       "; ".join(f"{s} {y} {g}" for s, y, g in missing) or "none")

# 2. Duplicates
dups = int(df.duplicated(subset=["state", "year", "gender"]).sum())
record("Duplicate state/year/sex rows", "PASS" if dups == 0 else "FAIL", f"{dups} duplicates")

# 3. Consistency of labels and types
bad_gender = set(df.gender.unique()) - EXPECTED_GENDERS
record("Unexpected gender labels", "PASS" if not bad_gender else "FAIL", str(bad_gender or "none"))
bad_year = set(df.year.unique()) - set(EXPECTED_YEARS)
record("Unexpected years", "PASS" if not bad_year else "FAIL", str(bad_year or "none"))
messy = df.state[df.state != df.state.str.strip()].unique().tolist()
record("State names with stray spaces", "PASS" if not messy else "FAIL", str(messy or "none"))
nonpos = df[df.total <= 0]
record("Zero or negative totals", "PASS" if nonpos.empty else "FAIL", f"{len(nonpos)} rows")

# 4. Reconciliation: national row vs sum of states
nat = df[df.state == "Nigeria"].set_index(["year", "gender"]).total
summ = states.groupby(["year", "gender"]).total.sum()
diff = (nat - summ).dropna()
record("National total equals sum of states", "PASS" if (diff == 0).all() else "FAIL",
       "difference by year/sex: " + ", ".join(f"{y} {g}: {int(d)}" for (y, g), d in diff.items()))

# 5. Plausibility: year-on-year change by state and sex
wide = states.pivot_table(index=["state", "gender"], columns="year", values="total")
wide["yoy_change"] = (wide[2016] - wide[2015]) / wide[2015]
big = wide[wide.yoy_change.abs() > YOY_THRESHOLD].reset_index()
for _, r in big.iterrows():
    flags.append({"check": "Large year-on-year change", "state": r.state, "year": "2015->2016",
                  "gender": r.gender, "value": f"{int(r[2015])} -> {int(r[2016])} ({r.yoy_change:+.0%})",
                  "note": f"Change above {YOY_THRESHOLD:.0%}"})
big_states = sorted(big.state.unique())
record(f"State/sex with year-on-year change over {YOY_THRESHOLD:.0%}",
       "PASS" if big.empty else "REVIEW", f"{len(big)} state/sex rows across {len(big_states)} states: " + ", ".join(big_states))

# 6. Plausibility: female share of enrolment
tot = states.pivot_table(index=["state", "year"], columns="gender", values="total").dropna()
tot["female_share"] = tot.Female / (tot.Female + tot.Male)
odd = tot[(tot.female_share < GENDER_SHARE_RANGE[0]) | (tot.female_share > GENDER_SHARE_RANGE[1])].reset_index()
for _, r in odd.iterrows():
    flags.append({"check": "Unusual female share", "state": r.state, "year": r.year, "gender": "both",
                  "value": f"{r.female_share:.0%} female", "note": f"Outside {GENDER_SHARE_RANGE[0]:.0%}-{GENDER_SHARE_RANGE[1]:.0%}"})
record("Female share outside 35%-55% of a state's enrolment", "PASS" if odd.empty else "REVIEW",
       f"{len(odd)} state-years: " + ", ".join(sorted(odd.state.unique())))

# 7. Metadata vs content
with open(PATH, encoding="utf-8") as f:
    title = f.readlines()[1]
looks_pct = "Percentage" in title
max_total = int(df.total.max())
record("File title matches the values", "FAIL" if looks_pct and max_total > 100 else "PASS",
       f"Title says 'Percentage Distribution' but values are counts up to {max_total:,}" if looks_pct and max_total > 100 else "consistent")

# Outputs
os.makedirs("reports", exist_ok=True)
pd.DataFrame(flags).to_csv("reports/flagged_rows.csv", index=False)
lines = ["# Data-quality report: Nigeria primary school enrolment, 2015-2016", "",
         f"Rows in file (after metadata): {len(df)}. States found: {n_states}.", "",
         "| Check | Result | Detail |", "|---|---|---|"]
lines += [f"| {n} | {s} | {d} |" for n, s, d in results]
open("reports/dq_report.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\n{len(flags)} flagged rows written to reports/flagged_rows.csv")
