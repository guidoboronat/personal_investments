"""
Custom exceptions for the trading toolkit.
"""


class TradingToolkitError(Exception):
    """Base exception for all trading toolkit errors."""
    pass


class DataFetchError(TradingToolkitError):
    """Raised when data fetching fails."""
    pass


class ValidationError(TradingToolkitError):
    """Raised when data validation fails."""
    pass


class BacktestError(TradingToolkitError):
    """Raised when backtesting encounters an error."""
    pass


class AlertError(TradingToolkitError):
    """Raised when alert system encounters an error."""
    pass


class ConfigurationError(TradingToolkitError):
    """Raised when configuration is invalid."""
    pass


class StrategyError(TradingToolkitError):
    """Raised when strategy execution encounters an error."""
    pass
