"""Unit tests for configuration file loading and structure."""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def categories_config():
    with open("config/categories.yaml", "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def rules_config():
    with open("config/rules.yaml", "r") as f:
        return yaml.safe_load(f)


class TestCategoriesConfig:
    """Tests for categories.yaml structure and content."""

    def test_categories_file_exists(self):
        """Verify categories.yaml exists."""
        assert Path("config/categories.yaml").exists()

    def test_categories_is_list(self, categories_config):
        """Verify categories config is a list of category rules."""
        assert isinstance(categories_config, list)
        assert len(categories_config) > 0

    def test_each_category_has_required_fields(self, categories_config):
        """Verify each category rule has category name and keywords."""
        for rule in categories_config:
            assert "category" in rule, "Each rule must have a 'category' field"
            assert "keywords" in rule, "Each rule must have a 'keywords' field"
            assert isinstance(rule["category"], str)
            assert isinstance(rule["keywords"], list)

    def test_keywords_are_strings(self, categories_config):
        """Verify all keywords are non-empty strings."""
        for rule in categories_config:
            for keyword in rule["keywords"]:
                assert isinstance(keyword, str), f"Keyword must be string, got {type(keyword)}"
                assert keyword.strip(), "Keywords must be non-empty"

    def test_sample_merchants_are_present(self, categories_config):
        """Verify expected merchants from spec are in categories."""
        all_keywords = []
        for rule in categories_config:
            all_keywords.extend(rule["keywords"])

        expected_merchants = [
            "sweetgreen",
            "spotify",
            "amazon prime",
            "peacock",
            "amazon",
            "shaws",
            "mbta",
            "xfinity",
            "eversource",
            "blizzard",
        ]

        for merchant in expected_merchants:
            assert merchant in all_keywords, f"Expected merchant '{merchant}' not in categories"

    def test_no_duplicate_keywords_across_categories(self, categories_config):
        """Verify keywords don't appear in multiple categories."""
        seen = {}
        for rule in categories_config:
            for keyword in rule["keywords"]:
                if keyword in seen:
                    pytest.fail(
                        f"Keyword '{keyword}' appears in both '{seen[keyword]}' and '{rule['category']}'"
                    )
                seen[keyword] = rule["category"]


class TestRulesConfig:
    """Tests for rules.yaml structure and content."""

    def test_rules_file_exists(self):
        """Verify rules.yaml exists."""
        assert Path("config/rules.yaml").exists()

    def test_rules_is_dict(self, rules_config):
        """Verify rules config is a dict."""
        assert isinstance(rules_config, dict)

    def test_high_dollar_threshold_exists_and_valid(self, rules_config):
        """Verify high_dollar_threshold is present and numeric."""
        assert "high_dollar_threshold" in rules_config
        assert isinstance(rules_config["high_dollar_threshold"], (int, float))
        assert rules_config["high_dollar_threshold"] > 0

    def test_category_thresholds_structure(self, rules_config):
        """Verify category_thresholds is dict of numeric values."""
        assert "category_thresholds" in rules_config
        thresholds = rules_config["category_thresholds"]
        assert isinstance(thresholds, dict)
        for category, threshold in thresholds.items():
            assert isinstance(category, str)
            assert isinstance(threshold, (int, float))
            assert threshold > 0

    def test_subscription_rule_structure(self, rules_config):
        """Verify subscription rule has required keys."""
        assert "subscription" in rules_config
        sub = rules_config["subscription"]
        assert "tracked_merchants" in sub
        assert "tolerance_amount" in sub
        assert "min_history_months" in sub
        assert isinstance(sub["tracked_merchants"], list)
        assert isinstance(sub["tolerance_amount"], (int, float))
        assert isinstance(sub["min_history_months"], int)

    def test_subscription_tracked_merchants_include_sample(self, rules_config):
        """Verify expected subscriptions are tracked."""
        tracked = rules_config["subscription"]["tracked_merchants"]
        expected_subscriptions = ["spotify", "amazon prime", "peacock", "blizzard"]
        for sub in expected_subscriptions:
            assert sub in tracked, f"Expected subscription '{sub}' not in tracked_merchants"

    def test_new_merchant_rule_structure(self, rules_config):
        """Verify new_merchant rule has required keys."""
        assert "new_merchant" in rules_config
        nm = rules_config["new_merchant"]
        assert "enabled" in nm
        assert "ignore_merchants" in nm
        assert isinstance(nm["enabled"], bool)
        assert isinstance(nm["ignore_merchants"], list)

    def test_reporting_structure(self, rules_config):
        """Verify reporting section has tracked_expenses."""
        assert "reporting" in rules_config
        report = rules_config["reporting"]
        assert "tracked_expenses" in report
        assert isinstance(report["tracked_expenses"], list)
        assert len(report["tracked_expenses"]) > 0

    def test_reporting_tracked_expenses_are_strings(self, rules_config):
        """Verify all tracked expenses are non-empty strings."""
        tracked = rules_config["reporting"]["tracked_expenses"]
        for expense in tracked:
            assert isinstance(expense, str)
            assert expense.strip()
