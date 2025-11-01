"""
Tests for core module.
"""

import unittest
import pandas as pd
from copilot.core.base import BaseStrategy, BaseIndicator, BaseDataSource
from copilot.core.utils import (
    timestamp_to_datetime,
    datetime_to_timestamp,
    calculate_returns,
    calculate_sharpe_ratio,
)
from copilot.core.exceptions import ValidationError


class TestBaseClasses(unittest.TestCase):
    """Test base classes."""

    def test_base_indicator_validation(self):
        """Test indicator input validation."""
        
        class TestIndicator(BaseIndicator):
            def calculate(self, df):
                return df
        
        indicator = TestIndicator()
        
        # Create valid DataFrame
        df = pd.DataFrame({
            'open_price': [100, 101],
            'high_price': [102, 103],
            'low_price': [99, 100],
            'close_price': [101, 102],
            'volume': [1000, 1100],
        })
        
        self.assertTrue(indicator.validate_inputs(df))

    def test_base_strategy_reset(self):
        """Test strategy reset."""
        
        class TestStrategy(BaseStrategy):
            def generate_signals(self, df):
                return df
            
            def should_buy(self, row):
                return False
            
            def should_sell(self, row):
                return False
        
        strategy = TestStrategy()
        strategy.position = 1
        strategy.trade_history = [{'test': 'data'}]
        
        strategy.reset()
        
        self.assertEqual(strategy.position, 0)
        self.assertEqual(len(strategy.trade_history), 0)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_calculate_returns(self):
        """Test returns calculation."""
        prices = pd.Series([100, 105, 103, 108])
        returns = calculate_returns(prices)
        
        self.assertEqual(len(returns), 4)
        self.assertTrue(pd.isna(returns.iloc[0]))
        self.assertAlmostEqual(returns.iloc[1], 0.05, places=2)

    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.005])
        sharpe = calculate_sharpe_ratio(returns)
        
        self.assertIsInstance(sharpe, float)
        self.assertGreater(sharpe, 0)


if __name__ == '__main__':
    unittest.main()
