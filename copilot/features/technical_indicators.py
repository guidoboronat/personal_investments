"""
Technical indicators implementation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from copilot.core.base import BaseIndicator
from copilot.core.exceptions import ValidationError


class MovingAverageIndicator(BaseIndicator):
    """Simple and Exponential Moving Average indicator."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.periods = self.config.get('periods', [20, 50])
        self.ma_type = self.config.get('type', 'sma')  # 'sma' or 'ema'

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate moving averages.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with MA columns added
        """
        if not self.validate_inputs(df):
            raise ValidationError("Invalid input data for MovingAverageIndicator")

        df = df.copy()

        for period in self.periods:
            if self.ma_type == 'sma':
                df[f'sma_{period}'] = df['close_price'].rolling(window=period).mean()
            elif self.ma_type == 'ema':
                df[f'ema_{period}'] = df['close_price'].ewm(span=period, adjust=False).mean()

        return df


class RSIIndicator(BaseIndicator):
    """Relative Strength Index indicator."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.period = self.config.get('period', 14)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with RSI column added
        """
        if not self.validate_inputs(df):
            raise ValidationError("Invalid input data for RSIIndicator")

        df = df.copy()

        # Calculate price changes
        delta = df['close_price'].diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        # Calculate RS and RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        return df


class MACDIndicator(BaseIndicator):
    """Moving Average Convergence Divergence indicator."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.fast_period = self.config.get('fast_period', 12)
        self.slow_period = self.config.get('slow_period', 26)
        self.signal_period = self.config.get('signal_period', 9)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD, signal line, and histogram.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with MACD columns added
        """
        if not self.validate_inputs(df):
            raise ValidationError("Invalid input data for MACDIndicator")

        df = df.copy()

        # Calculate MACD line
        ema_fast = df['close_price'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['close_price'].ewm(span=self.slow_period, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow

        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()

        # Calculate histogram
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        return df


class BollingerBandsIndicator(BaseIndicator):
    """Bollinger Bands indicator."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.period = self.config.get('period', 20)
        self.num_std = self.config.get('num_std', 2)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with Bollinger Bands columns added
        """
        if not self.validate_inputs(df):
            raise ValidationError("Invalid input data for BollingerBandsIndicator")

        df = df.copy()

        # Calculate middle band (SMA)
        df['bb_middle'] = df['close_price'].rolling(window=self.period).mean()

        # Calculate standard deviation
        std = df['close_price'].rolling(window=self.period).std()

        # Calculate upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (std * self.num_std)
        df['bb_lower'] = df['bb_middle'] - (std * self.num_std)

        # Calculate bandwidth
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        return df


class ATRIndicator(BaseIndicator):
    """Average True Range indicator."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.period = self.config.get('period', 14)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ATR.

        Args:
            df: DataFrame with OHLC data

        Returns:
            DataFrame with ATR column added
        """
        if not self.validate_inputs(df):
            raise ValidationError("Invalid input data for ATRIndicator")

        df = df.copy()

        # Calculate True Range
        df['high_low'] = df['high_price'] - df['low_price']
        df['high_close'] = abs(df['high_price'] - df['close_price'].shift())
        df['low_close'] = abs(df['low_price'] - df['close_price'].shift())

        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)

        # Calculate ATR
        df['atr'] = df['true_range'].rolling(window=self.period).mean()

        # Clean up intermediate columns
        df = df.drop(['high_low', 'high_close', 'low_close', 'true_range'], axis=1)

        return df
