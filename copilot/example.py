"""
Example script demonstrating the On-Chain Trading Analysis Toolkit.

This script shows how to:
1. Fetch data from Binance
2. Add technical indicators
3. Create a simple trading strategy
4. Backtest the strategy
5. Analyze results
"""

import sys
from pathlib import Path

# Add copilot to path
sys.path.insert(0, str(Path(__file__).parent))

from copilot.data.binance_source import BinanceDataSource
from copilot.features.technical_indicators import MovingAverageIndicator, RSIIndicator
from copilot.core.base import BaseStrategy
from copilot.backtest.backtester import Backtester
from copilot.pipeline.data_pipeline import DataPipeline
import pandas as pd


class SimpleMAStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    Buy when fast MA crosses above slow MA
    Sell when fast MA crosses below slow MA
    """
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MA crossover."""
        df = df.copy()
        df['signal'] = 0
        
        # Ensure we have the required columns
        if 'sma_20' not in df.columns or 'sma_50' not in df.columns:
            print("Warning: Required MA columns not found")
            return df
        
        # Buy signal: fast MA crosses above slow MA
        bullish_cross = (
            (df['sma_20'] > df['sma_50']) & 
            (df['sma_20'].shift(1) <= df['sma_50'].shift(1))
        )
        df.loc[bullish_cross, 'signal'] = 1
        
        # Sell signal: fast MA crosses below slow MA
        bearish_cross = (
            (df['sma_20'] < df['sma_50']) & 
            (df['sma_20'].shift(1) >= df['sma_50'].shift(1))
        )
        df.loc[bearish_cross, 'signal'] = -1
        
        return df
    
    def should_buy(self, row: pd.Series) -> bool:
        """Check if should buy."""
        return row.get('signal', 0) == 1
    
    def should_sell(self, row: pd.Series) -> bool:
        """Check if should sell."""
        return row.get('signal', 0) == -1


def main():
    """Main execution function."""
    print("=" * 60)
    print("On-Chain Trading Analysis Toolkit - Example")
    print("=" * 60)
    print()
    
    # Configuration
    SYMBOL = 'BTCUSDT'
    START_DATE = '2024-01-01'
    END_DATE = '2024-01-31'
    INTERVAL = '1h'
    INITIAL_BALANCE = 10000.0
    
    print("Configuration:")
    print(f"  Symbol: {SYMBOL}")
    print(f"  Period: {START_DATE} to {END_DATE}")
    print(f"  Interval: {INTERVAL}")
    print(f"  Initial Balance: ${INITIAL_BALANCE:,.2f}")
    print()
    
    # Step 1: Fetch Data
    print("Step 1: Fetching data from Binance...")
    try:
        data_source = BinanceDataSource()
        df = data_source.fetch_data(
            symbol=SYMBOL,
            start_time=START_DATE,
            end_time=END_DATE,
            interval=INTERVAL
        )
        print(f"  ✓ Fetched {len(df)} data points")
        print(f"  Price range: ${df['close_price'].min():.2f} - ${df['close_price'].max():.2f}")
    except Exception as e:
        print(f"  ✗ Error fetching data: {str(e)}")
        print("  Note: This example requires internet connection to fetch data from Binance.")
        return
    
    print()
    
    # Step 2: Add Technical Indicators
    print("Step 2: Adding technical indicators...")
    ma_indicator = MovingAverageIndicator({'periods': [20, 50], 'type': 'sma'})
    df = ma_indicator.calculate(df)
    
    rsi_indicator = RSIIndicator({'period': 14})
    df = rsi_indicator.calculate(df)
    
    # Remove NaN values
    df = df.dropna()
    print(f"  ✓ Added Moving Averages (20, 50)")
    print(f"  ✓ Added RSI (14)")
    print(f"  Data points after indicator calculation: {len(df)}")
    print()
    
    # Step 3: Create Strategy
    print("Step 3: Creating trading strategy...")
    strategy = SimpleMAStrategy()
    print("  ✓ Simple MA Crossover Strategy initialized")
    print()
    
    # Step 4: Backtest
    print("Step 4: Running backtest...")
    backtester = Backtester({
        'initial_balance': INITIAL_BALANCE,
        'commission': 0.001,  # 0.1%
        'slippage': 0.0005    # 0.05%
    })
    
    results = backtester.run(df=df, strategy=strategy)
    print("  ✓ Backtest complete")
    print()
    
    # Step 5: Display Results
    print("=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print()
    
    print("Performance Summary:")
    print(f"  Initial Balance:  ${results['initial_balance']:,.2f}")
    print(f"  Final Balance:    ${results['final_balance']:,.2f}")
    print(f"  Profit/Loss:      ${results['profit_loss']:,.2f} ({results['profit_loss_pct']:.2f}%)")
    print()
    
    print("Trading Activity:")
    print(f"  Number of Trades: {results['num_trades']}")
    print()
    
    if results['metrics']:
        print("Risk Metrics:")
        metrics = results['metrics']
        print(f"  Sharpe Ratio:     {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"  Max Drawdown:     {metrics.get('max_drawdown_pct', 0):.2f}%")
        print(f"  Volatility:       {metrics.get('volatility', 0):.4f}")
        print()
    
    # Trade Analysis
    trade_analysis = backtester.get_trade_analysis()
    if trade_analysis:
        print("Trade Analysis:")
        print(f"  Total Trades:     {trade_analysis.get('total_trades', 0)}")
        print(f"  Winning Trades:   {trade_analysis.get('winning_trades', 0)}")
        print(f"  Losing Trades:    {trade_analysis.get('losing_trades', 0)}")
        print(f"  Win Rate:         {trade_analysis.get('win_rate', 0) * 100:.2f}%")
        
        if trade_analysis.get('avg_win', 0) > 0:
            print(f"  Average Win:      ${trade_analysis.get('avg_win', 0):.2f}")
        if trade_analysis.get('avg_loss', 0) < 0:
            print(f"  Average Loss:     ${trade_analysis.get('avg_loss', 0):.2f}")
        
        print()
    
    # Display first few trades
    if results['trades'] and len(results['trades']) > 0:
        print("Recent Trades (first 5):")
        for i, trade in enumerate(results['trades'][:5]):
            print(f"  {i+1}. {trade['type'].upper():4s} @ ${trade['price']:.2f} - Balance: ${trade['balance']:.2f}")
    
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
