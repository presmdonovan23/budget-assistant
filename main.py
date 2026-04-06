# main.py
from budget_assistant.models import Transaction
from budget_assistant.store import save_month

if __name__ == "__main__":
    # transactions = [
    #     Transaction(
    #         date="2026-03-15",
    #         description="WHOLE FOODS 1234",
    #         merchant="whole foods",
    #         amount="123.45",
    #         account="bofa-checking",
    #         source_file="statement.pdf",
    #         category="groceries"
    #     )
    # ]
    # save_month("2026-03", transactions)

    # # call bofa.main() to test the parser
    # import budget_assistant.parsers.bofa as bofa
    # bofa.main()

    import budget_assistant.parsers.amex as amex
    amex.main()