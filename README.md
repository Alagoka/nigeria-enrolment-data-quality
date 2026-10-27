# Catching bad school data before it drives decisions

## The problem

Governments and education organisations use school enrolment tables to decide where teachers, books and money should go. If a state's numbers are missing, mislabelled or suddenly swing by hundreds of percent, those decisions get made on bad information, and nobody notices because the table looks tidy.

I wanted to see how much could be caught automatically. So I took a real government table, the National Bureau of Statistics' primary school enrolment for Nigeria's states in 2015 and 2016, and wrote a set of checks that anyone can rerun. They tell you what looks wrong and why it matters, in plain language.

## What I found

- **A state is missing for a whole year.** Borno has no 2015 figures. The national total also leaves it out, so the gap runs all the way up, and the file never says why.
- **Some numbers swing too much to be believed without a second look.** 20 state-and-gender figures changed by more than 40% in one year. Osun goes from about 13,000 girls to about 62,000. Benue and Cross River fall by more than 60%. Kaduna and Kwara roughly triple. A change that big usually means a counting or reporting change, or an entry error, not a sudden shift in children.
- **A few gender splits look unusual.** Kebbi, Zamfara and Abia have female shares outside the normal range. These may be real regional patterns, so I flag them for a person to review and don't call them errors.
- **The file describes itself wrongly.** It is titled "Percentage Distribution of Enrolment", but the values are headcounts of up to 3.2 million. Someone who trusts the title could read the data completely wrong.
- **What was clean:** no empty cells, no duplicate rows, no zero or negative values, and consistent state names and labels.

I can't say which of the flagged swings are genuine errors, because I don't have the original source forms. The point is to show where someone should look first, and why.

## How the checks work

`src/dq_checks.py` runs 13 checks in five groups:

| Group | What it asks |
|---|---|
| Completeness | Are any cells empty? Are all 36 states plus the FCT present, for every year and gender? |
| Consistency | Any duplicates, odd labels, stray spaces, or zero and negative totals? |
| Reconciliation | Does the national figure equal the sum of the states? |
| Plausibility | Did any state change by more than 40% in a year? Is any state's female share outside 35-55%? |
| Metadata | Does the file's title match what the numbers really are? |

The 40% and 35-55% limits are my own judgement calls. They sit at the top of the script, so anyone can change them.

## Run it yourself

```
pip install -r requirements.txt
python src/dq_checks.py
```

It reads the file in `data/` and writes two outputs to `reports/`: a summary table and a list of every flagged record.

## How the repo is arranged

```
.
├── README.md                  <- you are here
├── requirements.txt           <- the one library needed (pandas)
├── data/
│   └── primary_school_enrollment_2015_2016.csv   <- original file, unchanged
├── src/
│   └── dq_checks.py           <- the checks
└── reports/
    ├── dq_report.md           <- summary of every check
    └── flagged_rows.csv       <- every record that needs a human look
```

## Limits

There are only two years of data, so "year-on-year" is a single comparison. The thresholds are judgement calls. And a flagged number is a question, not a verdict.

## Data source

National Bureau of Statistics, Nigeria (2018), *Percentage Distribution of Enrolment in Primary Schools by State, Year and Sex, 2015-2016*, obtained through Open Africa.
