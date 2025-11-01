"""
Tests for backtest module.
"""

import unittest
import pandas as pd
from copilot.backtest.backtester import Backtester
from copilot.backtest.metrics import PerformanceMetrics
from copilot.core.base import BaseStrategy


class TestBacktester(unittest.TestCase):
    """Test backtester."""

    def setUp(self):
        """Set up test data and strategy."""
        self.df = pd.DataFrame({
            'open_time': pd.date_range('2024-01-01', periods=100, freq='H'),
            'open_price': [100 + i * 0.1 for i in range(100)],
            'high_price': [101 + i * 0.1 for i in range(100)],
            'low_price': [99 + i * 0.1 for i in range(100)],
            'close_price': [100.5 + i * 0.1 for i in range(100)],
            'volume': [1000] * 100,
        })

        class SimpleStrategy(BaseStrategy):
            def generate_signals(self, df):
                df = df.copy()
                df['signal'] = 0
                # Buy on even indices, sell on odd
                df.loc[df.index % 10 == 0, 'signal'] = 1
                df.loc[df.index % 10 == 5, 'signal'] = -1
                return df

            def should_buy(self, row):
                return row.name % 10 == 0

            def should_sell(self, row):
                return row.name % 10 == 5

        self.strategy = SimpleStrategy()

    def test_backtester_initialization(self):
        """Test backtester initialization."""
        backtester = Backtester({'initial_balance': 10000})
        self.assertEqual(backtester.initial_balance, 10000)

    def test_backtester_run(self):
        """Test backtester execution."""
        backtester = Backtester({'initial_balance': 10000})
        results = backtester.run(df=self.df, strategy=self.strategy)
        
        self.assertIn('initial_balance', results)
        self.assertIn('final_balance', results)
        self.assertIn('trades', results)
        self.assertIn('metrics', results)


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics."""

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        equity_curve = pd.Series([10000, 10100, 10050, 10200, 10300])
        trades = [
            {'type': 'buy', 'balance': 10000},
            {'type': 'sell', 'balance': 10300},
        ]
        
        metrics = PerformanceMetrics.calculate_metrics(
            equity_curve=equity_curve,
            trades=trades,
            initial_balance=10000
        )
        
        self.assertIn('total_return', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)


if __name__ == '__main__':
    unittest.main()
