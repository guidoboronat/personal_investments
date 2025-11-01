"""
Core module containing base classes and utilities for the trading toolkit.
"""

from copilot.core.base import BaseStrategy, BaseIndicator, BaseDataSource
from copilot.core.exceptions import (
    TradingToolkitError,
    DataFetchError,
    ValidationError,
    BacktestError,
    AlertError,
)
from copilot.core.utils import (
    timestamp_to_datetime,
    datetime_to_timestamp,
    validate_dataframe,
    calculate_returns,
)

__all__ = [
    "BaseStrategy",
    "BaseIndicator",
    "BaseDataSource",
    "TradingToolkitError",
    "DataFetchError",
    "ValidationError",
    "BacktestError",
    "AlertError",
    "timestamp_to_datetime",
    "datetime_to_timestamp",
    "validate_dataframe",
    "calculate_returns",
]
