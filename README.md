# Budget Assistant

A personal spending analysis tool that processes monthly account statements and produces reports on income, spending, and financial patterns over time.

## Overview

Budget Assistant is a Python CLI application built for personal use. It ingests monthly account statements (PDF or CSV), categorizes transactions, flags anomalies, and produces plain-text reports. It is not designed to generalize to arbitrary users or financial setups.

## Features

### Monthly Statement Analysis
Given one or more monthly statements, the tool produces a report containing:

- **Total income** — sum of all incoming transactions for the period
- **Total spending** — sum of all outgoing transactions for the period
- **Spending by category** — breakdowns for:
  - Groceries
  - Restaurants
  - Subscriptions
  - Utilities / bills (e.g. gas bill tracked individually over time)
  - Other notable recurring expenses
- **Spending anomalies** — rules-based detection of:
  - Subscription price changes
  - Unusually high-dollar transactions (above configurable thresholds)
  - Other prescriptive anomaly rules

### Long-Term Trend Analysis
Given a collection of monthly reports, the tool summarizes spending patterns over time:

- Total spend trends month-over-month
- Category-level trends (groceries, restaurants, subscriptions, bills, etc.)
- Notable changes or shifts in spending behavior

## Input Formats

- **PDF** — monthly account statements exported from a bank or credit card provider
- **CSV** — transaction exports from a bank or credit card provider

## Output

Reports are produced as plain text. Visualization support (charts, graphs) is planned for a future version.

## Tech Stack

- **Python 3** — primary implementation language
- [`pdfplumber`](https://github.com/jsvine/pdfplumber) — PDF table extraction
- CSV parsing via Python standard library
- YAML config via `PyYAML`

## Project Structure (Planned)

```
budget-assistant/
├── data/
│   ├── statements/          # Raw PDFs/CSVs — gitignored, organized by bank
│   └── transactions/        # Parsed JSON files — gitignored (one file per YYYY-MM)
├── reports/                 # Text report outputs — gitignored
├── budget_assistant/
│   ├── models.py            # Transaction dataclass + JSON serialization
│   ├── store.py             # Read/write transactions/YYYY-MM.json
│   ├── parsers/
│   │   ├── base.py          # Abstract parser interface
│   │   ├── bofa.py          # Bank of America
│   │   ├── chase.py         # Chase + Southwest (same issuer)
│   │   ├── amex.py          # American Express
│   │   └── paypal.py        # PayPal
│   ├── categorizer.py       # Keyword-matching against config/categories.yaml
│   ├── anomalies.py         # Rules-based anomaly detection
│   ├── reporter.py          # Monthly report text generation
│   └── trends.py            # Multi-month trend summarization
├── config/
│   ├── categories.yaml      # Merchant keyword → category mappings
│   └── rules.yaml           # Anomaly thresholds, tracked subscriptions/expenses
├── main.py                  # CLI entry point
└── README.md
```

## Usage (Planned)

```bash
# Parse a statement and persist transactions to the JSON store
python main.py parse data/statements/bofa/2026-03.pdf --source bofa --account bofa-checking

# Generate a monthly report
python main.py report --month 2026-03

# Summarize trends across a date range
python main.py trends --from 2026-01 --to 2026-03
```

## Configuration

All rules live in `config/` and are tailored for personal use rather than designed to generalize:

- **`categories.yaml`** — ordered list of keyword → category mappings. Matching is case-insensitive substring; first match wins.
- **`rules.yaml`** — anomaly thresholds (e.g. high-dollar cutoff), tracked subscription merchants, and other per-expense configuration.

## Testing

The test suite requires sample statement files that are not included in the repository for privacy reasons. To run the full test suite:

1. Obtain sample PDF statements for each supported parser (Chase, BofA, Amex, PayPal)
2. Place them in `tests/test_data/statements/` (create subdirectories as needed for different parsers)
3. Update test files to reference your specific sample files

Without these statement files, unit tests that validate PDF parsing will fail. The test data directory is gitignored to prevent accidental inclusion of sensitive financial documents.

```bash
# Run tests (will fail without test statement files)
python -m pytest tests/

# Run integration test with sample statements
python test_chase.py
```
