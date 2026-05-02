"""Unit tests for budget_assistant/parsers/paypal.py"""
import os
from decimal import Decimal

from budget_assistant.parsers.paypal import PayPalParser


class TestPayPalParser:
    def test_parse_march_statement_totals(self):
        test_pdf = os.path.join(os.path.dirname(__file__), "test_data", "statements", "statement-2026-03-15.pdf")
        parser = PayPalParser(test_pdf, "paypal-7513")

        transactions = parser.parse()
        purchases = [t for t in transactions if t.description.startswith("Purchase:")]
        payments = [t for t in transactions if t.description.startswith("Payment:")]
        refunds = [t for t in transactions if t.description.startswith("Refund:")]

        assert len(purchases) > 0
        assert sum(t.amount for t in purchases) == Decimal("7633.19")
        assert len(payments) == 1
        assert payments[0].amount == Decimal("-2535.13")
        assert len(refunds) == 1
        assert refunds[0].amount == Decimal("-258.82")

    def test_parse_april_statement_total_purchases(self):
        test_pdf = os.path.join(os.path.dirname(__file__), "test_data", "statements", "statement-2026-04-14.pdf")
        parser = PayPalParser(test_pdf, "paypal-7513")

        transactions = parser.parse()
        purchases = [t for t in transactions if t.description.startswith("Purchase:")]
        payments = [t for t in transactions if t.description.startswith("Payment:")]
        refunds = [t for t in transactions if t.description.startswith("Refund:")]

        assert len(purchases) > 0
        assert sum(t.amount for t in purchases) == Decimal("5842.25")
        assert len(payments) == 1
        assert payments[0].amount == Decimal("-7374.37")
        assert len(refunds) == 0

    def test_all_transaction_dates_are_2026(self):
        test_pdf = os.path.join(os.path.dirname(__file__), "test_data", "statements", "statement-2026-03-15.pdf")
        parser = PayPalParser(test_pdf, "paypal-7513")

        transactions = parser.parse()

        assert all(t.date.year == 2026 for t in transactions)
