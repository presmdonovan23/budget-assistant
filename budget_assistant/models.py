from dataclasses import dataclass, field, asdict
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from typing import Optional
import json

@dataclass
class Transaction:
    date: date
    description: str
    merchant: str
    amount: Decimal
    account: str
    source_file: str
    category: Optional[str] = field(default=None)

    def __post_init__(self):
        if isinstance(self.date, str):
            # Attempt to parse date string in ISO format (YYYY-MM-DD).
            try:
                self.date = date.fromisoformat(self.date)
            # If ISO format parsing fails, attempt to parse MM/DD/YY format.
            except ValueError as exc:
                try:
                    self.date = self.format_MMDDYY(self.date)
                except ValueError as exc2:
                    raise ValueError("date must be ISO format YYYY-MM-DD or MM/DD/YY") from exc2
        elif not isinstance(self.date, date):
            raise TypeError("date must be a datetime.date or ISO date string")

        try:
            self.amount = Decimal(str(self.amount))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise TypeError("amount must be a valid Decimal-compatible value") from exc

        for field_name in ("description", "merchant", "account", "source_file"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")
            if not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if self.category is not None:
            if not isinstance(self.category, str):
                raise TypeError("category must be a string or None")
            if not self.category.strip():
                raise ValueError("category must be non-empty when provided")
            
    def format_MMDDYY(self, date_str: str) -> str:
        date_pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(\d{2}).*$"  # MM/DD/YY format
        MM, DD, YY = re.match(date_pattern, date_str).groups()
        return date(2000 + int(YY), int(MM), int(DD)).isoformat()
    

@dataclass
class MonthlyTransactions:
    month: str  # e.g., "2026-03"
    accounts: list[str]
    transactions: list[Transaction]

@dataclass
class HistoricalTransactions:
    monthly_transactions: list[MonthlyTransactions]

    
class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)          # "12.34" — preserves precision
        if isinstance(obj, date):
            return obj.isoformat()   # "2026-03-15"
        return super().default(obj)
    

def transaction_from_dict(d: dict) -> Transaction:
    return Transaction(
        date=date.fromisoformat(d["date"]),
        description=d["description"],
        merchant=d["merchant"],
        amount=Decimal(d["amount"]),   # from the string "12.34"
        account=d["account"],
        source_file=d["source_file"],
        category=d.get("category"),
    )