# Budget Assistant — Technical Plan

## Context & Constraints
- 1-2 checking accounts + 4-5 credit cards
- Banks: Bank of America, Chase, American Express, Southwest (Chase-issued), PayPal
- Bespoke PDF parsers per bank are acceptable
- Categorization: fully deterministic keyword rules (config file)
- Persistence: JSON files (no SQLite)
- Anomaly rules:
  1. Transaction over $X (configurable threshold)
  2. Subscription price change vs prior month
  3. Merchant never seen in prior statements

---

## TL;DR

Two-phase CLI:
1. `parse` ingests raw statements into a normalized per-month transaction JSON store
2. `report` and `trends` commands operate on that store

Bespoke parsers per bank, deterministic keyword categorization via YAML config, rules-based anomaly detection.

---

## Data Model (`models.py`)

Central `Transaction` dataclass:
- `date: date`
- `description: str` — raw text from statement
- `merchant: str` — cleaned/normalized name
- `amount: Decimal` — positive = spend (debit), negative = income/refund/payment
- `account: str` — e.g. `"bofa-checking"`, `"chase-sapphire"`
- `category: Optional[str]` — assigned by categorizer
- `source_file: str` — which PDF/CSV this came from

Also a `MonthlyTransactions` wrapper holding a list of `Transaction` plus metadata (month, accounts included).

---

## Project Structure

```
budget-assistant/
├── data/
│   ├── statements/          # Raw PDFs/CSVs — gitignored, organized by bank
│   └── transactions/        # Parsed JSON files — gitignored
│       ├── 2026-01.json
│       └── 2026-02.json
├── reports/                 # Text report outputs — gitignored
├── budget_assistant/
│   ├── models.py            # Transaction dataclass + serialization
│   ├── store.py             # Read/write transactions/YYYY-MM.json
│   ├── parsers/
│   │   ├── base.py          # Abstract base parser interface
│   │   ├── bofa.py          # Bank of America (checking + credit)
│   │   ├── chase.py         # Chase + Southwest (same issuer, same format)
│   │   ├── amex.py          # American Express
│   │   └── paypal.py        # PayPal (likely CSV export)
│   ├── categorizer.py       # Keyword-matching against config/categories.yaml
│   ├── anomalies.py         # Three rules: high-dollar, subscription delta, new merchant
│   ├── reporter.py          # Monthly report text generation
│   └── trends.py            # Multi-month trend summarization
├── config/
│   ├── categories.yaml      # Merchant keyword → category mappings
│   └── rules.yaml           # Anomaly thresholds, tracked subscriptions, tracked expenses
├── main.py                  # CLI entry point (argparse)
└── requirements.txt
```

---

## Phase 1 — Foundation

Steps (can be done in parallel):
1. Define `Transaction` dataclass in `models.py` + JSON serialization/deserialization (using `dataclasses` + custom encoder for `Decimal` and `date`)
2. Implement `store.py`: `load_month(YYYY-MM) -> list[Transaction]`, `save_month(YYYY-MM, transactions)`, `load_all() -> dict[str, list[Transaction]]`
3. Scaffold `config/categories.yaml` and `config/rules.yaml` with initial rules

---

## Phase 2 — Parsers

Each parser implements the base interface: `parse(file_path, account_id) -> list[Transaction]`

4. `base.py` — abstract base class with the `parse` interface
5. `bofa.py` — parse BofA PDF with `pdfplumber`; extract table rows (date, description, amount)
6. `chase.py` — parse Chase PDF; Southwest uses the same format so it reuses this parser
7. `amex.py` — parse Amex PDF
8. `paypal.py` — parse PayPal CSV (simpler than PDFs)

> **Note:** PDF parsing is inherently exploratory. Each parser will require inspecting a real sample statement to confirm the table structure before writing the extractor. Plan for iteration here.

---

## Phase 3 — Categorization

9. `categorizer.py`: loads `config/categories.yaml`, iterates rules in order, matches keywords against `merchant` (case-insensitive substring). First match wins. Returns `"uncategorized"` if no rule matches.

`categories.yaml` structure:
```yaml
- category: groceries
  keywords: [whole foods, trader joe's, kroger, aldi, publix]
- category: restaurants
  keywords: [mcdonald's, chipotle, doordash, uber eats, grubhub]
- category: subscriptions
  keywords: [netflix, spotify, hulu, apple.com/bill, amazon prime]
- category: gas_bill
  keywords: [national grid, peoples gas, atmos]
```

---

## Phase 4 — Anomaly Detection

10. `anomalies.py`: takes a list of current-month `Transaction`s + prior months' stored data, returns a list of `Anomaly` objects (`type`, `transaction`, `detail: str`)

Three rules:
- **HighDollarRule**: `amount > rules.yaml:high_dollar_threshold` — optionally configurable per category
- **SubscriptionPriceChangeRule**: for each subscription merchant, compare current month amount vs median of same merchant in prior months; flag if delta exceeds a configurable tolerance (e.g. $1.00)
- **NewMerchantRule**: derive known merchant set from all prior months' stored transactions; flag any current-month merchant not in that set

---

## Phase 5 — Reporting

11. `reporter.py`: given a month's transactions + anomalies, produces a structured plain-text report:
    - Header: month, accounts included
    - Total income / total spending
    - Spending by category (sorted by amount descending)
    - Tracked specific expenses by name (e.g. gas bill)
    - Anomalies section

12. `trends.py`: given a dict of month → transactions, produces:
    - Month-by-month total spend table
    - Category totals per month
    - Notable observations (month with highest spend, fastest-growing category, etc.)

---

## Phase 6 — CLI

13. `main.py` with `argparse` subcommands:
    - `parse <file> --source <bofa|chase|amex|paypal> --account <account-id>` — parse statement and persist to JSON store
    - `report --month YYYY-MM [--output reports/]` — generate monthly report
    - `trends --from YYYY-MM --to YYYY-MM [--output reports/]` — generate trend report

---

## Verification

1. Unit tests for `categorizer.py` — keyword matching, case-insensitivity, first-match-wins
2. Unit tests for each anomaly rule with synthetic transaction lists
3. Integration test: run `parse` on a sample statement, verify JSON file written correctly
4. Integration test: run `report` on a known month, spot-check totals and category sums manually
5. Manual review of one real statement per bank to confirm parser output before trusting any reports

---

## Decisions

- Southwest is Chase-issued → `chase.py` handles both
- Positive amount = spending, negative = income/refund (consistent sign convention across all parsers)
- JSON persistence scoped to one file per month (`data/transactions/YYYY-MM.json`)
- Config in YAML (more readable than Python dicts for keyword lists)
- `pdfplumber` preferred over `pypdf` for table extraction from bank PDFs
- LLM-assisted categorization is out of scope for v1
- Visualization is out of scope for v1

---

## Open Questions

- **PayPal format**: PDF statements or CSV exports? CSV would be significantly simpler to parse — worth confirming before writing `paypal.py`.
- **Amount sign normalization**: banks vary in sign conventions and column structure (e.g. separate debit/credit columns vs signed amounts). Each parser is responsible for normalizing to the shared convention.
