# Script Reference Guide

Quick reference for all scripts in the BackTesting Signals project (v2.1.0 - Updated Nov 4, 2025).

## 📋 Table of Contents

1. [Signal Extraction Scripts](#signal-extraction-scripts)
2. [Backtesting Scripts](#backtesting-scripts)
3. [Analysis Scripts](#analysis-scripts)
4. [Utility Scripts](#utility-scripts)
5. [Test Scripts](#test-scripts)
6. [Archived Scripts](#archived-scripts)

---

## Signal Extraction Scripts

### extract_telegram.py 📱 (PRODUCTION)

**Purpose**: Production-ready Telegram signal extraction (DaviddTech format)

**Usage**:
```bash
python extract_telegram.py
```

**What it does**:
- Connects to Telegram using Telethon library
- Fetches messages from DaviddTech channel (@DaviddTech)
- Parses DaviddTech signal format (LONG/SHORT, Entry, Targets, Stop Loss)
- Supports historical extraction (up to 365 days back)
- Saves to CSV and JSON

**Configuration**: Uses `config/config.json`:
```json
{
  "telegram": {
    "api_id": "YOUR_API_ID",
    "api_hash": "YOUR_API_HASH",
    "phone_number": "+1234567890",
    "channels": [
      {
        "name": "DaviddTech",
        "username": "DaviddTech"
      }
    ]
  }
}
```

**Output files**:
- `data/signals/telegram_signals_export_YYYYMMDD_HHMMSS.csv`
- `data/signals/telegram_signals_export_YYYYMMDD_HHMMSS.json`
- `data/cache/telegram_messages_sample.json` (debug sample)
- `data/cache/signal_extractor.session` (Telegram session)

**Performance**: Extracted 805 signals (365 days) successfully

**Success rate**: High accuracy with DaviddTech format

**Setup guide**: `docs/setup/telegram_setup.md`

---

### Discord Extraction (ARCHIVED)

Discord extraction scripts have been archived to `archive/extraction_methods/`:
- `extract_signals.py` - Complex OCR-based extractor
- `extract_all_signals.py` - Simple web API method
- `quick_extract.py` - Direct token extraction
- `bulk_extract.py` - Hybrid batch extractor

**When to use**: Reference implementations available in archive for Discord signal extraction.

---

## Backtesting Scripts

### full_backtest.py 🎯 (MAIN BACKTESTING)

**Purpose**: Comprehensive backtesting of all signals against Binance data

**Usage**:
```bash
# Interactive (prompts for file selection)
python full_backtest.py

# Specific file
python full_backtest.py data/signals/telegram_signals_export_20251104_043620.csv
```

**What it does**:
1. Load signals from CSV
2. Fetch 1-minute OHLCV data from Binance (72 hours after signal)
3. Simulate trading positions (LONG/SHORT)
4. Track target hits (1, 2, 3) and stop loss
5. Calculate performance metrics
6. Save detailed results

**Features**:
- Batch processing: Efficient signal processing
- Progress tracking: Real-time progress updates
- Intelligent caching: Saves Binance data to `data/cache/`
- Error recovery: Can handle failed requests
- LONG/SHORT support: Proper direction tracking

**Output files**:
- `data/backtest_results/meta_signals_backtest_detailed_YYYYMMDD_HHMMSS.csv`
- `data/backtest_results/meta_signals_backtest_metrics_YYYYMMDD_HHMMSS.json`

**Performance**: 
- DaviddTech 805 signals: 25 minutes 29 seconds
- Uses cached data on subsequent runs

**Metrics calculated**:
- Win rate (overall, LONG, SHORT)
- Profit factor
- Average profit/loss
- Best/worst trades
- Time to target statistics
- Target hit distribution

**Results**: DaviddTech analysis showed 48.2% WR (388/805 wins)

---

## Analysis Scripts

All analysis scripts now use the shared `BacktestAnalyzer` class from `src/analytics/backtest_analyzer.py`.

### analyze_davidtech.py 📊 (COMPREHENSIVE ANALYSIS)

**Purpose**: All-in-one optimization analysis using latest backtest results

**Usage**:
```bash
python analyze_davidtech.py
```

**What it does**:
1. Automatically loads latest backtest results from `data/backtest_results/`
2. Performs comprehensive optimization analysis
3. Analyzes performance by day, hour, coin, month
4. Identifies best and worst performing patterns
5. Generates detailed markdown report

**Analysis includes**:
- Overall statistics (win rate, profit factor, etc.)
- Performance by day of week
- Performance by hour (UTC)
- Performance by coin/symbol
- Performance by month
- Best combinations
- Recommendations

**Output files**:
- `docs/analysis/DAVIDTECH_FULL_ANALYSIS_YYYYMMDD.md`
- Console output with key findings

**Example results**:
```
Overall: 48.2% WR (388 wins / 361 losses)
Best Hour: 05:00 UTC (59.1% WR, PF 4.45)
Best Coin: LINKUSDT (61.8% WR)
Best Day: Thursday (53.2% WR)
```

**When to use**: After running `full_backtest.py` on DaviddTech signals

---

### long_short_optimization.py 📊

**Purpose**: Comprehensive optimization analysis for both LONG and SHORT signals

**Usage**:
```bash
python long_short_optimization.py
```

**What it does**:
- Loads latest backtest results
- Analyzes LONG signals: performance by day/hour/coin/month
- Analyzes SHORT signals: performance by day/hour/coin/month
- Identifies high-performance patterns (>60% WR) for both
- Progressive filtering strategies for each type
- Perfect combinations (100% WR patterns)

**Analysis output**:
- Overall LONG and SHORT statistics separately
- Performance by day of week (both types)
- Performance by hour UTC (both types)
- Performance by coin/symbol (both types)
- Performance by month (both types)
- Best combinations for each
- Filtered strategies with improvements

**Output files**:
- `long_short_optimization_results.json`
- Console output with separate recommendations for LONG and SHORT

**Example findings**:
```
🟢 LONG SIGNALS (773 total)
Overall: 50.6% WR (391/773)
Best Days: Wed (60%), Sat (58%), Sun (55%)
Best Hours: 01:00-03:00 UTC
Best Coins: BNB (80% WR), FET (67% WR)

🔴 SHORT SIGNALS (366 total)
Overall: 48.2% WR (176/366)
Best Days: Mon (55%), Fri (53%)
Best Hours: 18:00-20:00 UTC
Best Coins: ETH (72% WR), XRP (65% WR)
```

**When to use**: After backtesting to optimize both LONG and SHORT signal strategies

---

### short_optimization.py 🔴

**Purpose**: Analyze SHORT signal performance and find optimal patterns

**Usage**:
```bash
python short_optimization.py
```

**What it does**:
- Loads latest backtest results
- Filters for SHORT signals only
- Analyzes performance by day/hour/coin/month
- Identifies high-performance SHORT patterns
- Progressive filtering strategies
- Perfect combinations for SHORT positions

**Analysis output**:
- Overall SHORT statistics
- Performance by day of week
- Performance by hour (UTC)
- Performance by coin/symbol
- Performance by month
- Best SHORT combinations
- Filtered SHORT strategies

**Output files**:
- `data/results/short_optimization_results.json`
- Console output with recommendations

**Example findings**:
```
🔴 SHORT SIGNALS (216 total)
Overall: 46.8% WR (101/216)

Best Days: Mon, Wed, Sat, Sun
Best Hours: 04:00, 06:00, 10:00, 18:00 UTC
Best Coins: FET (73% WR), IMX (67% WR)
AVOID: Thursday (22.2% WR), Friday (29.6% WR)
```

**When to use**: After backtesting to optimize SHORT signal strategy

---

### compare_long_short.py ⚖️

**Purpose**: Compare LONG vs SHORT signal performance

**Usage**:
```bash
python compare_long_short.py
```

**What it does**:
- Loads latest backtest results
- Separates LONG and SHORT signals
- Compares performance metrics
- Identifies which position type performs better
- Analyzes differences in patterns
- Recommends position type preferences

**Analysis output**:
- Side-by-side LONG vs SHORT comparison
- Win rate comparison
- Profit factor comparison
- Average profit/loss comparison
- Time to target comparison
- Best coins for each position type
- Best times for each position type

**Output files**:
- `data/results/long_vs_short_comparison.json`
- Console output with comparison

**Example findings**:
```
LONG:  773 signals, 50.6% WR, PF 1.42
SHORT: 216 signals, 46.8% WR, PF 1.18

LONG performs better on: Wed, Sat, Sun
SHORT performs better on: Mon
Both avoid: Thursday

LONG best coins: BNB, FET, DOGE
SHORT best coins: FET, IMX, RUNE
```

**When to use**: To understand which position types work best in different scenarios

---

### compare_october_november.py �

**Purpose**: Compare performance across different time periods (October vs November)

**Usage**:
```bash
python compare_october_november.py
```

**What it does**:
- Loads latest backtest results
- Separates signals by month (October, November)
- Compares performance metrics month-over-month
- Identifies temporal patterns
- Analyzes if strategy effectiveness changes over time

**Analysis output**:
- Month-by-month performance comparison
- Win rate trends
- Profit factor trends
- Volume of signals per month
- Best performing months
- Seasonal patterns

**Output files**:
- `data/results/month_comparison_results.json`
- Console output with comparison

**When to use**: To identify temporal patterns and validate strategy consistency

---

## Utility Scripts

### fix_symbols.py 🔧

**Purpose**: Fix and normalize cryptocurrency symbol names

**Usage**:
```bash
python fix_symbols.py
```

**What it does**:
- Scans signal files for symbol inconsistencies
- Normalizes symbol format (e.g., BTC → BTCUSDT)
- Fixes common symbol errors
- Validates Binance symbol availability

**When to use**: When signals have incorrect or inconsistent symbol names

---

### check_telegram_channel.py ✅

**Purpose**: Verify Telegram API access and channel connectivity

**Usage**:
```bash
python check_telegram_channel.py
```

**What it does**:
- Tests Telegram API credentials
- Verifies channel access
- Checks authentication
- Validates session file

**When to use**: Troubleshooting Telegram extraction issues

---

### setup.py 🛠️

**Purpose**: Environment configuration and setup

**Usage**:
```bash
python setup.py
```

**What it does**:
- Creates directory structure
- Validates Python version
- Checks dependencies
- Creates config templates
- Initializes required folders

**When to use**: First-time setup

---

### setup.ps1 (Windows)

**Purpose**: Automated setup for Windows

**Usage**:
```powershell
.\setup.ps1
```

**What it does**:
1. Check Python installation
2. Create virtual environment
3. Activate venv
4. Install dependencies
5. Run setup.py
6. Create directories

---

### setup.sh (macOS/Linux)

**Purpose**: Automated setup for macOS/Linux

**Usage**:
```bash
chmod +x setup.sh
./setup.sh
```

**What it does**:
1. Check Python installation
2. Create virtual environment
3. Activate venv
4. Install dependencies
5. Run setup.py
6. Create directories

---

## Test Scripts

### test_parser.py

**Purpose**: Validate signal parsing logic

**Usage**:
```bash
python test_parser.py
```

**What it does**:
- Test Meta Signals format parsing
- Validate regex patterns
- Test edge cases
- Ensure accuracy

**Test cases**:
- LONG signals
- SHORT signals
- Multiple target formats
- Various stop loss formats
- Edge cases and malformed signals

---

## Complete Workflow

Here's how to use all scripts in sequence:

```bash
# 1. SETUP (First time only)
.\setup.ps1  # Windows
# or
./setup.sh   # macOS/Linux

# 2. CONFIGURE
# Edit config/config.json with Discord credentials

# 3. EXTRACT SIGNALS
python quick_extract.py
# Output: 989 signals extracted to data/signals/

# 4. RUN BACKTEST
python full_backtest.py
# Output: Results in data/results/
# Takes: ~30-45 minutes for 989 signals

# 5. ANALYZE PERFORMANCE
python advanced_analysis.py
# Output: Performance insights by symbol, time, etc.

# 6. INVESTIGATE METHODOLOGY
python methodology_investigation.py
# Output: Algorithm patterns and R/R structure

# 7. REVIEW RESULTS
# Check CSV files in data/results/
# Review insights from analysis scripts
```

---

## File Output Reference

### Signal Storage
- **SQLite Database**: `data/signals/meta_signals_*.db`
- **CSV Export**: `data/signals/meta_signals_*.csv`
- **JSON Export**: `data/signals/meta_signals_*.json`

### Backtest Results
- **Detailed Results**: `data/results/backtest_results_*.csv`
- **Summary**: `data/results/backtest_summary_*.json`
- **Intermediate**: `intermediate_results_*.csv`

### Cache
- **Binance Data**: `data/cache/SYMBOL_1m_YYYYMMDD_YYYYMMDD.csv`

### Logs
- **Extraction Log**: `signal_extraction.log`
- **Analysis Log**: Console output (can redirect to file)

---

## Performance Tips

### Speed Up Extraction
- Use `quick_extract.py` (fastest)
- Ensure stable internet connection
- Run during low Discord traffic times

### Speed Up Backtesting
- First run will be slower (fetches data)
- Subsequent runs use cached data (10x faster)
- Process in batches (automatic in full_backtest.py)
- Don't delete cache directory

### Memory Management
- Use `bulk_extract.py` for very large datasets
- Close other applications during processing
- Monitor with Task Manager/Activity Monitor

### Data Management
- Cache files can be large (100+ MB)
- Clean old cache files periodically
- Export to CSV for external analysis
- Backup important results

---

## Troubleshooting by Script

### quick_extract.py issues
- **"Invalid token"**: Check config.json Discord token
- **"Channel not found"**: Verify Guild ID and Channel ID
- **"Rate limited"**: Wait and retry (automatic retry included)
- **Low parsing rate**: Check signal format in inspect_messages.py

### full_backtest.py issues
- **"Symbol not found"**: Symbol may not exist on Binance
- **"Connection error"**: Check internet connection
- **Slow performance**: Check if cache is being used
- **Memory error**: Reduce batch size in code

### advanced_analysis.py issues
- **"No results file"**: Run full_backtest.py first
- **"Empty results"**: Check backtest completed successfully
- **Calculation errors**: Verify data integrity

### methodology_investigation.py issues
- **"No signals"**: Run quick_extract.py first
- **"Database error"**: Check database file exists
- **Timezone errors**: Ensure proper datetime handling

---

## Script Comparison

| Script | Purpose | Speed | Complexity | Output |
|--------|---------|-------|------------|--------|
| quick_extract.py | Signal extraction | Fast | Low | DB, CSV, JSON |
| full_backtest.py | Backtesting | Slow (first run) | Medium | CSV, JSON |
| advanced_analysis.py | Analytics | Fast | Medium | Console report |
| methodology_investigation.py | Algorithm analysis | Fast | High | Console report |
| extract_signals.py | Alt extraction | Medium | Low | DB, CSV, JSON |
| bulk_extract.py | Batch extraction | Medium | Medium | DB, CSV, JSON |
| inspect_messages.py | Debugging | Fast | Low | JSON |

---

## Best Practices

1. **Always run setup first** (setup.ps1 or setup.sh)
2. **Configure Discord credentials** before extraction
3. **Run quick_extract.py** for signal collection
4. **Run full_backtest.py** for performance validation
5. **Analyze results** with both analysis scripts
6. **Keep cache directory** for faster re-runs
7. **Backup results regularly** to avoid data loss
8. **Test with small dataset** first (10-50 signals)
9. **Monitor logs** for errors and warnings
10. **Update documentation** when modifying scripts

---

**For detailed installation instructions, see [Installation Guide](installation.md)**

**For Discord token setup, see [Discord Token Guide](discord-token-guide.md)**

**For complete project overview, see [README.md](../README.md)**
