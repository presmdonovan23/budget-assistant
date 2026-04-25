"""
Unit tests for budget_assistant/parsers/chase.py
"""
import pytest
from decimal import Decimal

from budget_assistant.parsers.chase import ChaseParser
from budget_assistant.models import Transaction


class TestChaseParser:
    """Test suite for ChaseParser class"""

    def test_init(self):
        """Test parser initialization"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")
        assert parser.file_path == "/path/to/file.pdf"
        assert parser.account_id == "test-account"
        assert parser.text == ""
        assert parser.statement_year is None

    def test_extract_statement_year_from_statement_date(self):
        """Test extracting year from 'Statement Date: MM/DD/YY' pattern"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")

        # Mock text with statement date pattern
        parser.text = "Some text Statement Date: 04/19/26 More text"

        parser._extract_statement_year()
        assert parser.statement_year == "26"

    def test_extract_statement_year_from_opening_closing_date(self):
        """Test extracting year from 'Opening/Closing Date MM/DD/YY - MM/DD/YY' pattern"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")

        # Mock text with opening/closing date pattern
        parser.text = "Some text Opening/Closing Date 03/20/26 - 04/19/26 More text"

        parser._extract_statement_year()
        assert parser.statement_year == "26"

    def test_extract_statement_year_default(self):
        """Test default year extraction when patterns not found"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")

        # Mock text without date patterns
        parser.text = "Some text without date patterns"

        parser._extract_statement_year()
        assert parser.statement_year == "26"  # Default fallback

    def test_parse_full_flow(self):
        """Test full parsing flow with actual PDF content"""
        import os
        
        # Use the actual test PDF file
        test_pdf_path = os.path.join(os.path.dirname(__file__), "test_data", "statements", "20260327-statements-7256-.pdf")
        
        parser = ChaseParser(test_pdf_path, "chase-7256")
        transactions = parser.parse()

        # Should have 3 transactions: all purchases
        assert len(transactions) == 3

        # Check that all are purchases
        purchases = [t for t in transactions if "Purchase:" in t.description]
        assert len(purchases) == 3
        
        # Check total amount matches expected
        total_amount = sum(t.amount for t in purchases)
        assert total_amount == Decimal("182.80")

        # Check specific transactions
        descriptions = [t.description for t in purchases]
        assert "Purchase: COMCAST / XFINITY 800-266-2278 NH" in descriptions
        assert "Purchase: ALDI 73115 WALPOLE WALPOLE MA" in descriptions
        assert "Purchase: SWEETGREEN BOY BOSTON MA" in descriptions

    def test_extract_transaction_lines_simple(self):
        """Test extracting transaction lines from simple text"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")

        section_text = """03/20 AMAZON MKTPL*BD2SD2721 Amzn.com/bill WA 35.05
03/22 AMAZON MKTPL*B51LL0511 Amzn.com/bill WA 29.94"""

        lines = parser._extract_transaction_lines(section_text)

        assert len(lines) == 2
        assert lines[0] == ("03/20", "AMAZON MKTPL*BD2SD2721 Amzn.com/bill WA", "35.05")
        assert lines[1] == ("03/22", "AMAZON MKTPL*B51LL0511 Amzn.com/bill WA", "29.94")

    def test_extract_transaction_lines_with_order_numbers(self):
        """Test extracting transaction lines that include order number metadata"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")

        section_text = """03/20 AMAZON MKTPL*BD2SD2721 Amzn.com/bill WA 35.05
Order Number 111-2891072-7442622
03/22 AMAZON MKTPL*B51LL0511 Amzn.com/bill WA 29.94
Order Number 113-9117723-3967429"""

        lines = parser._extract_transaction_lines(section_text)

        # Should skip the "Order Number" lines
        assert len(lines) == 2
        assert lines[0] == ("03/20", "AMAZON MKTPL*BD2SD2721 Amzn.com/bill WA", "35.05")
        assert lines[1] == ("03/22", "AMAZON MKTPL*B51LL0511 Amzn.com/bill WA", "29.94")

    def test_extract_transaction_lines_with_commas_in_amount(self):
        """Test extracting transaction lines with comma separators in amounts"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")

        section_text = "03/20 LARGE PURCHASE Amzn.com/bill WA 1,234.56"

        lines = parser._extract_transaction_lines(section_text)

        assert len(lines) == 1
        # Note: commas are stripped from amounts
        assert lines[0] == ("03/20", "LARGE PURCHASE Amzn.com/bill WA", "1234.56")

    def test_get_purchases_section_not_found(self):
        """Test handling when PURCHASE section is not found"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")
        parser.text = "Some text without PURCHASE section"
        parser.statement_year = "26"

        purchases = parser.get_purchases()

        assert purchases == []

    def test_get_payments_and_credits_section_not_found(self):
        """Test handling when PAYMENTS AND OTHER CREDITS section is not found"""
        parser = ChaseParser("/path/to/file.pdf", "test-account")
        parser.text = "Some text without PAYMENTS section"
        parser.statement_year = "26"

        credits = parser.get_payments_and_credits()

        assert credits == []

    def test_transaction_type_classification_purchases(self):
        """Test that purchase transactions get correct prefix using actual PDF"""
        import os
        
        # Use the actual test PDF file (which has purchases)
        test_pdf_path = os.path.join(os.path.dirname(__file__), "test_data", "statements", "20260327-statements-7256-.pdf")
        
        parser = ChaseParser(test_pdf_path, "chase-7256")
        transactions = parser.parse()

        purchases = [t for t in transactions if "Purchase:" in t.description]
        assert len(purchases) == 3  # The test PDF has 3 purchases
        for purchase in purchases:
            assert purchase.description.startswith("Purchase:")

    def test_transaction_type_classification_payments(self):
        """Test that payment transactions get correct prefix using actual PDF"""
        import os
        
        # Use the second test PDF file (which has payments and credits)
        test_pdf_path = os.path.join(os.path.dirname(__file__), "test_data", "statements", "20260419-statements-5450-.pdf")
        
        parser = ChaseParser(test_pdf_path, "chase-5450")
        transactions = parser.parse()

        payments = [t for t in transactions if "Payment:" in t.description]
        assert len(payments) == 1  # The test PDF has 1 payment
        assert payments[0].description.startswith("Payment:")

    def test_transaction_type_classification_refunds(self):
        """Test that refund transactions get correct prefix using actual PDF"""
        import os
        
        # Use the second test PDF file (which has refunds)
        test_pdf_path = os.path.join(os.path.dirname(__file__), "test_data", "statements", "20260419-statements-5450-.pdf")
        
        parser = ChaseParser(test_pdf_path, "chase-5450")
        transactions = parser.parse()

        refunds = [t for t in transactions if "Refund:" in t.description]
        assert len(refunds) == 1  # The test PDF has 1 refund
        assert refunds[0].description.startswith("Refund:")

    def test_date_formatting_with_year(self):
        """Test that dates are properly formatted with the extracted year using actual PDF"""
        from datetime import date
        import os
        
        # Use the first test PDF file
        test_pdf_path = os.path.join(os.path.dirname(__file__), "test_data", "statements", "20260327-statements-7256-.pdf")
        
        parser = ChaseParser(test_pdf_path, "chase-7256")
        transactions = parser.parse()

        assert len(transactions) == 3
        # Check that dates are properly parsed as date objects
        for transaction in transactions:
            assert isinstance(transaction.date, date)
            # All transactions should be in 2026
            assert transaction.date.year == 2026