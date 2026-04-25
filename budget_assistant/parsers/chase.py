# PDF Parser for Chase credit card statements. Inherits from base Parser and implements parse method to extract transactions from PDF statements.

from datetime import datetime
from decimal import Decimal
import logging
import re
from typing import List

from budget_assistant.models import Transaction
from budget_assistant.parsers.base import Parser
import pdfplumber

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ChaseParser(Parser):
    
    def __init__(self, file_path: str, account_id: str):
        super().__init__(file_path, account_id)
        self.text = ""
        self.statement_year = None
        
    def parse(self) -> List[Transaction]:
        logger.info(f"Parsing Chase statement from file {self.file_path} for account {self.account_id}")
        
        # Extract text from PDF using pdfplumber
        with pdfplumber.open(self.file_path) as pdf:
            # Combine text from all pages
            self.text = '\n'.join([page.extract_text() for page in pdf.pages])
        
        # Extract the statement date to get the year
        self._extract_statement_year()
        
        transactions = []
        
        # Extract purchases
        purchases = self.get_purchases()
        transactions.extend(purchases)
        
        # Extract payments and credits (both payments and refunds)
        payments_and_credits = self.get_payments_and_credits()
        transactions.extend(payments_and_credits)
        
        logger.info(f"Finished parsing Chase statement. Found {len(purchases)} purchases and {len(payments_and_credits)} payments/credits.")
        
        return transactions
    
    def _extract_statement_year(self):
        """Extract the year from the statement date"""
        # Look for patterns like "Statement Date: MM/DD/YY" or in the opening/closing date
        statement_date_pattern = r'Statement Date:\s+(\d{2})/(\d{2})/(\d{2})'
        match = re.search(statement_date_pattern, self.text)
        if match:
            self.statement_year = match.group(3)
        else:
            # Fall back to looking for "Opening/Closing Date MM/DD/YY - MM/DD/YY"
            opening_closing_pattern = r'Opening/Closing Date\s+(\d{2})/(\d{2})/(\d{2})\s*-\s*(\d{2})/(\d{2})/(\d{2})'
            match = re.search(opening_closing_pattern, self.text)
            if match:
                self.statement_year = match.group(6)
        
        if not self.statement_year:
            logger.warning(f"Could not extract statement year from {self.file_path}, defaulting to 26")
            self.statement_year = "26"
        
        logger.info(f"Extracted statement year: {self.statement_year}")
    
    def get_purchases(self) -> List[Transaction]:
        """Extract purchase transactions from PURCHASE section"""
        purchases = []
        
        # Find the PURCHASE section - look for "PURCHASE" heading followed by transactions
        # The section ends either at "PAYMENTS" or at year-to-date totals
        full_year = f"20{self.statement_year}"
        purchase_pattern = rf'PURCHASE\n(.*?)(?:PAYMENTS AND OTHER CREDITS|RETURNS AND OTHER CREDITS|{full_year} Totals|$)'
        purchase_match = re.search(purchase_pattern, self.text, re.DOTALL)
        
        if not purchase_match:
            logger.warning(f"Could not find PURCHASE section in statement {self.file_path}")
            return purchases
        
        purchases_text = purchase_match.group(1)
        
        # Extract transactions from purchases section
        # Format: MM/DD Description... $ Amount
        # Need to handle multi-line descriptions with Order Numbers
        transaction_lines = self._extract_transaction_lines(purchases_text)
        
        for date_str, description, amount_str in transaction_lines:
            try:
                # Format date as MM/DD/YY
                date_with_year = f"{date_str}/{self.statement_year}"
                amount = Decimal(amount_str)
                transaction = Transaction(
                    date=date_with_year,
                    description=f"Purchase: {description}",
                    merchant="unknown",
                    amount=amount,
                    account=self.account_id,
                    source_file=self.file_path
                )
                purchases.append(transaction)
            except Exception as e:
                import traceback
                logger.warning(f"Failed to parse purchase transaction: {date_str} {description} {amount_str}: {e}")
                logger.warning(f"Traceback: {traceback.format_exc()}")
        
        return purchases
        
        return purchases
    
    def get_payments_and_credits(self) -> List[Transaction]:
        """Extract payment and refund transactions from PAYMENTS AND OTHER CREDITS section"""
        transactions = []
        
        # Find the PAYMENTS AND OTHER CREDITS section
        full_year = f"20{self.statement_year}"
        credits_pattern = rf'PAYMENTS AND OTHER CREDITS\n(.*?)(?:PURCHASE|RETURNS AND OTHER CREDITS|{full_year} Totals|$)'
        credits_match = re.search(credits_pattern, self.text, re.DOTALL)
        
        if not credits_match:
            logger.warning(f"Could not find PAYMENTS AND OTHER CREDITS section in statement {self.file_path}")
            return transactions
        
        credits_text = credits_match.group(1)
        
        # Extract transactions from payments and credits section
        transaction_lines = self._extract_transaction_lines(credits_text)
        
        for date_str, description, amount_str in transaction_lines:
            try:
                # Format date as MM/DD/YY
                date_with_year = f"{date_str}/{self.statement_year}"
                amount = Decimal(amount_str)
                
                # Determine transaction type based on description
                if "PAYMENT" in description.upper():
                    prefix = "Payment: "
                else:
                    prefix = "Refund: "
                
                transaction = Transaction(
                    date=date_with_year,
                    description=f"{prefix}{description}",
                    merchant="unknown",
                    amount=amount,
                    account=self.account_id,
                    source_file=self.file_path
                )
                transactions.append(transaction)
            except Exception as e:
                import traceback
                logger.warning(f"Failed to parse payment/credit transaction: {date_str} {description} {amount_str}: {e}")
                logger.warning(f"Traceback: {traceback.format_exc()}")
        
        return transactions
    
    def _extract_transaction_lines(self, section_text: str) -> List[tuple]:
        """
        Extract transaction lines from a section of text.
        Returns list of (date, description, amount) tuples.
        
        Transactions have format:
        MM/DD Description (can span multiple lines with Order Number info) Amount
        """
        transactions = []
        
        # Pattern to match: MM/DD followed by text until we find an amount at the end of a line
        # Account for Order Number lines that follow
        date_pattern = r'^(\d{2}/\d{2})\s+(.+?)\s+(-?[\d,]+\.?\d{2})$'
        lines = section_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip Order Number lines and other metadata
            if line.lower().startswith("order number"):
                continue
            
            # Match line starting with MM/DD
            match = re.match(date_pattern, line)
            
            if match:
                date_str = match.group(1)
                description = match.group(2).strip()
                amount_str = match.group(3)
                
                # Clean up the amount (remove commas)
                amount_str = amount_str.replace(',', '')
                
                transactions.append((date_str, description, amount_str))
        
        return transactions


def main():
    """Example usage of ChaseParser"""
    parser = ChaseParser("/Users/prestondonovan/Documents/budget_data/statements/20260327-statements-7256-.pdf", "chase-7256")
    transactions = parser.parse()
    for t in transactions:
        print(f"{t.date} {t.description[:40]:40} {t.amount:>8}")
    
    print(f"\nTotal transactions: {len(transactions)}")


if __name__ == "__main__":
    main()
