"""
Trading rules implementation.
"""

import pandas as pd
from typing import Dict, Any, Optional
from copilot.core.base import BaseRule


class PriceThresholdRule(BaseRule):
    """Rule based on price threshold."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.threshold = self.config.get('threshold', 0.0)
        self.operator = self.config.get('operator', 'greater')  # 'greater', 'less', 'equal'

    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate if price meets threshold condition.

        Args:
            df: DataFrame with price data
            row_idx: Current row index

        Returns:
            True if condition is met
        """
        if row_idx >= len(df):
            return False

        price = df.iloc[row_idx]['close_price']

        if self.operator == 'greater':
            return price > self.threshold
        elif self.operator == 'less':
            return price < self.threshold
        elif self.operator == 'equal':
            return abs(price - self.threshold) < 0.01
        return False

    def get_description(self) -> str:
        """Get rule description."""
        return f"Price {self.operator} {self.threshold}"


class MovingAverageCrossRule(BaseRule):
    """Rule based on moving average crossover."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.fast_period = self.config.get('fast_period', 20)
        self.slow_period = self.config.get('slow_period', 50)
        self.cross_type = self.config.get('cross_type', 'bullish')  # 'bullish' or 'bearish'

    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate if MA crossover occurred.

        Args:
            df: DataFrame with MA data
            row_idx: Current row index

        Returns:
            True if crossover condition is met
        """
        if row_idx < 1 or row_idx >= len(df):
            return False

        fast_col = f'sma_{self.fast_period}'
        slow_col = f'sma_{self.slow_period}'

        if fast_col not in df.columns or slow_col not in df.columns:
            return False

        # Current values
        fast_current = df.iloc[row_idx][fast_col]
        slow_current = df.iloc[row_idx][slow_col]

        # Previous values
        fast_prev = df.iloc[row_idx - 1][fast_col]
        slow_prev = df.iloc[row_idx - 1][slow_col]

        if self.cross_type == 'bullish':
            # Fast crosses above slow
            return fast_prev <= slow_prev and fast_current > slow_current
        elif self.cross_type == 'bearish':
            # Fast crosses below slow
            return fast_prev >= slow_prev and fast_current < slow_current

        return False

    def get_description(self) -> str:
        """Get rule description."""
        return f"{self.cross_type.capitalize()} MA cross: {self.fast_period}/{self.slow_period}"


class RSIRule(BaseRule):
    """Rule based on RSI levels."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.oversold_threshold = self.config.get('oversold_threshold', 30)
        self.overbought_threshold = self.config.get('overbought_threshold', 70)
        self.condition = self.config.get('condition', 'oversold')  # 'oversold' or 'overbought'

    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate RSI condition.

        Args:
            df: DataFrame with RSI data
            row_idx: Current row index

        Returns:
            True if RSI condition is met
        """
        if row_idx >= len(df) or 'rsi' not in df.columns:
            return False

        rsi = df.iloc[row_idx]['rsi']

        if pd.isna(rsi):
            return False

        if self.condition == 'oversold':
            return rsi < self.oversold_threshold
        elif self.condition == 'overbought':
            return rsi > self.overbought_threshold

        return False

    def get_description(self) -> str:
        """Get rule description."""
        if self.condition == 'oversold':
            return f"RSI < {self.oversold_threshold} (oversold)"
        else:
            return f"RSI > {self.overbought_threshold} (overbought)"


class VolumeRule(BaseRule):
    """Rule based on volume conditions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.threshold_multiplier = self.config.get('threshold_multiplier', 1.5)
        self.baseline_period = self.config.get('baseline_period', 20)

    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate volume condition.

        Args:
            df: DataFrame with volume data
            row_idx: Current row index

        Returns:
            True if volume exceeds threshold
        """
        if row_idx >= len(df) or 'volume' not in df.columns:
            return False

        current_volume = df.iloc[row_idx]['volume']

        # Calculate average volume
        if row_idx < self.baseline_period:
            return False

        avg_volume = df.iloc[row_idx - self.baseline_period:row_idx]['volume'].mean()

        return current_volume > (avg_volume * self.threshold_multiplier)

    def get_description(self) -> str:
        """Get rule description."""
        return f"Volume > {self.threshold_multiplier}x {self.baseline_period}-period average"


class TrendRule(BaseRule):
    """Rule based on trend detection."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.lookback = self.config.get('lookback', 5)
        self.trend_type = self.config.get('trend_type', 'up')  # 'up' or 'down'

    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate trend condition.

        Args:
            df: DataFrame with price data
            row_idx: Current row index

        Returns:
            True if trend condition is met
        """
        if row_idx < self.lookback or row_idx >= len(df):
            return False

        prices = df.iloc[row_idx - self.lookback:row_idx + 1]['close_price']

        if self.trend_type == 'up':
            # Check if prices are generally increasing
            return prices.iloc[-1] > prices.iloc[0]
        elif self.trend_type == 'down':
            # Check if prices are generally decreasing
            return prices.iloc[-1] < prices.iloc[0]

        return False

    def get_description(self) -> str:
        """Get rule description."""
        return f"{self.trend_type.capitalize()} trend over {self.lookback} periods"
