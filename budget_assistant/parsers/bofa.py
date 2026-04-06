# PDF Parser for Bank of America statements. Inherits from base Parser and implements parse method to extract transactions from PDF statements.

from ast import pattern
from datetime import date, datetime
from decimal import Decimal
import logging
from pydoc import text
import re
from typing import List

from budget_assistant.models import Transaction
from budget_assistant.parsers.base import Parser
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BofaParser(Parser):
    
    def __init__(self, file_path: str, account_id: str):
        super().__init__(file_path, account_id)
        self.in_checks_section = False
        self.transaction_pattern = '(\\d{2}/\\d{2}/\\d{2})\\s+(.+?)(-?(?:\\d{1,3}(?:,\\d{3})+|\\d+)\\.\\d{2})'
        self.missing_transactions = False
        self.text = ""
        
    def parse(self) -> List[Transaction]:
        
        logger.info(f"Parsing Bank of America statement from file {self.file_path} for account {self.account_id}")
        self.cursor = 0

        reader = PdfReader(self.file_path)
        self.text = ''.join([page.extract_text().replace('\n', ' ') for page in reader.pages])

        deposits = self.get_deposits()
        withdrawals = self.get_withdrawals()
        checks = self.get_checks()

        # run this global search for transactions as a backup if we fail to identify the sections
        if self.missing_transactions:
            transactions = self.get_transactions_backup()
            logger.info(f"Finished parsing Bank of America statement. Found {len(transactions)} transactions using backup method.")
        else:
            transactions = deposits + withdrawals + checks
            logger.info(f"Finished parsing Bank of America statement. Found {len(deposits)} deposits, {len(withdrawals)} withdrawals, and {len(checks)} checks.")
        
        return transactions

    def get_transactions_backup(self) -> List[Transaction]:
        transactions = []
        transaction_tuples = re.findall(self.transaction_pattern, self.text)
        for transaction_date, description, transaction_amount in transaction_tuples:
            transaction_amount_decimal = Decimal(transaction_amount.replace(',', ''))
            transaction = Transaction(
                date=transaction_date,
                description=description,
                merchant="unknown",
                amount=transaction_amount_decimal,
                account=self.account_id,
                source_file=self.file_path
            )
            transactions.append(transaction)
        return transactions

    def get_deposits(self) -> List[Transaction]:
        deposits = []
        total_deposits_pattern = r'Total deposits and other additions\s+\$((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})'
        total_deposits_match = re.search(total_deposits_pattern, self.text)
        total_deposits = Decimal(total_deposits_match.group(1).replace(',', ''))
        
        if total_deposits_match:
            deposits_start, deposits_end = total_deposits_match.span()  # position of full match
            deposits_text = self.text[self.cursor:deposits_start]
            deposit_tuples = re.findall(self.transaction_pattern, deposits_text)
            
            total_deposits_found = 0
            for transaction_date, description, transaction_amount in deposit_tuples:
                deposit_amount = Decimal(transaction_amount.replace(',', ''))
                transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    merchant="unknown",
                    amount=deposit_amount,
                    account=self.account_id,
                    source_file=self.file_path
                )
                deposits.append(transaction)

                total_deposits_found += deposit_amount
            self.cursor = deposits_end
            if total_deposits_found != total_deposits:
                self.missing_transactions = True
                logger.warning(f"Total deposits found in transactions (${total_deposits_found}) does not match total deposits reported on statement (${total_deposits}). This may indicate that some transactions were not parsed correctly.")
        else:
            logger.warning(f"Did not find any deposits in statement {self.file_path} for account {self.account_id}.")

        return deposits

    def get_withdrawals(self) -> List[Transaction]:
        withdrawals = []
        total_withdrawals_pattern = r'Total withdrawals and other subtractions\s+-\$\s*((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})'
        total_withdrawals_match = re.search(total_withdrawals_pattern, self.text)
        total_withdrawals = -Decimal(total_withdrawals_match.group(1).replace(',', ''))
        
        if total_withdrawals_match:
            withdrawals_start, withdrawals_end = total_withdrawals_match.span()  # position of full match
            withdrawals_text = self.text[self.cursor:withdrawals_start]
            withdrawal_tuples = re.findall(self.transaction_pattern, withdrawals_text)
            
            total_withdrawals_found = 0
            for transaction_date, description, transaction_amount in withdrawal_tuples:
                withdrawal_amount = Decimal(transaction_amount.replace(',', ''))
                
                transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    merchant="unknown",
                    amount=withdrawal_amount,
                    account=self.account_id,
                    source_file=self.file_path
                )
                withdrawals.append(transaction)

                total_withdrawals_found += withdrawal_amount
            if total_withdrawals_found != (total_withdrawals + 1):
                self.missing_transactions = True
                logger.warning(f"Total withdrawals found in transactions (${total_withdrawals_found}) does not match total withdrawals reported on statement (${total_withdrawals}). This may indicate that some transactions were not parsed correctly.")
            self.cursor = withdrawals_end
        else:
            logger.warning(f"Did not find any withdrawals in statement {self.file_path} for account {self.account_id}.")

        return withdrawals

    def get_checks(self) -> List[Transaction]:
        checks = []
        total_checks_pattern = r'Total checks\s+-\$\s*((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})'
        total_checks_match = re.search(total_checks_pattern, self.text)
        total_checks = -Decimal(total_checks_match.group(1).replace(',', ''))

        if total_checks_match:
            checks_start, checks_end = total_checks_match.span()  # position of full match
            checks_text = self.text[self.cursor:checks_start]
            check_tuples = re.findall(self.transaction_pattern, checks_text)
            
            total_checks_found = 0
            for transaction_date, description, transaction_amount in check_tuples:
                check_amount = Decimal(transaction_amount.replace(',', ''))
                transaction = Transaction(
                    date=transaction_date,
                    description=description,
                    merchant="unknown",
                    amount=check_amount,
                    account=self.account_id,
                    source_file=self.file_path
                )
                checks.append(transaction)

                total_checks_found += check_amount
            if total_checks_found != total_checks:
                self.missing_transactions = True
                logger.warning(f"Total checks found in transactions (${total_checks_found}) does not match total checks reported on statement (${total_checks}). This may indicate that some transactions were not parsed correctly.")
        else:
            logger.warning(f"Did not find any checks in statement {self.file_path} for account {self.account_id}.")

        return checks
    
def main():
    parser = BofaParser("/Users/prestondonovan/Documents/budget_data/statements/eStmt_2026-03-23.pdf", "bofa-checking")
    #transactions = parser.parse("/Users/prestondonovan/Documents/budget_data/statements/eStmt_2026-02-19.pdf", "bofa-checking")
    transactions = parser.parse()
    for t in transactions:
        print(t.date, t.description[:10], t.amount)