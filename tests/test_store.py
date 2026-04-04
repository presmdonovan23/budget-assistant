"""Unit tests for budget_assistant.store."""

import json

import pytest

from budget_assistant import store


def test_save_month(isolated_store_workspace, sample_transactions_march):
    path = store.save_month("2026-03", sample_transactions_march)

    assert path == store._month_path("2026-03")
    assert path.exists()
    assert path.resolve() == (isolated_store_workspace / "data" / "2026-03.json").resolve()

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "transactions" in data
    assert len(data["transactions"]) == 3
    assert data["transactions"][0]["description"] == "WHOLE FOODS 1234"


def test_load_month(isolated_store_workspace, sample_transactions_march):
    store.save_month("2026-03", sample_transactions_march)

    transactions = store.load_month("2026-03")

    assert len(transactions) == 3
    assert transactions[0].description == "WHOLE FOODS 1234"


def test_load_month_raises_for_missing_month(isolated_store_workspace):
    with pytest.raises(FileNotFoundError, match="No data found for month: 2026-03"):
        store.load_month("2026-03")


def test_load_months(isolated_store_workspace, sample_transactions_march, sample_transactions_april):
    store.save_month("2026-03", sample_transactions_march)
    store.save_month("2026-04", sample_transactions_april)

    monthly_data = store.load_months()

    assert "2026-03" in monthly_data
    assert "2026-04" in monthly_data
    assert len(monthly_data["2026-03"]) == 3
    assert len(monthly_data["2026-04"]) == 2


def test_load_months_applies_start_and_end_filters(
    isolated_store_workspace,
    sample_transactions_march,
    sample_transactions_april,
):
    store.save_month("2026-02", sample_transactions_march)
    store.save_month("2026-03", sample_transactions_march)
    store.save_month("2026-04", sample_transactions_april)

    monthly_data = store.load_months(start_month="2026-03", end_month="2026-03")

    assert monthly_data == {"2026-03": sample_transactions_march}


def test_load_months_raises_when_data_directory_is_missing(store_workspace_without_data_dir):
    with pytest.raises(FileNotFoundError, match="No data directory found"):
        store.load_months()


@pytest.mark.parametrize("month", ["2026-3", "03-2026", "march-2026"])
def test_month_path_rejects_invalid_month_format(isolated_store_workspace, month):
    with pytest.raises(ValueError, match=r"month must be in the format"):
        store._month_path(month)