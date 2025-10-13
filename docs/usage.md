# Usage Examples

## Basic Signal Parsing

```python
from src.parsers import TelegramSignalParser

# Initialize parser
parser = TelegramSignalParser("my_telegram_channel")

# Parse a signal message
message = "🚀 BUY #BTCUSDT @ 45000 🎯 TP: 50000 🛑 SL: 42000"
signals = parser.parse_message(message)

for signal in signals:
    print(f"Symbol: {signal.symbol}")
    print(f"Action: {signal.action}")
    print(f"Entry: {signal.entry_price}")
    print(f"Take Profit: {signal.take_profit}")
    print(f"Stop Loss: {signal.stop_loss}")
```

## Basic Backtesting

```python
from src.backtesting import BacktestEngine
from src.parsers import Signal

# Initialize backtest engine
engine = BacktestEngine(initial_capital=10000, commission=0.001)

# Create a sample signal
signal = Signal(
    symbol="BTCUSDT",
    action="BUY",
    entry_price=45000,
    stop_loss=42000,
    take_profit=50000
)

# Execute the signal
result = engine.execute_signal(signal, current_price=45000)
print(f"Signal executed: {result['executed']}")

# Close the position later
close_signal = Signal(
    symbol="BTCUSDT",
    action="SELL",
    entry_price=48000  # Exit at different price
)

close_result = engine.execute_signal(close_signal, current_price=48000)
print(f"Position closed. PnL: {close_result['pnl']}")

# Get performance summary
summary = engine.get_performance_summary()
print(f"Total trades: {summary['total_trades']}")
print(f"Win rate: {summary['win_rate']:.2f}%")
print(f"Total return: {summary['total_return']:.2f}%")
```

## Configuration Setup

1. Copy `config/config.template.json` to `config/config.json`
2. Fill in your API credentials
3. Configure your signal sources and backtesting parameters