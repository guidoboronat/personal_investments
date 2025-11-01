"""
Backtest module for testing trading strategies on historical data.
"""

from copilot.backtest.backtester import Backtester
from copilot.backtest.metrics import PerformanceMetrics

__all__ = [
    "Backtester",
    "PerformanceMetrics",
]
