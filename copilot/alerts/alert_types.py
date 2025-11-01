"""
Alert type implementations.
"""

import pandas as pd
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAlert(ABC):
    """Base class for alert types."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def check(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Check if alert condition is met.

        Args:
            df: DataFrame with market data
            row_idx: Current row index

        Returns:
            True if alert should be triggered
        """
        pass

    @abstractmethod
    def get_message(self, df: pd.DataFrame, row_idx: int) -> str:
        """
        Get alert message.

        Args:
            df: DataFrame with market data
            row_idx: Current row index

        Returns:
            Alert message
        """
        pass


class PriceAlert(BaseAlert):
    """Alert based on price thresholds."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.threshold = self.config.get('threshold', 0.0)
        self.condition = self.config.get('condition', 'above')  # 'above' or 'below'

    def check(self, df: pd.DataFrame, row_idx: int) -> bool:
        """Check if price alert condition is met."""
        if row_idx >= len(df):
            return False

        price = df.iloc[row_idx]['close_price']

        if self.condition == 'above':
            return price > self.threshold
        elif self.condition == 'below':
            return price < self.threshold

        return False

    def get_message(self, df: pd.DataFrame, row_idx: int) -> str:
        """Get price alert message."""
        price = df.iloc[row_idx]['close_price']
        return f"Price {self.condition} threshold: ${price:.2f} {self.condition} ${self.threshold:.2f}"


class VolumeAlert(BaseAlert):
    """Alert based on volume anomalies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.threshold_multiplier = self.config.get('threshold_multiplier', 2.0)
        self.baseline_period = self.config.get('baseline_period', 20)

    def check(self, df: pd.DataFrame, row_idx: int) -> bool:
        """Check if volume alert condition is met."""
        if row_idx < self.baseline_period or row_idx >= len(df):
            return False

        current_volume = df.iloc[row_idx]['volume']
        avg_volume = df.iloc[row_idx - self.baseline_period:row_idx]['volume'].mean()

        return current_volume > (avg_volume * self.threshold_multiplier)

    def get_message(self, df: pd.DataFrame, row_idx: int) -> str:
        """Get volume alert message."""
        current_volume = df.iloc[row_idx]['volume']
        avg_volume = df.iloc[row_idx - self.baseline_period:row_idx]['volume'].mean()
        multiplier = current_volume / avg_volume

        return f"High volume detected: {multiplier:.2f}x average ({current_volume:.2f})"


class IndicatorAlert(BaseAlert):
    """Alert based on indicator values."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.indicator_name = self.config.get('indicator_name', 'rsi')
        self.threshold = self.config.get('threshold', 70)
        self.condition = self.config.get('condition', 'above')

    def check(self, df: pd.DataFrame, row_idx: int) -> bool:
        """Check if indicator alert condition is met."""
        if row_idx >= len(df) or self.indicator_name not in df.columns:
            return False

        value = df.iloc[row_idx][self.indicator_name]

        if pd.isna(value):
            return False

        if self.condition == 'above':
            return value > self.threshold
        elif self.condition == 'below':
            return value < self.threshold

        return False

    def get_message(self, df: pd.DataFrame, row_idx: int) -> str:
        """Get indicator alert message."""
        value = df.iloc[row_idx][self.indicator_name]
        return f"{self.indicator_name.upper()} {self.condition} threshold: {value:.2f} {self.condition} {self.threshold:.2f}"


class StrategyAlert(BaseAlert):
    """Alert based on strategy signals."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.signal_type = self.config.get('signal_type', 'buy')  # 'buy' or 'sell'

    def check(self, df: pd.DataFrame, row_idx: int) -> bool:
        """Check if strategy signal alert condition is met."""
        if row_idx >= len(df) or 'signal' not in df.columns:
            return False

        signal = df.iloc[row_idx]['signal']

        if self.signal_type == 'buy':
            return signal == 1
        elif self.signal_type == 'sell':
            return signal == -1

        return False

    def get_message(self, df: pd.DataFrame, row_idx: int) -> str:
        """Get strategy alert message."""
        price = df.iloc[row_idx]['close_price']
        return f"{self.signal_type.upper()} signal generated at ${price:.2f}"


class DrawdownAlert(BaseAlert):
    """Alert based on drawdown threshold."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.threshold = self.config.get('threshold', 0.10)  # 10% drawdown

    def check(self, df: pd.DataFrame, row_idx: int) -> bool:
        """Check if drawdown alert condition is met."""
        if row_idx < 1 or row_idx >= len(df):
            return False

        equity = df.iloc[:row_idx + 1]['close_price']
        running_max = equity.expanding().max()
        drawdown = (equity.iloc[-1] - running_max.iloc[-1]) / running_max.iloc[-1]

        return abs(drawdown) > self.threshold

    def get_message(self, df: pd.DataFrame, row_idx: int) -> str:
        """Get drawdown alert message."""
        equity = df.iloc[:row_idx + 1]['close_price']
        running_max = equity.expanding().max()
        drawdown = (equity.iloc[-1] - running_max.iloc[-1]) / running_max.iloc[-1]

        return f"Drawdown alert: {abs(drawdown) * 100:.2f}% from peak"
