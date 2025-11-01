"""
Feature engineering utilities.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from copilot.core.exceptions import ValidationError


class FeatureEngineer:
    """Feature engineering for trading data."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price-based features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with price features added
        """
        df = df.copy()

        # Price changes
        df['price_change'] = df['close_price'].diff()
        df['price_change_pct'] = df['close_price'].pct_change()

        # High-Low range
        df['high_low_range'] = df['high_price'] - df['low_price']
        df['high_low_pct'] = (df['high_price'] - df['low_price']) / df['low_price']

        # Open-Close range
        df['open_close_range'] = df['close_price'] - df['open_price']
        df['open_close_pct'] = (df['close_price'] - df['open_price']) / df['open_price']

        # Price position in range
        df['price_position'] = (df['close_price'] - df['low_price']) / (df['high_price'] - df['low_price'])

        return df

    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based features.

        Args:
            df: DataFrame with volume data

        Returns:
            DataFrame with volume features added
        """
        df = df.copy()

        # Volume changes
        df['volume_change'] = df['volume'].diff()
        df['volume_change_pct'] = df['volume'].pct_change()

        # Volume moving averages
        df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()

        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']

        # Price-Volume
        df['price_volume'] = df['close_price'] * df['volume']

        return df

    def add_momentum_features(self, df: pd.DataFrame, periods: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Add momentum features.

        Args:
            df: DataFrame with price data
            periods: List of lookback periods

        Returns:
            DataFrame with momentum features added
        """
        df = df.copy()

        if periods is None:
            periods = [5, 10, 20]

        for period in periods:
            # Rate of Change
            df[f'roc_{period}'] = df['close_price'].pct_change(periods=period)

            # Momentum
            df[f'momentum_{period}'] = df['close_price'] - df['close_price'].shift(period)

        return df

    def add_volatility_features(self, df: pd.DataFrame, periods: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Add volatility features.

        Args:
            df: DataFrame with price data
            periods: List of lookback periods

        Returns:
            DataFrame with volatility features added
        """
        df = df.copy()

        if periods is None:
            periods = [5, 10, 20]

        for period in periods:
            # Standard deviation
            df[f'std_{period}'] = df['close_price'].rolling(window=period).std()

            # Historical volatility
            returns = df['close_price'].pct_change()
            df[f'volatility_{period}'] = returns.rolling(window=period).std() * np.sqrt(period)

        return df

    def add_lag_features(self, df: pd.DataFrame, columns: List[str], lags: List[int]) -> pd.DataFrame:
        """
        Add lagged features.

        Args:
            df: DataFrame with data
            columns: List of columns to create lags for
            lags: List of lag periods

        Returns:
            DataFrame with lagged features added
        """
        df = df.copy()

        for col in columns:
            if col not in df.columns:
                raise ValidationError(f"Column '{col}' not found in DataFrame")

            for lag in lags:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)

        return df

    def add_rolling_statistics(
        self,
        df: pd.DataFrame,
        columns: List[str],
        windows: List[int],
        stats: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Add rolling statistics.

        Args:
            df: DataFrame with data
            columns: List of columns to calculate statistics for
            windows: List of window sizes
            stats: List of statistics ('mean', 'std', 'min', 'max')

        Returns:
            DataFrame with rolling statistics added
        """
        df = df.copy()

        if stats is None:
            stats = ['mean', 'std']

        for col in columns:
            if col not in df.columns:
                raise ValidationError(f"Column '{col}' not found in DataFrame")

            for window in windows:
                for stat in stats:
                    if stat == 'mean':
                        df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
                    elif stat == 'std':
                        df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
                    elif stat == 'min':
                        df[f'{col}_rolling_min_{window}'] = df[col].rolling(window=window).min()
                    elif stat == 'max':
                        df[f'{col}_rolling_max_{window}'] = df[col].rolling(window=window).max()

        return df

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all features at once.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with all features added
        """
        df = self.add_price_features(df)
        df = self.add_volume_features(df)
        df = self.add_momentum_features(df)
        df = self.add_volatility_features(df)

        return df
