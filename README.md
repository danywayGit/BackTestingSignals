# 📊 BackTesting Signals

**A comprehensive framework for extracting, backtesting, and optimizing cryptocurrency trading signals from Discord/Telegram channels.**

---

## 🎯 What It Does

1. **Extracts** trading signals from Discord channels (Meta Signals format)
2. **Backtests** signals using real Binance historical price data  
3. **Optimizes** performance by analyzing patterns (day/hour/coin combinations)
4. **Generates** actionable trading strategies with high win rates

**Results:** Optimized win rate from **49.7%** baseline to **83%+** through intelligent filtering.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Discord User Token (for signal extraction)
- Binance API access (free, for price data)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/BackTestingSignals.git
cd BackTestingSignals

# Run setup script (creates venv, installs dependencies, prompts for config)
python setup.py
```

The setup script will:
- Create virtual environment
- Install all dependencies
- Guide you through configuration (Discord token, Binance API, etc.)

### Configuration

Edit `config/config.json` with your credentials:

```json
{
  "discord_token": "YOUR_DISCORD_USER_TOKEN",
  "discord_channel_id": "YOUR_CHANNEL_ID",
  "binance": {
    "api_key": "optional",
    "api_secret": "optional"
  }
}
```

> **Getting Discord Token:** See `docs/discord-token-guide.md`

---

## 🚀 Usage

### 1. Extract Signals from Discord

```bash
# Extract all signals from a Discord channel
python extract_signals.py

# Bulk extract with custom date range
python bulk_extract.py
```

Extracted signals are saved to `data/signals/meta_signals_YYYYMMDD_HHMMSS.csv`

### 2. Run Backtest

```bash
# Interactive backtest (prompts for file selection)
python full_backtest.py

# Backtest specific file
python full_backtest.py data/signals/meta_signals_20251013_195448.csv
```

Results saved to `data/backtest_results/`

### 3. Optimize Strategies

```bash
# Analyze LONG signals (finds best days/hours/coins)
python corrected_optimization.py

# Analyze SHORT signals
python short_optimization.py
```

Results saved as JSON files with detailed breakdowns.

---

## 📈 Trading Strategies

After backtesting 989 signals, we identified optimal strategies:

### 🟢 LONG Strategy (82.1% Win Rate)

**When to Trade:**
- ✅ Days: Wednesday, Saturday, Sunday
- ✅ Hours: 01:00-03:00 UTC
- ✅ Coins: BNB, FET, DOGE, EOS, ETH

**Avoid:**
- ❌ Thursday (33.3% WR - THE THURSDAY CURSE)
- ❌ Hours: 00:00, 04:00, 05:00, 11:00
- ❌ Coins: ADA, ALGO, AR, ATOM

### 🔴 SHORT Strategy (84.6% Win Rate)

**When to Trade:**
- ✅ Days: Monday, Wednesday, Saturday, Sunday
- ✅ Hours: 04:00, 06:00, 10:00, 18:00 UTC
- ✅ Coins: FET, IMX, RUNE, TRX, DOT

**Avoid:**
- ❌ Thursday (22.2% WR)
- ❌ Friday (29.6% WR)
- ❌ Hours: 00:00, 16:00
- ❌ Coins: XTZ, LINK, XLM, XRP, BTC

> 📖 **Full Strategy Guide:** See `FINAL_TRADING_STRATEGIES.md` for complete details, risk management, and expected returns.

---

## 📁 Project Structure

```
BackTestingSignals/
├── extract_signals.py          # Main signal extraction tool
├── bulk_extract.py             # Batch extraction utility
├── full_backtest.py            # Backtesting engine
├── corrected_optimization.py   # LONG signal analysis
├── short_optimization.py       # SHORT signal analysis
├── setup.py                    # Setup wizard
│
├── src/                        # Core modules
│   ├── parsers/               # Signal format parsers
│   │   ├── discord_parser.py  # Meta Signals parser (LONG/SHORT detection)
│   │   └── base_parser.py     # Base parser interface
│   ├── backtesting/           # Backtesting logic
│   │   └── signal_backtester.py
│   ├── data/                  # Data management
│   │   ├── binance_data.py    # Binance API + caching
│   │   ├── discord_client.py  # Discord message extraction
│   │   └── storage.py         # SQLite database + CSV exports
│   └── analytics/             # Analysis tools
│       └── image_processor.py # OCR for signal images
│
├── config/                    # Configuration files
│   └── config.json           # API keys, settings
│
├── data/                      # Data storage
│   ├── signals/              # Extracted signals (CSV)
│   ├── backtest_results/     # Backtest outputs
│   ├── cache/                # Binance price data cache
│   └── signals.db            # SQLite database
│
├── docs/                      # Documentation
│   ├── installation.md       # Detailed install guide
│   ├── usage.md             # Usage examples
│   └── discord-token-guide.md # How to get Discord token
│
├── FINAL_TRADING_STRATEGIES.md # Complete strategy guide
├── CHANGELOG.md               # Project history
└── README.md                  # This file
```

---

## 🔬 How It Works

### Signal Parsing

The parser identifies LONG vs SHORT by comparing entry price to target:

```python
# If entry > target1 → SHORT position
if entry_price > target1:
    position_type = "SHORT"
    stop_loss = "SL Close Above: xxx"
    
# If entry < target1 → LONG position
else:
    position_type = "LONG"
    stop_loss = "SL Close Below: xxx"
```

### Backtesting Logic

For each signal:
1. Fetch 1-minute Binance OHLCV data for 72 hours after signal
2. **LONG:** Track if price reaches Target 1-3 (upward) or Stop Loss (downward)
3. **SHORT:** Track if price reaches Target 1-3 (downward) or Stop Loss (upward)
4. Record which level hit first, timing, max profit, and max drawdown

### Optimization Analysis

1. Group signals by day, hour, coin, month
2. Calculate win rates for each group
3. Identify high-performance combinations (>60% WR)
4. Apply progressive filters to maximize win rate
5. Generate actionable trading rules

---

## 📊 Performance Metrics

### Baseline (No Filtering)
- **LONG:** 50.6% WR (391/773 wins)
- **SHORT:** 46.8% WR (101/216 wins)
- **Combined:** 49.7% WR (492/989 wins)

### Optimized (Ultra-Filtered)
- **LONG:** 82.1% WR (32/39 signals) → **+31.5% improvement**
- **SHORT:** 84.6% WR (22/26 signals) → **+37.8% improvement**
- **Combined:** 83.1% WR (54/65 signals) → **+33.4% improvement**

### Expected Monthly Performance (Conservative)
- **Signals:** 5-7 trades per month
- **Win Rate:** 83%+
- **Monthly Return:** 7-10%
- **Annual Return:** 84-120%
- **Sharpe Ratio:** ~2.5-3.0

---

## 🛠️ Key Features

### ✅ Accurate Position Detection
- Fixed parser bug that misclassified 21.2% of signals
- Correctly identifies LONG/SHORT based on entry vs target comparison
- Proper stop loss direction for each position type

### ✅ Intelligent Caching
- Local cache of Binance price data
- Avoids redundant API calls
- Dramatically speeds up analysis

### ✅ Comprehensive Analysis
- Performance by day of week
- Performance by hour (UTC)
- Performance by coin/symbol
- Performance by month
- Perfect combinations (100% WR patterns)

### ✅ Progressive Filtering
- Multiple strategy levels (Conservative, Moderate, Aggressive)
- Trade quality over quantity
- Clear inclusion/exclusion criteria

---

## 📚 Documentation

- **Installation:** `docs/installation.md` - Detailed setup instructions
- **Usage:** `docs/usage.md` - Examples and workflows
- **Discord Token:** `docs/discord-token-guide.md` - How to get your token
- **Trading Strategies:** `FINAL_TRADING_STRATEGIES.md` - Complete guide
- **Changelog:** `CHANGELOG.md` - Version history and updates

---

## ⚠️ Important Notes

### The Thursday Curse 🚨
- **LONG Thursday:** 33.3% WR (worst day)
- **SHORT Thursday:** 22.2% WR (worst day)
- **Recommendation:** Skip ALL Thursday signals, no exceptions

### Sample Sizes
- Coins with 100% WR often have only 3 signals
- Prioritize coins with 5+ signals and >65% WR
- Use tiered approach for reliability

### Risk Management
- Maximum 2% risk per trade
- Always use stop losses
- Maximum 3 simultaneous positions
- Maximum 15% monthly drawdown limit

---

## 🐛 Troubleshooting

### Discord Token Issues
- Token expired: Re-extract from browser (see `docs/discord-token-guide.md`)
- Invalid token: Ensure no extra spaces/quotes
- Forbidden error: Check channel access permissions

### Binance API Issues
- Rate limit: Built-in retry logic handles this automatically
- No data returned: Check symbol format (e.g., BTCUSDT not BTC-USDT)
- Timezone errors: All timestamps are UTC

### Installation Issues
- Python version: Requires 3.10+
- Dependencies: Run `pip install -r requirements.txt` manually
- venv issues: Delete `venv/` folder and re-run `setup.py`

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional signal formats (other Discord groups, Telegram)
- More exchange integrations (Bybit, OKX, etc.)
- Advanced analytics (machine learning, pattern recognition)
- Real-time monitoring and alerts
- Automated trading execution

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Meta Signals** - For providing high-quality trading signals
- **Binance** - For reliable historical market data API
- **Discord** - For accessible message extraction

---

## 📞 Support

For questions, issues, or suggestions:
1. Check `docs/` folder for detailed guides
2. Review `FINAL_TRADING_STRATEGIES.md` for strategy questions
3. Check existing issues on GitHub
4. Open a new issue with detailed description

---

## ⚡ Quick Commands Cheat Sheet

```bash
# Setup
python setup.py                          # Initial setup wizard

# Extract signals
python extract_signals.py                # Extract from Discord
python bulk_extract.py                   # Batch extraction

# Backtest
python full_backtest.py                  # Interactive backtest
python full_backtest.py <csv_file>       # Backtest specific file

# Optimize
python corrected_optimization.py         # Analyze LONG signals
python short_optimization.py             # Analyze SHORT signals

# Utilities
python quick_extract.py                  # Quick signal extraction
python test_parser.py                    # Test parser on samples
```

---

**Version:** 2.0  
**Last Updated:** October 13, 2025  
**Status:** Production Ready ✅
