# PDF Parser for Bank of America statements. Inherits from base Parser and implements parse method to extract transactions from PDF statements.

from datetime import date, datetime
from decimal import Decimal
import re
from typing import List

from budget_assistant.models import Transaction
from budget_assistant.parsers.base import Parser
from PyPDF2 import PdfReader

class BofaParser(Parser):
    def parse(self, file_path: str, account_id: str) -> List[Transaction]:
        reader = PdfReader(file_path)
        transactions = []
        for page in reader.pages:
            text = page.extract_text()
            transactions.extend(self._parse_transactions_from_text(text, account_id, file_path))
        return transactions

    def _parse_transactions_from_text(self, text: str, account_id: str, source_file: str) -> List[Transaction]:
        transactions = []
        lines = text.splitlines()
        date_pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(\d{2}).*$"  # MM/DD/YY format
        transaction_amt_pattern = r"(\d{1,3}(?:,\d{3})*\.\d{2})$"
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.match(date_pattern, line)  # MM/DD/YY format

            # new transaction found
            if match:
                transaction_str = line
                # Get date of transaction in YYYY-MM-DD format
                MM, DD, YY = match.groups()
                transaction_date = date(2000 + int(YY), int(MM), int(DD)).isoformat()

                # Check if the current line also contains a transaction amount
                amount_match = re.search(transaction_amt_pattern, lines[i])
                j = i + 1
                # If a transaction amount was not found, keep reading until we find one.
                while not amount_match and j < len(lines):
                    transaction_str += " " + lines[j]  # Append next line to transaction string
                    amount_match = re.search(transaction_amt_pattern, lines[j])
                    j += 1
                    i += 1  # Increment i to skip over lines we've already processed as part of this transaction
                
                # Extract dollar value of transaction, which is the last part of the transaction string
                # but may not be separated by any text. For example, the text may lok like "starbucks3.45" with no space between merchant and amount.
                if not amount_match:
                    raise Warning(f"Reached EOF and could not extract amount from transaction string: {transaction_str}")
                transaction_amount = Decimal(amount_match.group(1).replace(',', ''))  # Remove commas from amount

                merchant = "unknown"

                transaction = Transaction(
                    date=transaction_date,
                    description=transaction_str,
                    merchant=merchant,
                    amount=transaction_amount,
                    account=account_id,
                    source_file=source_file
                )
                transactions.append(transaction)
            i += 1
        return transactions
    
def main():
    parser = BofaParser()
    transactions = parser.parse("/Users/prestondonovan/Documents/budget_data/statements/eStmt_2026-02-19.pdf", "bofa-checking")
    for t in transactions:
        print(t)