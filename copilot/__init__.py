"""
On-Chain Trading Analysis Toolkit

A modular framework for analyzing on-chain trading data, building trading strategies,
and backtesting them with comprehensive alerting and monitoring capabilities.
"""

__version__ = "0.1.0"
__author__ = "Personal Investments Team"

from copilot.core.base import BaseStrategy, BaseIndicator
from copilot.core.exceptions import (
    TradingToolkitError,
    DataFetchError,
    ValidationError,
    BacktestError,
)

__all__ = [
    "BaseStrategy",
    "BaseIndicator",
    "TradingToolkitError",
    "DataFetchError",
    "ValidationError",
    "BacktestError",
]
