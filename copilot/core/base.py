"""
Base classes for the trading toolkit.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import pandas as pd


class BaseDataSource(ABC):
    """Abstract base class for data sources."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def fetch_data(self, symbol: str, start_time: str, end_time: str, **kwargs) -> pd.DataFrame:
        """
        Fetch historical data for a given symbol and time range.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            start_time: Start time in 'YYYY-MM-DD' format
            end_time: End time in 'YYYY-MM-DD' format
            **kwargs: Additional parameters

        Returns:
            DataFrame with OHLCV data
        """
        pass

    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate fetched data.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        pass


class BaseIndicator(ABC):
    """Abstract base class for technical indicators."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicator values.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with indicator values added
        """
        pass

    def validate_inputs(self, df: pd.DataFrame) -> bool:
        """
        Validate input data.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid
        """
        required_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
        return all(col in df.columns for col in required_columns)


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.position = 0  # Current position: 0 (no position), 1 (long), -1 (short)
        self.trade_history: List[Dict[str, Any]] = []

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.

        Args:
            df: DataFrame with price and indicator data

        Returns:
            DataFrame with signal column added
        """
        pass

    @abstractmethod
    def should_buy(self, row: pd.Series) -> bool:
        """
        Determine if a buy signal should be generated.

        Args:
            row: DataFrame row with current market data

        Returns:
            True if should buy
        """
        pass

    @abstractmethod
    def should_sell(self, row: pd.Series) -> bool:
        """
        Determine if a sell signal should be generated.

        Args:
            row: DataFrame row with current market data

        Returns:
            True if should sell
        """
        pass

    def reset(self):
        """Reset strategy state."""
        self.position = 0
        self.trade_history = []

    def record_trade(self, trade_type: str, price: float, timestamp: Any, quantity: float = 1.0):
        """
        Record a trade in history.

        Args:
            trade_type: 'buy' or 'sell'
            price: Trade price
            timestamp: Trade timestamp
            quantity: Trade quantity
        """
        self.trade_history.append({
            'type': trade_type,
            'price': price,
            'timestamp': timestamp,
            'quantity': quantity,
        })


class BaseRule(ABC):
    """Abstract base class for trading rules."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate rule condition.

        Args:
            df: DataFrame with market data
            row_idx: Current row index

        Returns:
            True if rule condition is met
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of the rule.

        Returns:
            Rule description
        """
        pass
