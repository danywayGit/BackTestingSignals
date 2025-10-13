# BackTesting Signals

A comprehensive Python framework for extracting, backtesting, and analyzing cryptocurrency trading signals from Discord and Telegram groups using real Binance historical market data.

## Overview

This project provides an end-to-end solution for validating trading signal performance. It extracts signals from Discord channels (like Meta Signals), fetches corresponding historical OHLCV data from Binance, performs accurate backtesting with target/stop-loss validation, and generates detailed performance analytics to help traders make data-driven decisions.

**Successfully tested with 989 signals from Meta Signals Discord "Free Alerts" channel.**

## Features

### 🎯 Signal Extraction
- **Discord Integration**: Extract historical signals from Discord channels using authenticated user token
- **Meta Signals Parser**: Specialized parser for Meta Signals format with regex pattern matching
- **Bulk Extraction**: Efficient batch processing of thousands of historical messages
- **Data Storage**: SQLite database with CSV/JSON export capabilities

### 📊 Market Data Integration
- **Binance Historical Data**: Fetch 1-minute OHLCV data with precise timestamp alignment
- **Intelligent Caching**: Local cache system to minimize API calls and speed up analysis
- **Timezone Handling**: Proper UTC timezone management for accurate signal timing
- **Rate Limiting**: Built-in rate limit handling for Binance API

### 🔬 Backtesting Engine
- **Accurate Position Tracking**: Simulates real trading with entry price, targets (1-3), and stop loss
- **Target Hit Detection**: Validates which targets were hit and at what time
- **Stop Loss Analysis**: Tracks stop loss hits before target achievement
- **Performance Metrics**: Win rate, profit factor, average time to target, max drawdown

### 📈 Advanced Analytics
- **Symbol Performance**: Win rates and profit analysis by trading pair
- **Timing Patterns**: Optimal trading hours and timeframe analysis
- **Market Conditions**: Performance correlation with market volatility
- **Methodology Investigation**: Reverse engineer signal generation algorithms

## Project Structure

```
BackTestingSignals/
├── src/                              # Source code
│   ├── parsers/                      # Signal parsing modules
│   │   ├── discord_parser.py        # Meta Signals format parser
│   │   └── __init__.py
│   ├── backtesting/                  # Backtesting engine
│   │   └── signal_backtester.py     # Core backtesting logic
│   ├── data/                         # Data management
│   │   ├── binance_data.py          # Binance API integration
│   │   ├── discord_client.py        # Discord message extraction
│   │   ├── storage.py               # SQLite database & exports
│   │   └── hybrid_extractor.py      # Combined extraction strategies
│   └── analytics/                    # Performance analysis
│       └── image_processor.py       # Signal image processing
├── data/                             # Data storage
│   ├── signals/                      # Collected signals (CSV/JSON)
│   ├── cache/                        # Binance data cache
│   └── results/                      # Backtest results
├── config/                           # Configuration files
│   └── config.template.json         # Template for Discord credentials
├── docs/                             # Documentation
│   ├── installation.md              # Detailed setup guide
│   └── discord-token-guide.md       # How to get Discord token
├── tests/                            # Unit tests
│   ├── test_parser.py               # Parser validation tests
│   └── test_backtest.py             # Backtesting logic tests
├── quick_extract.py                  # 🚀 Fast signal extraction script
├── full_backtest.py                  # 🎯 Comprehensive backtesting
├── advanced_analysis.py              # 📊 Performance analytics
├── methodology_investigation.py      # 🔬 Algorithm analysis
├── extract_signals.py                # Original extraction script
├── setup.py                          # Environment setup
├── setup.ps1 / setup.sh             # Automated setup scripts
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Discord account with access to signal channels
- Binance account (for API access, no trading required)

### Quick Setup (Recommended)

**Windows:**
```powershell
# Run the automated setup script
.\setup.ps1
```

**macOS/Linux:**
```bash
# Make script executable and run
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Create and activate a virtual environment
2. Install all required dependencies
3. Create necessary directories
4. Generate configuration templates

### Manual Setup

For detailed installation instructions, see [Installation Guide](docs/installation.md).

1. **Clone this repository**
   ```bash
   git clone <repository-url>
   cd BackTestingSignals
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Discord credentials:**
   - Copy `config/config.template.json` to `config/config.json`
   - Add your Discord token (see [Discord Token Guide](docs/discord-token-guide.md))
   ```json
   {
     "discord_token": "YOUR_DISCORD_TOKEN_HERE",
     "guild_id": "1234567890",
     "channel_id": "0987654321"
   }
   ```

## Usage Guide

### 1. Extract Signals from Discord 🚀

Extract all historical signals from a Discord channel (e.g., Meta Signals "Free Alerts"):

```bash
python quick_extract.py
```

**What it does:**
- Connects to Discord using your user token
- Fetches all messages from specified channel
- Parses Meta Signals format (Entry, Targets 1-3, Stop Loss)
- Saves to SQLite database and exports to CSV/JSON
- Shows extraction statistics

**Output:**
- `data/signals/meta_signals_YYYYMMDD_HHMMSS.db` (SQLite database)
- `data/signals/meta_signals_YYYYMMDD_HHMMSS.csv` (CSV export)
- `data/signals/meta_signals_YYYYMMDD_HHMMSS.json` (JSON export)

**Example output:**
```
📊 Extraction Complete!
✅ Successfully parsed: 989/1000 signals (98.9%)
❌ Failed to parse: 11 signals
⏱️  Time taken: 45.3 seconds
```

### 2. Run Comprehensive Backtesting 🎯

Backtest all extracted signals against Binance historical data:

```bash
python full_backtest.py
```

**What it does:**
- Loads signals from database
- Fetches 1-minute OHLCV data from Binance (with caching)
- Simulates trading: tracks entry, targets hit, stop loss
- Calculates performance metrics
- Generates detailed reports

**Features:**
- **Batch Processing**: Processes 50 signals at a time with progress updates
- **Intelligent Caching**: Saves Binance data locally to speed up re-runs
- **Intermediate Results**: Saves progress every 50 signals
- **Comprehensive Metrics**: Win rate, profit factor, avg time to target, max drawdown

**Output:**
- `data/results/backtest_results_YYYYMMDD_HHMMSS.csv` (detailed results)
- `data/results/backtest_summary_YYYYMMDD_HHMMSS.json` (performance summary)
- Cached market data in `data/cache/` directory

**Example output:**
```
⏳ Progress: 200/989 (20.2%)
📦 Batch 4 (50 signals): Win Rate: 44.5% | Wins: 22 | Losses: 28
💾 Saved intermediate results: intermediate_results_200.csv

Final Results:
✅ Overall Win Rate: 47.8%
📈 Profit Factor: 1.34
⏱️  Average Time to Target: 4.8 hours
📊 Total Signals Tested: 989
```

### 3. Advanced Performance Analysis 📊

Analyze backtesting results to identify patterns and optimize strategy:

```bash
python advanced_analysis.py
```

**What it does:**
- Analyzes backtest results by symbol, timeframe, and market conditions
- Identifies best performing trading pairs
- Discovers optimal trading hours
- Calculates profit distribution and correlation patterns

**Analysis includes:**
- **Symbol Performance**: Win rates by cryptocurrency (AAVE, BNB, ETH, etc.)
- **Timing Analysis**: Best hours for signal accuracy
- **Market Conditions**: Performance during different volatility periods
- **Profit Distribution**: Risk/reward analysis
- **Target Hit Rates**: Which targets (1, 2, or 3) are most reliable

**Example insights:**
```
🏆 Best Performing Symbols:
   AAVE: 83.3% win rate (5/6 signals)
   BNB: 80.0% win rate (4/5 signals)
   DOGE: 66.7% win rate (8/12 signals)

⏰ Optimal Trading Hours:
   05:00 UTC: 100% win rate
   15:00 UTC: 85.7% win rate
   22:00 UTC: 71.4% win rate

📈 Target Performance:
   Target 1 hit: 78.5% of winning trades
   Average time to Target 1: 3.2 hours
   Target 2 hit: 45.2% of winning trades
```

### 4. Methodology Investigation 🔬

Reverse engineer the signal generation methodology:

```bash
python methodology_investigation.py
```

**What it does:**
- Analyzes entry conditions and price patterns
- Calculates risk/reward ratios for each target level
- Identifies systematic patterns in signal generation
- Discovers algorithmic rules used by signal providers

**Discovers:**
- Average R/R ratios (e.g., Target 1: 1.37x, Target 2: 3.22x, Target 3: 6.31x)
- Target progression patterns (T2/T1 ratio: ~2.47x)
- Most common risk/reward structures
- Entry timing patterns and technical conditions

**Example findings:**
```
🎯 Meta Signals Algorithm Analysis:
   Average R/R Target 1: 1.37
   Average R/R Target 2: 3.22
   Average R/R Target 3: 6.31
   
   Systematic Pattern: T2 ≈ 2.5 × T1
   Most Common R/R: 1.0 for Target 1 (40% of signals)
   
   Entry Strategy: Breakout confirmation with volume
```

## Complete Workflow Example

Here's a complete end-to-end workflow for analyzing Meta Signals:

```bash
# 1. Setup environment (first time only)
.\setup.ps1

# 2. Configure Discord credentials
# Edit config/config.json with your Discord token

# 3. Extract all historical signals from Discord
python quick_extract.py
# Output: 989 signals extracted successfully

# 4. Run comprehensive backtest on all signals
python full_backtest.py
# Output: Detailed performance metrics for 989 signals

# 5. Analyze performance patterns
python advanced_analysis.py
# Output: Best symbols, optimal hours, profit distributions

# 6. Investigate signal methodology
python methodology_investigation.py
# Output: Algorithm patterns and R/R structure

# 7. Review results
# Check data/results/ for CSV and JSON files
# Analyze findings to optimize trading strategy
```

## Key Performance Metrics Explained

### Win Rate
Percentage of signals that hit Target 1 before Stop Loss
- **Good**: > 50%
- **Excellent**: > 60%

### Profit Factor
Total profit divided by total loss (R:R adjusted)
- **Breakeven**: 1.0
- **Profitable**: > 1.2
- **Excellent**: > 2.0

### Average Time to Target
How long it takes for winning signals to hit targets
- Helps with position management
- Identifies optimal holding periods

### Stop Loss Analysis
- **Hit Before Target 1**: Signals that stopped out
- **Time to Stop Loss**: How quickly losses occur
- Helps optimize stop loss placement

### Target Hit Rates
- **Target 1**: Most conservative, highest hit rate
- **Target 2**: Medium risk/reward
- **Target 3**: Most aggressive, lower hit rate

## Configuration

### Discord Setup

1. Get your Discord user token ([Guide](docs/discord-token-guide.md))
2. Find the Guild ID (Server ID) and Channel ID
3. Update `config/config.json`:

```json
{
  "discord_token": "YOUR_DISCORD_TOKEN_HERE",
  "guild_id": "1234567890123456789",
  "channel_id": "9876543210987654321"
}
```

### Binance API (Optional)

While the system uses public Binance data that doesn't require API keys, you can optionally configure API credentials for enhanced rate limits:

```json
{
  "binance_api_key": "your_api_key",
  "binance_api_secret": "your_api_secret"
}
```

## Troubleshooting

### Common Issues

**Discord extraction fails:**
- Verify Discord token is valid
- Check Guild ID and Channel ID are correct
- Ensure account has access to the channel

**Binance data errors:**
- Check internet connection
- Verify symbol format (e.g., BTCUSDT not BTC-USDT)
- Rate limiting: Script includes automatic retry logic

**Parsing failures:**
- Some message formats may not match Meta Signals pattern
- Check `signal_extraction.log` for details
- Adjust regex patterns in `src/parsers/discord_parser.py` if needed

## Data Sources

- **Discord**: Meta Signals "Free Alerts" channel (tested with 989+ signals)
- **Binance**: Historical 1-minute OHLCV data via public API
- Extensible for other Discord servers and Telegram channels

## Performance Results

Real results from 989 Meta Signals backtest:

- **Overall Win Rate**: ~45-50% (varies by time period)
- **Best Performing Symbols**: AAVE (83.3%), BNB (80%), DOGE (66.7%)
- **Average Time to Target**: 4-6 hours
- **Optimal Hours**: 05:00 UTC, 15:00 UTC (highest win rates)
- **Target 1 Hit Rate**: ~78% of winning trades
- **Profit Factor**: 1.2-1.4 (profitable strategy)

## Technologies Used

- **Python 3.10+**: Core language
- **discord.py 2.6.4**: Discord API integration
- **python-binance 1.0.29**: Binance market data
- **pandas 2.3.3**: Data analysis and manipulation
- **numpy 2.2.6**: Numerical computations
- **SQLite**: Local database for signal storage

## Project Roadmap

- [x] Discord signal extraction
- [x] Meta Signals parser
- [x] Binance data integration
- [x] Backtesting engine with target/stop loss validation
- [x] Advanced analytics and performance metrics
- [x] Methodology investigation tools
- [ ] Telegram integration
- [ ] Real-time signal monitoring
- [ ] Automated trading integration
- [ ] Web dashboard for results visualization
- [ ] Machine learning for signal filtering

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is for educational purposes only. Trading cryptocurrencies carries risk. Always do your own research and never invest more than you can afford to lose.

## Disclaimer

This software is provided for educational and research purposes only. The developers are not responsible for any financial losses incurred from using this software. Past performance does not guarantee future results.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review test files for usage examples

---

**Built for traders who believe in data-driven decisions. 📊🚀**