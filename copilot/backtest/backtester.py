"""
Backtesting engine for strategy evaluation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from copilot.core.base import BaseStrategy
from copilot.core.exceptions import BacktestError
from copilot.backtest.metrics import PerformanceMetrics


class Backtester:
    """Backtesting engine for evaluating trading strategies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initial_balance = self.config.get('initial_balance', 10000.0)
        self.commission = self.config.get('commission', 0.001)  # 0.1%
        self.slippage = self.config.get('slippage', 0.0005)  # 0.05%
        self.strategy: Optional[BaseStrategy] = None
        self.data: Optional[pd.DataFrame] = None
        self.results: Optional[Dict[str, Any]] = None

    def set_strategy(self, strategy: BaseStrategy):
        """
        Set the trading strategy.

        Args:
            strategy: Strategy instance
        """
        self.strategy = strategy

    def load_data(self, df: pd.DataFrame):
        """
        Load historical data.

        Args:
            df: DataFrame with historical market data
        """
        if df.empty:
            raise BacktestError("Cannot load empty DataFrame")
        self.data = df.copy()

    def run(
        self,
        df: Optional[pd.DataFrame] = None,
        strategy: Optional[BaseStrategy] = None
    ) -> Dict[str, Any]:
        """
        Run backtest.

        Args:
            df: DataFrame with historical data (optional if already loaded)
            strategy: Strategy instance (optional if already set)

        Returns:
            Dictionary with backtest results

        Raises:
            BacktestError: If backtest fails
        """
        if df is not None:
            self.load_data(df)
        if strategy is not None:
            self.set_strategy(strategy)

        if self.strategy is None:
            raise BacktestError("Strategy not set")
        if self.data is None:
            raise BacktestError("Data not loaded")

        # Generate signals
        try:
            signals_df = self.strategy.generate_signals(self.data)
        except Exception as e:
            raise BacktestError(f"Failed to generate signals: {str(e)}")

        # Execute trades
        self.results = self._execute_backtest(signals_df)

        return self.results

    def _execute_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute backtest simulation.

        Args:
            df: DataFrame with signals

        Returns:
            Dictionary with backtest results
        """
        balance = self.initial_balance
        crypto_balance = 0.0
        position = 0  # 0: no position, 1: long
        trades: List[Dict[str, Any]] = []
        equity_curve = []
        returns = []

        for idx, row in df.iterrows():
            # Calculate current equity
            if position == 1:
                current_equity = crypto_balance * row['close_price']
            else:
                current_equity = balance
            equity_curve.append(current_equity)

            # Buy signal
            if row.get('signal') == 1 and position == 0:
                if balance > 0:
                    # Apply commission and slippage
                    execution_price = row['close_price'] * (1 + self.slippage)
                    crypto_balance = (balance * (1 - self.commission)) / execution_price
                    
                    trades.append({
                        'type': 'buy',
                        'price': execution_price,
                        'timestamp': row.get('open_time', idx),
                        'balance': balance,
                        'crypto_balance': crypto_balance,
                    })
                    
                    balance = 0
                    position = 1

            # Sell signal
            elif row.get('signal') == -1 and position == 1:
                if crypto_balance > 0:
                    # Apply commission and slippage
                    execution_price = row['close_price'] * (1 - self.slippage)
                    balance = crypto_balance * execution_price * (1 - self.commission)
                    
                    trades.append({
                        'type': 'sell',
                        'price': execution_price,
                        'timestamp': row.get('open_time', idx),
                        'balance': balance,
                        'crypto_balance': crypto_balance,
                    })
                    
                    crypto_balance = 0
                    position = 0

        # Close any open position at the end
        if position == 1:
            final_price = df.iloc[-1]['close_price'] * (1 - self.slippage)
            balance = crypto_balance * final_price * (1 - self.commission)
            trades.append({
                'type': 'sell',
                'price': final_price,
                'timestamp': df.iloc[-1].get('open_time', df.index[-1]),
                'balance': balance,
                'crypto_balance': crypto_balance,
            })

        # Calculate metrics
        metrics = PerformanceMetrics.calculate_metrics(
            equity_curve=pd.Series(equity_curve),
            trades=trades,
            initial_balance=self.initial_balance
        )

        return {
            'initial_balance': self.initial_balance,
            'final_balance': balance,
            'profit_loss': balance - self.initial_balance,
            'profit_loss_pct': ((balance - self.initial_balance) / self.initial_balance) * 100,
            'num_trades': len(trades),
            'trades': trades,
            'equity_curve': equity_curve,
            'metrics': metrics,
        }

    def get_results(self) -> Optional[Dict[str, Any]]:
        """
        Get backtest results.

        Returns:
            Dictionary with results or None if backtest hasn't run
        """
        return self.results

    def get_trade_analysis(self) -> Dict[str, Any]:
        """
        Analyze individual trades.

        Returns:
            Dictionary with trade analysis
        """
        if self.results is None or not self.results['trades']:
            return {}

        trades = self.results['trades']
        
        # Pair buy and sell trades
        trade_pairs = []
        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades) and trades[i]['type'] == 'buy' and trades[i + 1]['type'] == 'sell':
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                pnl = sell_trade['balance'] - buy_trade['balance']
                pnl_pct = (pnl / buy_trade['balance']) * 100
                
                trade_pairs.append({
                    'buy_price': buy_trade['price'],
                    'sell_price': sell_trade['price'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'buy_timestamp': buy_trade['timestamp'],
                    'sell_timestamp': sell_trade['timestamp'],
                })

        if not trade_pairs:
            return {}

        # Calculate statistics
        pnls = [t['pnl'] for t in trade_pairs]
        winning_trades = [t for t in trade_pairs if t['pnl'] > 0]
        losing_trades = [t for t in trade_pairs if t['pnl'] <= 0]

        return {
            'total_trades': len(trade_pairs),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trade_pairs) if trade_pairs else 0,
            'avg_win': np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0,
            'largest_win': max(pnls) if pnls else 0,
            'largest_loss': min(pnls) if pnls else 0,
            'trade_pairs': trade_pairs,
        }
