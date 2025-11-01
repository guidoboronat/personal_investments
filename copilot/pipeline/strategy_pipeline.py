"""
Strategy pipeline for executing trading strategies.
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from copilot.core.base import BaseStrategy
from copilot.core.exceptions import StrategyError, ValidationError


class StrategyPipeline:
    """Pipeline for executing trading strategies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.strategy: Optional[BaseStrategy] = None
        self.data: Optional[pd.DataFrame] = None
        self.signals: Optional[pd.DataFrame] = None

    def set_strategy(self, strategy: BaseStrategy):
        """
        Set the trading strategy.

        Args:
            strategy: Strategy instance
        """
        self.strategy = strategy

    def load_data(self, df: pd.DataFrame):
        """
        Load data into the pipeline.

        Args:
            df: DataFrame with market data and indicators
        """
        if df.empty:
            raise ValidationError("Cannot load empty DataFrame")
        self.data = df.copy()

    def generate_signals(self) -> pd.DataFrame:
        """
        Generate trading signals using the strategy.

        Returns:
            DataFrame with signals

        Raises:
            StrategyError: If strategy is not set or execution fails
        """
        if self.strategy is None:
            raise StrategyError("Strategy not set. Call set_strategy() first.")

        if self.data is None:
            raise StrategyError("Data not loaded. Call load_data() first.")

        try:
            self.signals = self.strategy.generate_signals(self.data)
            return self.signals
        except Exception as e:
            raise StrategyError(f"Failed to generate signals: {str(e)}")

    def execute_strategy(self, initial_balance: float = 10000.0) -> Dict[str, Any]:
        """
        Execute the strategy and track trades.

        Args:
            initial_balance: Initial capital

        Returns:
            Dictionary with execution results
        """
        if self.signals is None:
            self.generate_signals()

        self.strategy.reset()
        balance = initial_balance
        crypto_balance = 0.0
        trades = []

        for idx, row in self.signals.iterrows():
            # Buy signal
            if row.get('signal') == 1 and self.strategy.position == 0:
                if balance > 0:
                    crypto_balance = balance / row['close_price']
                    self.strategy.record_trade('buy', row['close_price'], row.get('open_time'), crypto_balance)
                    self.strategy.position = 1
                    trades.append({
                        'type': 'buy',
                        'price': row['close_price'],
                        'timestamp': row.get('open_time'),
                        'balance': balance,
                    })
                    balance = 0

            # Sell signal
            elif row.get('signal') == -1 and self.strategy.position == 1:
                if crypto_balance > 0:
                    balance = crypto_balance * row['close_price']
                    self.strategy.record_trade('sell', row['close_price'], row.get('open_time'), crypto_balance)
                    self.strategy.position = 0
                    trades.append({
                        'type': 'sell',
                        'price': row['close_price'],
                        'timestamp': row.get('open_time'),
                        'balance': balance,
                    })
                    crypto_balance = 0

        # Calculate final balance
        if crypto_balance > 0:
            final_price = self.signals.iloc[-1]['close_price']
            balance = crypto_balance * final_price

        return {
            'initial_balance': initial_balance,
            'final_balance': balance,
            'profit_loss': balance - initial_balance,
            'profit_loss_pct': ((balance - initial_balance) / initial_balance) * 100,
            'num_trades': len(trades),
            'trades': trades,
        }

    def run(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        initial_balance: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Run the complete strategy pipeline.

        Args:
            df: DataFrame with market data
            strategy: Trading strategy
            initial_balance: Initial capital

        Returns:
            Dictionary with execution results
        """
        self.load_data(df)
        self.set_strategy(strategy)
        return self.execute_strategy(initial_balance)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get strategy execution statistics.

        Returns:
            Dictionary with statistics
        """
        if self.signals is None:
            raise StrategyError("No signals generated yet")

        buy_signals = (self.signals['signal'] == 1).sum()
        sell_signals = (self.signals['signal'] == -1).sum()
        total_signals = buy_signals + sell_signals

        return {
            'total_periods': len(self.signals),
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_signals': total_signals,
            'signal_rate': total_signals / len(self.signals) if len(self.signals) > 0 else 0,
        }
