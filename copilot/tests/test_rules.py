"""
Tests for rules module.
"""

import unittest
import pandas as pd
from copilot.rules.trading_rules import (
    PriceThresholdRule,
    MovingAverageCrossRule,
    RSIRule,
)
from copilot.rules.rule_engine import RuleEngine


class TestTradingRules(unittest.TestCase):
    """Test trading rules."""

    def setUp(self):
        """Set up test data."""
        self.df = pd.DataFrame({
            'close_price': [100, 105, 103, 108, 110],
            'sma_5': [100, 102, 103, 105, 107],
            'sma_20': [98, 99, 101, 104, 106],
            'rsi': [25, 45, 65, 75, 80],
        })

    def test_price_threshold_rule(self):
        """Test price threshold rule."""
        rule = PriceThresholdRule({'threshold': 105, 'operator': 'greater'})
        
        self.assertFalse(rule.evaluate(self.df, 0))
        self.assertFalse(rule.evaluate(self.df, 1))
        self.assertTrue(rule.evaluate(self.df, 3))

    def test_rsi_rule(self):
        """Test RSI rule."""
        rule = RSIRule({'oversold_threshold': 30, 'condition': 'oversold'})
        
        self.assertTrue(rule.evaluate(self.df, 0))
        self.assertFalse(rule.evaluate(self.df, 2))


class TestRuleEngine(unittest.TestCase):
    """Test rule engine."""

    def setUp(self):
        """Set up test data."""
        self.df = pd.DataFrame({
            'close_price': [100, 105, 110, 108, 112],
        })

    def test_rule_engine_and_logic(self):
        """Test AND logic."""
        engine = RuleEngine({'logic': 'AND'})
        
        rule1 = PriceThresholdRule({'threshold': 100, 'operator': 'greater'})
        rule2 = PriceThresholdRule({'threshold': 120, 'operator': 'less'})
        
        engine.add_rule(rule1)
        engine.add_rule(rule2)
        
        # Both rules should be satisfied
        self.assertTrue(engine.evaluate(self.df, 2))

    def test_rule_engine_or_logic(self):
        """Test OR logic."""
        engine = RuleEngine({'logic': 'OR'})
        
        rule1 = PriceThresholdRule({'threshold': 150, 'operator': 'greater'})
        rule2 = PriceThresholdRule({'threshold': 100, 'operator': 'greater'})
        
        engine.add_rule(rule1)
        engine.add_rule(rule2)
        
        # At least one rule should be satisfied
        self.assertTrue(engine.evaluate(self.df, 2))


if __name__ == '__main__':
    unittest.main()
