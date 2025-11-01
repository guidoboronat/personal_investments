# On-Chain Trading Analysis Toolkit

A comprehensive, modular framework for analyzing on-chain trading data, building trading strategies, and backtesting them with advanced monitoring and alerting capabilities.

## Features

### Core Modules

- **Core**: Base classes, utilities, and exceptions for the framework
- **Data**: Data fetching from Binance and on-chain sources, preprocessing utilities
- **Features**: Technical indicators (MA, RSI, MACD, Bollinger Bands, ATR) and feature engineering
- **Pipeline**: Orchestration for data and strategy execution
- **Rules**: Trading rule definitions and rule engine
- **Backtest**: Comprehensive backtesting engine with performance metrics
- **Alerts**: Alert management and notification system

## Installation

### From Source

```bash
cd copilot
pip install -e .
```

### Development Installation

```bash
cd copilot
pip install -e ".[dev]"
```

## Quick Start

### 1. Fetch Data

```python
from copilot.data.binance_source import BinanceDataSource

# Initialize data source
source = BinanceDataSource()

# Fetch historical data
df = source.fetch_data(
    symbol='BTCUSDT',
    start_time='2024-01-01',
    end_time='2024-01-31',
    interval='1h'
)
```

### 2. Add Technical Indicators

```python
from copilot.features.technical_indicators import MovingAverageIndicator, RSIIndicator

# Add moving averages
ma_indicator = MovingAverageIndicator({'periods': [20, 50], 'type': 'sma'})
df = ma_indicator.calculate(df)

# Add RSI
rsi_indicator = RSIIndicator({'period': 14})
df = rsi_indicator.calculate(df)
```

### 3. Create a Trading Strategy

```python
from copilot.core.base import BaseStrategy
import pandas as pd

class MACrossStrategy(BaseStrategy):
    """Simple moving average crossover strategy."""
    
    def generate_signals(self, df):
        df = df.copy()
        df['signal'] = 0
        
        # Buy when fast MA crosses above slow MA
        df.loc[(df['sma_20'] > df['sma_50']) & 
               (df['sma_20'].shift(1) <= df['sma_50'].shift(1)), 'signal'] = 1
        
        # Sell when fast MA crosses below slow MA
        df.loc[(df['sma_20'] < df['sma_50']) & 
               (df['sma_20'].shift(1) >= df['sma_50'].shift(1)), 'signal'] = -1
        
        return df
    
    def should_buy(self, row):
        return row.get('signal') == 1
    
    def should_sell(self, row):
        return row.get('signal') == -1
```

### 4. Backtest the Strategy

```python
from copilot.backtest.backtester import Backtester

# Initialize backtester
backtester = Backtester({
    'initial_balance': 10000,
    'commission': 0.001,
    'slippage': 0.0005
})

# Run backtest
strategy = MACrossStrategy()
results = backtester.run(df=df, strategy=strategy)

print(f"Initial Balance: ${results['initial_balance']:.2f}")
print(f"Final Balance: ${results['final_balance']:.2f}")
print(f"Profit/Loss: ${results['profit_loss']:.2f} ({results['profit_loss_pct']:.2f}%)")
print(f"Number of Trades: {results['num_trades']}")
print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['metrics']['max_drawdown_pct']:.2f}%")
```

### 5. Use Pipeline for End-to-End Workflow

```python
from copilot.pipeline.data_pipeline import DataPipeline
from copilot.pipeline.strategy_pipeline import StrategyPipeline

# Set up data pipeline
data_pipeline = DataPipeline()
data_pipeline.set_data_source(source)
data_pipeline.add_indicator(ma_indicator)
data_pipeline.add_indicator(rsi_indicator)

# Fetch and process data
df = data_pipeline.run('BTCUSDT', '2024-01-01', '2024-01-31', interval='1h')

# Set up strategy pipeline
strategy_pipeline = StrategyPipeline()
results = strategy_pipeline.run(df, strategy, initial_balance=10000)
```

## Configuration

Configuration files are located in `config/`:

- `default_config.yaml`: YAML format configuration
- `default_config.json`: JSON format configuration

Load configuration:

```python
from copilot.config import ConfigLoader

config = ConfigLoader.load()  # Loads default config
# or
config = ConfigLoader.load('path/to/custom_config.yaml')
```

## Testing

Run tests:

```bash
cd copilot
python -m pytest tests/
```

Run tests with coverage:

```bash
python -m pytest tests/ --cov=copilot --cov-report=html
```

## Module Structure

```
copilot/
├── core/               # Base classes and utilities
│   ├── __init__.py
│   ├── base.py         # Abstract base classes
│   ├── exceptions.py   # Custom exceptions
│   └── utils.py        # Utility functions
├── data/               # Data fetching and preprocessing
│   ├── __init__.py
│   ├── binance_source.py
│   ├── onchain_source.py
│   └── preprocessor.py
├── features/           # Technical indicators and feature engineering
│   ├── __init__.py
│   ├── technical_indicators.py
│   └── feature_engineering.py
├── pipeline/           # Data and strategy pipelines
│   ├── __init__.py
│   ├── data_pipeline.py
│   └── strategy_pipeline.py
├── rules/              # Trading rules and rule engine
│   ├── __init__.py
│   ├── trading_rules.py
│   └── rule_engine.py
├── backtest/           # Backtesting engine and metrics
│   ├── __init__.py
│   ├── backtester.py
│   └── metrics.py
├── alerts/             # Alert management and types
│   ├── __init__.py
│   ├── alert_manager.py
│   └── alert_types.py
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_backtest.py
│   ├── test_rules.py
│   └── test_alerts.py
└── config/             # Configuration files
    ├── __init__.py
    ├── default_config.yaml
    └── default_config.json
```

## Contributing

Contributions are welcome! Please ensure:

1. Code follows existing style conventions
2. All tests pass
3. New features include tests
4. Documentation is updated

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
