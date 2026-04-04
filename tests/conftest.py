# tests/conftest.py
from datetime import date
from decimal import Decimal

import pytest

from budget_assistant.models import Transaction

@pytest.fixture
def sample_transaction_march_1():
    return Transaction(
        date=date(2026, 3, 15),
        description="WHOLE FOODS 1234",
        merchant="whole foods",
        amount=Decimal("123.45"),
        account="bofa-checking",
        source_file="statement.pdf",
        category="groceries"
    )

@pytest.fixture
def sample_transaction_march_2():
    return Transaction(
        date=date(2026, 3, 16),
        description="STARBUCKS 5678",
        merchant="starbucks",
        amount=Decimal("4.56"),
        account="bofa-checking",
        source_file="statement.pdf",
        category="coffee"
    )

@pytest.fixture
def sample_transaction_march_3():
    return Transaction(
        date=date(2026, 3, 17),
        description="AMAZON MKTPLACE PMTS",
        merchant="amazon",
        amount=Decimal("78.90"),
        account="bofa-checking",
        source_file="statement.pdf",
        category="shopping"
    )

@pytest.fixture
def sample_transaction_april_1():
    return Transaction(
        date=date(2026, 4, 1),
        description="UBER TRIP",
        merchant="uber",
        amount=Decimal("15.00"),
        account="bofa-checking",
        source_file="statement.pdf",
        category="transportation"
    )

@pytest.fixture
def sample_transaction_april_2():
    return Transaction(
        date=date(2026, 4, 2),
        description="LYFT RIDE",
        merchant="lyft",
        amount=Decimal("20.00"),
        account="bofa-checking",
        source_file="statement.pdf",
        category="transportation"
    )

@pytest.fixture
def sample_transactions_march(sample_transaction_march_1, sample_transaction_march_2, sample_transaction_march_3):
    return [
        sample_transaction_march_1,
        sample_transaction_march_2,
        sample_transaction_march_3
    ]

@pytest.fixture
def sample_transactions_april(sample_transaction_april_1, sample_transaction_april_2):
    return [
        sample_transaction_april_1,
        sample_transaction_april_2
    ]


@pytest.fixture
def isolated_store_workspace(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "storage.yaml").write_text(
        "data_dir: ignored-in-tests\nmonth_pattern: '^\\d{4}-\\d{2}$'\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def store_workspace_without_data_dir(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "storage.yaml").write_text(
        "data_dir: ignored-in-tests\nmonth_pattern: '^\\d{4}-\\d{2}$'\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path
