from pathlib import Path
import json
import re
import yaml
from typing import Optional
from dataclasses import asdict, dataclass

from budget_assistant.models import (
    MonthlyTransactions,
    Transaction,
    TransactionEncoder,
    HistoricalTransactions,
    transaction_from_dict
)

def _validate_month(month: str) -> bool:
    with open("config/storage.yaml", "r") as f:
        config = yaml.safe_load(f)
        month_pattern = config.get("month_pattern", r"^\d{4}-\d{2}$")
    
    if not re.match(month_pattern, month):
        raise ValueError(f"month must be in the format: {month_pattern}")

def _month_path(month: str) -> Path:
    _validate_month(month)
    return Path(f"data/{month}.json")

def save_month(month: str, transactions: list[Transaction]) -> Path:
    path = _month_path(month)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "transactions": [asdict(transaction) for transaction in transactions]
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, cls=TransactionEncoder, indent=2)

    return path

def load_month(month: str) -> list[Transaction]:
    path = _month_path(month)
    if not path.exists():
        raise FileNotFoundError(f"No data found for month: {month}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [transaction_from_dict(t) for t in data["transactions"]]

def load_months(start_month: Optional[str] = None, end_month: Optional[str] = None) -> dict[str, list[Transaction]]:
    data_dir = Path("data")
    if not data_dir.exists():
        raise FileNotFoundError("No data directory found")

    monthly_transactions = {}
    for file in data_dir.glob("*.json"):
        month = file.stem
        if start_month and month < start_month:
            continue
        if end_month and month > end_month:
            continue

        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            transactions = [transaction_from_dict(t) for t in data["transactions"]]
            monthly_transactions[month] = transactions

    return monthly_transactions

if __name__ == "__main__":
    # Example usage
    transactions = [
        Transaction(
            date="2026-03-15",
            description="WHOLE FOODS 1234",
            merchant="whole foods",
            amount="123.45",
            account="bofa-checking",
            source_file="statement.pdf",
            category="groceries"
        )
    ]
    save_month("2026-03", transactions)