from decimal import Decimal
import logging
import re
from typing import List

import pdfplumber

from budget_assistant.models import Transaction
from budget_assistant.parsers.base import Parser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PayPalParser(Parser):
    def __init__(self, file_path: str, account_id: str):
        super().__init__(file_path, account_id)
        self.text = ""
        self.statement_year = None

    def parse(self) -> List[Transaction]:
        logger.info(f"Parsing PayPal statement from file {self.file_path} for account {self.account_id}")

        with pdfplumber.open(self.file_path) as pdf:
            page_text = [page.extract_text() or "" for page in pdf.pages]
            self.text = "\n".join(page_text)

        self._extract_statement_year()

        transactions: List[Transaction] = []
        transactions.extend(self.get_payments())
        transactions.extend(self.get_credits())
        transactions.extend(self.get_purchases())

        logger.info(
            f"Finished parsing PayPal statement. Found {len(transactions)} transactions: {len(self.get_payments())} payments, {len(self.get_credits())} credits, {len(self.get_purchases())} purchases."
        )

        return transactions

    def _extract_statement_year(self):
        # Prefer the explicit year found in the statement summary
        patterns = [
            r'New balance as of \d{2}/\d{2}/(\d{4})',
            r'Payment due date \d{2}/\d{2}/(\d{4})',
            r'\d{2}/\d{2}/\d{4} to \d{2}/\d{2}/(\d{4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.text)
            if match:
                self.statement_year = match.group(1)
                break

        if not self.statement_year:
            logger.warning(f"Could not extract statement year from {self.file_path}, defaulting to 2026")
            self.statement_year = "2026"

        logger.info(f"Extracted statement year: {self.statement_year}")

    def get_payments(self) -> List[Transaction]:
        section = self._extract_section(r'Payments\s+-\$[\d,]+\.\d{2}', [r'Other Credits', r'Purchases and Other Debits', r'Total Fees Charged', r'Total Interest Charged'])
        return self._parse_section(section, prefix='Payment:')

    def get_credits(self) -> List[Transaction]:
        section = self._extract_section(r'Other Credits\s+-\$[\d,]+\.\d{2}', [r'Purchases and Other Debits', r'Total Fees Charged', r'Total Interest Charged'])
        return self._parse_section(section, prefix='Refund:')

    def get_purchases(self) -> List[Transaction]:
        section = self._extract_section(r'Purchases and Other Debits\s+\$[\d,]+\.\d{2}', [r'Total Fees Charged', r'Total Interest Charged', r'\d{4} Year to date fees and interest'])
        return self._parse_section(section, prefix='Purchase:')

    def _extract_section(self, heading_pattern: str, terminators: List[str]) -> str:
        regex = rf'{heading_pattern}\n(.*?)(?:{'|'.join(terminators)}|$)'
        match = re.search(regex, self.text, re.DOTALL)
        return match.group(1) if match else ""

    def _parse_section(self, section_text: str, prefix: str) -> List[Transaction]:
        if not section_text:
            return []

        transactions: List[Transaction] = []
        transaction_pattern = re.compile(
            r'^(\d{2}/\d{2})\s+(.+?)\s+(-?\$?\d{1,3}(?:,\d{3})*\.\d{2}|\$-?\d{1,3}(?:,\d{3})*\.\d{2})$'
        )

        current = None
        for raw_line in section_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith('Date Reference #') or line.startswith('Transaction details'):
                continue

            match = transaction_pattern.match(line)
            if match:
                if current:
                    transactions.append(current)
                date_str, description, amount_str = match.groups()
                amount = Decimal(amount_str.replace('$', '').replace(',', ''))
                transaction = Transaction(
                    date=f"{date_str}/{self.statement_year[-2:]}",
                    description=f"{prefix} {description}",
                    merchant="unknown",
                    amount=amount,
                    account=self.account_id,
                    source_file=self.file_path,
                )
                current = transaction
            elif current:
                current.description += f" {line}"

        if current:
            transactions.append(current)

        return transactions


def main():
    parser = PayPalParser("tests/test_data/statements/statement-2026-03-15.pdf", "paypal-7513")
    transactions = parser.parse()
    for t in transactions:
        print(f"{t.date} {t.description[:60]:60} {t.amount}")


if __name__ == "__main__":
    main()
