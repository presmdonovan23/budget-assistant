#!/usr/bin/env python3
"""
Test script for Chase parser - run from project root directory
"""

from budget_assistant.parsers.chase import ChaseParser
from decimal import Decimal

def test_chase_parser():
    print("=" * 80)
    print("TESTING CHASE PARSER")
    print("=" * 80)

    # Test with first statement
    print("\n[1] Testing First Statement (20260327-statements-7256-.pdf)")
    print("-" * 80)
    file1 = "tests/test_data/statements/20260327-statements-7256-.pdf"
    parser1 = ChaseParser(file1, "chase-7256")
    transactions1 = parser1.parse()

    purchases = [t for t in transactions1 if "Purchase:" in t.description]
    purchases_total = sum(t.amount for t in purchases)

    print(f"Transactions found: {len(transactions1)}")
    print(f"Total purchases: ${purchases_total}")
    print(f"Expected: $182.80")
    print(f"✓ PASS" if purchases_total == Decimal('182.80') else "✗ FAIL")

    # Test with second statement
    print("\n[2] Testing Second Statement (20260419-statements-5450-.pdf)")
    print("-" * 80)
    file2 = "tests/test_data/statements/20260419-statements-5450-.pdf"
    parser2 = ChaseParser(file2, "chase-5450")
    transactions2 = parser2.parse()

    purchases = [t for t in transactions2 if "Purchase:" in t.description]
    payments = [t for t in transactions2 if "Payment:" in t.description]
    refunds = [t for t in transactions2 if "Refund:" in t.description]

    purchases_total = sum(t.amount for t in purchases)
    credits_total = abs(sum(t.amount for t in payments) + sum(t.amount for t in refunds))

    print(f"Transactions found: {len(transactions2)}")
    print(f"  - Purchases: {len(purchases)}")
    print(f"  - Payments: {len(payments)}")
    print(f"  - Refunds: {len(refunds)}")
    print(f"\nTotal purchases: ${purchases_total}")
    print(f"Expected: $615.80")
    print(f"✓ PASS" if purchases_total == Decimal('615.80') else "✗ FAIL")
    print(f"\nTotal credits: ${credits_total}")
    print(f"Expected: $1082.42")
    print(f"✓ PASS" if credits_total == Decimal('1082.42') else "✗ FAIL")

    # Print all transactions for manual review
    print("\nAll transactions from first statement:")
    for t in transactions1:
        print(f"{t.date} {t.description} {t.amount:>8}")

    print("\nAll transactions from second statement:")
    for t in transactions2:
        print(f"{t.date} {t.description} {t.amount:>8}")

    print("\n" + "=" * 80)
    success = (
        purchases_total == Decimal('615.80') and
        credits_total == Decimal('1082.42') and
        sum(t.amount for t in [t for t in transactions1 if "Purchase:" in t.description]) == Decimal('182.80')
    )
    print("ALL TESTS PASSED!" if success else "SOME TESTS FAILED")
    print("=" * 80)

if __name__ == "__main__":
    test_chase_parser()