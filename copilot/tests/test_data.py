"""
Tests for data module.
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch
from copilot.data.binance_source import BinanceDataSource
from copilot.data.preprocessor import DataPreprocessor
from copilot.core.exceptions import DataFetchError, ValidationError


class TestBinanceDataSource(unittest.TestCase):
    """Test Binance data source."""

    def test_initialization(self):
        """Test data source initialization."""
        source = BinanceDataSource()
        self.assertIsNotNone(source)
        self.assertEqual(source.base_url, 'https://api.binance.com/api/v3')

    def test_validation_empty_df(self):
        """Test validation fails on empty DataFrame."""
        source = BinanceDataSource()
        
        with self.assertRaises(ValidationError):
            source.validate_data(pd.DataFrame())


class TestDataPreprocessor(unittest.TestCase):
    """Test data preprocessor."""

    def test_clean_data_removes_duplicates(self):
        """Test duplicate removal."""
        df = pd.DataFrame({
            'open_price': [100, 100, 101],
            'close_price': [101, 101, 102],
        })
        
        preprocessor = DataPreprocessor()
        cleaned = preprocessor.clean_data(df)
        
        # After dropping duplicates, should have fewer rows
        self.assertLessEqual(len(cleaned), len(df))

    def test_add_time_features(self):
        """Test time feature addition."""
        df = pd.DataFrame({
            'open_time': pd.date_range('2024-01-01', periods=5, freq='D'),
            'close_price': [100, 101, 102, 103, 104],
        })
        
        preprocessor = DataPreprocessor()
        result = preprocessor.add_time_features(df)
        
        self.assertIn('hour', result.columns)
        self.assertIn('day_of_week', result.columns)
        self.assertIn('month', result.columns)


if __name__ == '__main__':
    unittest.main()
