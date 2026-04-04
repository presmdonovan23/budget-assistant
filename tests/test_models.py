"""
This is a suite of unit tests for budget_assistant/models.py. It uses pytest as the testing framework.
"""
from budget_assistant.models import MonthlyTransactions, Transaction, TransactionEncoder, transaction_from_dict
from datetime import date
from decimal import Decimal
from dataclasses import asdict
import json
import pytest


def test_transaction_creation():

    t = Transaction(
        date=date(2026, 3, 15),
        description="Grocery shopping",
        merchant="Supermarket",
        amount=Decimal("123.45"),
        account="Checking",
        source_file="transactions.csv",
        category="Groceries"
    )

    assert t.date == date(2026, 3, 15)
    assert t.description == "Grocery shopping"
    assert t.merchant == "Supermarket"
    assert t.amount == Decimal("123.45")
    assert t.account == "Checking"
    assert t.source_file == "transactions.csv"
    assert t.category == "Groceries"

def test_transaction_creation_without_date():
    with pytest.raises(TypeError):
        t = Transaction(
            description="Grocery shopping",
            merchant="Supermarket",
            amount=Decimal("123.45"),
            account="Checking",
            source_file="transactions.csv",
            category="Groceries"
        )

def test_transaction_creation_without_category():
    t = Transaction(
        date=date(2026, 3, 15),
        description="Grocery shopping",
        merchant="Supermarket",
        amount=Decimal("123.45"),
        account="Checking",
        source_file="transactions.csv"
    )

    assert t.category is None

def test_transaction_creation_with_invalid_amount():
    with pytest.raises(TypeError):
        t = Transaction(
            date=date(2026, 3, 15),
            description="Grocery shopping",
            merchant="Supermarket",
            amount="not a number",  # Invalid amount
            account="Checking",
            source_file="transactions.csv",
            category="Groceries"
        )

def test_transaction_creation_with_string_amount_coerces_to_decimal():
    t = Transaction(
        date=date(2026, 3, 15),
        description="Grocery shopping",
        merchant="Supermarket",
        amount="123.45",
        account="Checking",
        source_file="transactions.csv",
        category="Groceries"
    )

    assert t.amount == Decimal("123.45")

def test_transaction_creation_with_iso_date_string_coerces_to_date():
    t = Transaction(
        date="2026-03-15",
        description="Grocery shopping",
        merchant="Supermarket",
        amount=Decimal("123.45"),
        account="Checking",
        source_file="transactions.csv",
        category="Groceries"
    )

    assert t.date == date(2026, 3, 15)

def test_monthly_transactions_creation():
    t1 = Transaction(
        date=date(2026, 3, 15),
        description="Grocery shopping",
        merchant="Supermarket",
        amount=Decimal("123.45"),
        account="Checking",
        source_file="transactions.csv",
        category="Groceries"
    )
    t2 = Transaction(
        date=date(2026, 3, 20),
        description="Gas station",
        merchant="Gas Station",
        amount=Decimal("45.67"),
        account="Credit Card",
        source_file="transactions.csv",
        category="Transportation"
    )

    mt = MonthlyTransactions(
        month="2026-03",
        accounts=["Checking", "Credit Card"],
        transactions=[t1, t2]
    )

    assert mt.month == "2026-03"
    assert mt.accounts == ["Checking", "Credit Card"]
    assert mt.transactions == [t1, t2]

def test_transaction_encoder():
    
    t = Transaction(
        date=date(2026, 3, 15),
        description="Grocery shopping",
        merchant="Supermarket",
        amount=Decimal("123.45"),
        account="Checking",
        source_file="transactions.csv",
        category="Groceries"
    )

    json_str = json.dumps(asdict(t), cls=TransactionEncoder)

    assert '"date": "2026-03-15"' in json_str
    assert '"amount": "123.45"' in json_str

def test_transaction_from_dict():
    
    d = {
        "date": "2026-03-15",
        "description": "Grocery shopping",
        "merchant": "Supermarket",
        "amount": "123.45",
        "account": "Checking",
        "source_file": "transactions.csv",
        "category": "Groceries"
    }
    t = transaction_from_dict(d)
    assert t.date == date(2026, 3, 15)
    assert t.description == "Grocery shopping"
    assert t.merchant == "Supermarket"
    assert t.amount == Decimal("123.45")
    assert t.account == "Checking"
    assert t.source_file == "transactions.csv"
    assert t.category == "Groceries"