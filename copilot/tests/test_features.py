"""
Tests for features module.
"""

import unittest
import pandas as pd
from copilot.features.technical_indicators import (
    MovingAverageIndicator,
    RSIIndicator,
    BollingerBandsIndicator,
)
from copilot.features.feature_engineering import FeatureEngineer


class TestTechnicalIndicators(unittest.TestCase):
    """Test technical indicators."""

    def setUp(self):
        """Set up test data."""
        self.df = pd.DataFrame({
            'open_price': [100, 101, 102, 103, 104] * 10,
            'high_price': [102, 103, 104, 105, 106] * 10,
            'low_price': [99, 100, 101, 102, 103] * 10,
            'close_price': [101, 102, 103, 104, 105] * 10,
            'volume': [1000, 1100, 1200, 1300, 1400] * 10,
        })

    def test_moving_average_indicator(self):
        """Test moving average calculation."""
        indicator = MovingAverageIndicator({'periods': [5, 10], 'type': 'sma'})
        result = indicator.calculate(self.df)
        
        self.assertIn('sma_5', result.columns)
        self.assertIn('sma_10', result.columns)

    def test_rsi_indicator(self):
        """Test RSI calculation."""
        indicator = RSIIndicator({'period': 14})
        result = indicator.calculate(self.df)
        
        self.assertIn('rsi', result.columns)

    def test_bollinger_bands_indicator(self):
        """Test Bollinger Bands calculation."""
        indicator = BollingerBandsIndicator({'period': 20, 'num_std': 2})
        result = indicator.calculate(self.df)
        
        self.assertIn('bb_upper', result.columns)
        self.assertIn('bb_lower', result.columns)
        self.assertIn('bb_middle', result.columns)


class TestFeatureEngineer(unittest.TestCase):
    """Test feature engineering."""

    def setUp(self):
        """Set up test data."""
        self.df = pd.DataFrame({
            'open_price': [100, 101, 102, 103, 104],
            'high_price': [102, 103, 104, 105, 106],
            'low_price': [99, 100, 101, 102, 103],
            'close_price': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400],
        })

    def test_add_price_features(self):
        """Test price feature addition."""
        engineer = FeatureEngineer()
        result = engineer.add_price_features(self.df)
        
        self.assertIn('price_change', result.columns)
        self.assertIn('price_change_pct', result.columns)

    def test_add_volume_features(self):
        """Test volume feature addition."""
        engineer = FeatureEngineer()
        result = engineer.add_volume_features(self.df)
        
        self.assertIn('volume_change', result.columns)
        self.assertIn('volume_ma_5', result.columns)


if __name__ == '__main__':
    unittest.main()
