"""Unit tests for budget_assistant/parsers/bofa.py"""
import os
from decimal import Decimal

from budget_assistant.parsers.bofa import BofaParser


class TestBofaParser:
    def test_parse_january_statement_totals(self):
        """Test parsing eStmt_2026-01-22 with expected totals"""
        test_pdf = os.path.join(os.path.dirname(__file__), "test_data", "statements", "eStmt_2026-01-22.pdf")
        parser = BofaParser(test_pdf, "bofa-checking")

        transactions = parser.parse()

        deposits = [t for t in transactions if t.description.startswith("Deposit:")]
        withdrawals = [t for t in transactions if t.description.startswith("Withdrawal:")]
        checks = [t for t in transactions if t.description.startswith("Check:")]

        assert sum(t.amount for t in deposits) == Decimal("27220.00")
        assert sum(t.amount for t in withdrawals) == Decimal("-17931.23")
        assert sum(t.amount for t in checks) == Decimal("-1441.24")

    def test_parse_february_statement_totals(self):
        """Test parsing eStmt_2026-02-19 with expected totals"""
        test_pdf = os.path.join(os.path.dirname(__file__), "test_data", "statements", "eStmt_2026-02-19.pdf")
        parser = BofaParser(test_pdf, "bofa-checking")

        transactions = parser.parse()

        deposits = [t for t in transactions if t.description.startswith("Deposit:")]
        withdrawals = [t for t in transactions if t.description.startswith("Withdrawal:")]
        checks = [t for t in transactions if t.description.startswith("Check:")]

        assert sum(t.amount for t in deposits) == Decimal("7969.03")
        assert sum(t.amount for t in withdrawals) == Decimal("-13922.09")
        assert sum(t.amount for t in checks) == Decimal("-340.00")

    def test_parse_march_statement_totals(self):
        """Test parsing eStmt_2026-03-23 with expected totals"""
        test_pdf = os.path.join(os.path.dirname(__file__), "test_data", "statements", "eStmt_2026-03-23.pdf")
        parser = BofaParser(test_pdf, "bofa-checking")

        transactions = parser.parse()

        deposits = [t for t in transactions if t.description.startswith("Deposit:")]
        withdrawals = [t for t in transactions if t.description.startswith("Withdrawal:")]
        checks = [t for t in transactions if t.description.startswith("Check:")]

        assert sum(t.amount for t in deposits) == Decimal("26592.75")
        assert sum(t.amount for t in withdrawals) == Decimal("-20317.59")
        assert sum(t.amount for t in checks) == Decimal("-510.00")