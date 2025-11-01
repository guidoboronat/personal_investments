"""
Performance metrics calculation for backtesting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class PerformanceMetrics:
    """Calculate performance metrics for backtesting results."""

    @staticmethod
    def calculate_metrics(
        equity_curve: pd.Series,
        trades: List[Dict[str, Any]],
        initial_balance: float,
        risk_free_rate: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.

        Args:
            equity_curve: Series of equity values over time
            trades: List of executed trades
            initial_balance: Initial capital
            risk_free_rate: Risk-free rate for Sharpe ratio

        Returns:
            Dictionary with performance metrics
        """
        if len(equity_curve) == 0:
            return {}

        # Convert to pandas Series if needed
        if not isinstance(equity_curve, pd.Series):
            equity_curve = pd.Series(equity_curve)

        # Calculate returns
        returns = equity_curve.pct_change().dropna()

        # Basic metrics
        final_balance = equity_curve.iloc[-1]
        total_return = (final_balance - initial_balance) / initial_balance
        total_return_pct = total_return * 100

        # Risk metrics
        volatility = returns.std()
        sharpe_ratio = PerformanceMetrics._calculate_sharpe_ratio(returns, risk_free_rate)
        max_drawdown = PerformanceMetrics._calculate_max_drawdown(equity_curve)
        max_drawdown_pct = max_drawdown * 100

        # Trade metrics
        num_trades = len(trades)
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'num_trades': num_trades,
            'final_balance': final_balance,
        }

    @staticmethod
    def _calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of trading periods per year

        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / periods_per_year)
        return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()

    @staticmethod
    def _calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown.

        Args:
            equity_curve: Series of equity values

        Returns:
            Maximum drawdown as decimal
        """
        if len(equity_curve) == 0:
            return 0.0

        cumulative = equity_curve
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return abs(drawdown.min())

    @staticmethod
    def _calculate_calmar_ratio(
        total_return: float,
        max_drawdown: float,
        years: float = 1.0
    ) -> float:
        """
        Calculate Calmar ratio.

        Args:
            total_return: Total return as decimal
            max_drawdown: Maximum drawdown as decimal
            years: Number of years

        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return 0.0

        annualized_return = (1 + total_return) ** (1 / years) - 1
        return annualized_return / max_drawdown

    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sortino ratio (uses downside deviation).

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of trading periods per year

        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / periods_per_year)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        downside_std = downside_returns.std()
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std

    @staticmethod
    def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate win rate from trades.

        Args:
            trades: List of trade dictionaries

        Returns:
            Win rate as decimal
        """
        if len(trades) < 2:
            return 0.0

        # Pair buy and sell trades
        winning_trades = 0
        total_pairs = 0

        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades) and trades[i]['type'] == 'buy' and trades[i + 1]['type'] == 'sell':
                if trades[i + 1]['balance'] > trades[i]['balance']:
                    winning_trades += 1
                total_pairs += 1

        return winning_trades / total_pairs if total_pairs > 0 else 0.0

    @staticmethod
    def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate profit factor (gross profit / gross loss).

        Args:
            trades: List of trade dictionaries

        Returns:
            Profit factor
        """
        if len(trades) < 2:
            return 0.0

        gross_profit = 0.0
        gross_loss = 0.0

        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades) and trades[i]['type'] == 'buy' and trades[i + 1]['type'] == 'sell':
                pnl = trades[i + 1]['balance'] - trades[i]['balance']
                if pnl > 0:
                    gross_profit += pnl
                else:
                    gross_loss += abs(pnl)

        return gross_profit / gross_loss if gross_loss > 0 else 0.0
