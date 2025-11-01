"""
Utility functions for the trading toolkit.
"""

import datetime
from typing import Optional, List
import pandas as pd
import numpy as np


def timestamp_to_datetime(timestamp_ms: int) -> datetime.datetime:
    """
    Convert timestamp in milliseconds to datetime object.

    Args:
        timestamp_ms: Timestamp in milliseconds

    Returns:
        datetime object
    """
    return datetime.datetime.fromtimestamp(timestamp_ms / 1000)


def datetime_to_timestamp(dt: datetime.datetime) -> int:
    """
    Convert datetime object to timestamp in milliseconds.

    Args:
        dt: datetime object

    Returns:
        Timestamp in milliseconds
    """
    return int(dt.timestamp() * 1000)


def convertir_a_timestamp(fecha_str: str) -> int:
    """
    Convert date string to timestamp in milliseconds.

    Args:
        fecha_str: Date string in 'YYYY-MM-DD' format

    Returns:
        Timestamp in milliseconds
    """
    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(fecha.timestamp() * 1000)


def validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> bool:
    """
    Validate DataFrame has required columns and data.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Returns:
        True if valid

    Raises:
        ValueError if validation fails
    """
    if df is None or df.empty:
        raise ValueError("DataFrame is None or empty")

    if required_columns:
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    return True


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate simple returns from price series.

    Args:
        prices: Series of prices

    Returns:
        Series of returns
    """
    return prices.pct_change()


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate log returns from price series.

    Args:
        prices: Series of prices

    Returns:
        Series of log returns
    """
    return np.log(prices / prices.shift(1))


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252) -> float:
    """
    Calculate Sharpe ratio from returns.

    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (annualized)
        periods: Number of periods per year (252 for daily)

    Returns:
        Sharpe ratio
    """
    if returns.std() == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods)
    return np.sqrt(periods) * excess_returns.mean() / returns.std()


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown from price series.

    Args:
        prices: Series of prices

    Returns:
        Maximum drawdown as a decimal (e.g., 0.15 for 15%)
    """
    cumulative = (1 + calculate_returns(prices)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def resample_ohlcv(df: pd.DataFrame, timeframe: str, time_column: str = 'open_time') -> pd.DataFrame:
    """
    Resample OHLCV data to different timeframe.

    Args:
        df: DataFrame with OHLCV data
        timeframe: Target timeframe (e.g., '1H', '4H', '1D')
        time_column: Name of the time column

    Returns:
        Resampled DataFrame
    """
    df = df.copy()
    df.set_index(time_column, inplace=True)

    resampled = pd.DataFrame()
    resampled['open_price'] = df['open_price'].resample(timeframe).first()
    resampled['high_price'] = df['high_price'].resample(timeframe).max()
    resampled['low_price'] = df['low_price'].resample(timeframe).min()
    resampled['close_price'] = df['close_price'].resample(timeframe).last()
    resampled['volume'] = df['volume'].resample(timeframe).sum()

    return resampled.reset_index()
