import csv
from decimal import Decimal
from typing import List, Tuple

from budget_assistant.parsers.base import Parser
from budget_assistant.models import Transaction


class AmexParser(Parser):
    
    def __init__(self, file_path: str, account_id: str):
        super().__init__(file_path, account_id)
    
    def parse(self) -> list[Transaction]:
        transactions = []

        with open(self.file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                transaction_date = row["Date"].strip()
                description = row["Description"].strip()

                # Clean and convert amount
                amount_str = row["Amount"].strip().replace(",", "")
                amount = Decimal(amount_str)

                extended_details = (row.get("Extended Details") or "").strip()
                category = (row.get("Category") or "").strip()

                transactions.append(
                    Transaction(
                        date=transaction_date,
                        description=description,
                        merchant="unknown",
                        amount=amount,
                        account=self.account_id,
                        source_file=self.file_path,
                    )
                )

        return transactions


def main():
    parser = AmexParser("/Users/prestondonovan/Documents/budget_data/statements/amex_march.csv", "amex_credit")
    #transactions = parser.parse("/Users/prestondonovan/Documents/budget_data/statements/eStmt_2026-02-19.pdf", "bofa-checking")
    transactions = parser.parse()
    for t in transactions:
        print(t.date, t.description[:10], t.amount)