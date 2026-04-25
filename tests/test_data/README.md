# Test Data Directory

This directory contains sample statement files used for unit testing the budget assistant parsers.

**Note: This directory and its contents are gitignored to prevent sensitive financial documents from being committed to the repository.**

## Contents

### statements/
- `20260327-statements-7256-.pdf` - Chase credit card statement with 3 purchases totaling $182.80
- `20260419-statements-5450-.pdf` - Chase credit card statement with 19 purchases ($615.80) and 2 credits ($1,082.42)

## Usage

These files are used by the unit tests in `tests/test_chase.py` to validate the Chase parser functionality with real PDF data instead of mocked content.

## Adding New Test Statements

When adding test statements for other parsers:
1. Place PDF files in appropriate subdirectories under `test_data/`
2. Update corresponding unit tests to use the actual files
3. Ensure tests validate expected transaction counts and totals
4. Keep file names descriptive of their contents
5. **Remember: These files will not be committed to git due to .gitignore rules**