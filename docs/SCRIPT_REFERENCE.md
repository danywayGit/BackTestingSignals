# Script Reference Guide

Quick reference for all scripts in the BackTesting Signals project.

## 📋 Table of Contents

1. [Signal Extraction Scripts](#signal-extraction-scripts)
2. [Backtesting Scripts](#backtesting-scripts)
3. [Analysis Scripts](#analysis-scripts)
4. [Utility Scripts](#utility-scripts)
5. [Test Scripts](#test-scripts)

---

## Signal Extraction Scripts

### quick_extract.py ⚡ (RECOMMENDED)

**Purpose**: Fast extraction of all historical signals from Discord channel

**Usage**:
```bash
python quick_extract.py
```

**What it does**:
- Connects to Discord using your user token
- Fetches all messages from Meta Signals "Free Alerts" channel
- Parses signal format (Entry, Targets, Stop Loss)
- Saves to SQLite database
- Exports to CSV and JSON

**Output files**:
- `data/signals/meta_signals_YYYYMMDD_HHMMSS.db`
- `data/signals/meta_signals_YYYYMMDD_HHMMSS.csv`
- `data/signals/meta_signals_YYYYMMDD_HHMMSS.json`

**Performance**: Processes 1000 messages in ~45 seconds

**Success rate**: 98.9% parsing accuracy (989/1000 signals)

---

### extract_signals.py

**Purpose**: Alternative signal extraction method

**Usage**:
```bash
python extract_signals.py
```

**What it does**:
- Different extraction approach from quick_extract.py
- May work better for certain message formats
- Similar output format

**When to use**: If quick_extract.py has issues

---

### bulk_extract.py

**Purpose**: Batch processing for large datasets

**Usage**:
```bash
python bulk_extract.py
```

**What it does**:
- Process multiple channels simultaneously
- Memory-efficient for thousands of messages
- Batch processing with progress tracking

**When to use**: Processing multiple channels or very large datasets (10,000+ messages)

---

### inspect_messages.py

**Purpose**: Debug and analysis tool for Discord messages

**Usage**:
```bash
python inspect_messages.py
```

**What it does**:
- Fetch raw Discord messages
- Display message structure
- Test parsing logic
- Generate message analysis report

**Output**: `message_analysis.json`

**When to use**: 
- Debugging parsing issues
- Understanding message format
- Validating Discord connection

---

## Backtesting Scripts

### full_backtest.py 🎯 (MAIN BACKTESTING)

**Purpose**: Comprehensive backtesting of all signals against Binance data

**Usage**:
```bash
python full_backtest.py
```

**What it does**:
1. Load signals from database
2. Fetch 1-minute OHLCV data from Binance
3. Simulate trading positions
4. Track target hits (1, 2, 3) and stop loss
5. Calculate performance metrics
6. Save results to CSV/JSON

**Features**:
- Batch processing: 50 signals at a time
- Progress tracking: ⏳ Progress: X/989 (X.X%)
- Intelligent caching: Saves Binance data locally
- Intermediate saves: Every 50 signals
- Error recovery: Can resume from last batch

**Output files**:
- `data/results/backtest_results_YYYYMMDD_HHMMSS.csv`
- `data/results/backtest_summary_YYYYMMDD_HHMMSS.json`
- `intermediate_results_XXX_XXXXXX.csv` (every 50 signals)

**Performance**: 
- ~2-3 seconds per signal (first run)
- ~0.5-1 second per signal (cached)
- 989 signals: ~30-45 minutes first run

**Metrics calculated**:
- Win rate
- Profit factor
- Average time to target
- Target hit distribution
- Stop loss analysis
- Max drawdown

---

### test_backtest.py

**Purpose**: Unit tests for backtesting logic

**Usage**:
```bash
python test_backtest.py
```

**What it does**:
- Test position tracking
- Validate target hit detection
- Test stop loss logic
- Verify profit/loss calculations

**When to use**: 
- Validating code changes
- Ensuring calculation accuracy
- Regression testing

---

## Analysis Scripts

### advanced_analysis.py 📊

**Purpose**: Deep performance analytics on backtest results

**Usage**:
```bash
python advanced_analysis.py
```

**What it does**:
1. Load backtest results
2. Analyze performance by symbol
3. Find optimal trading hours
4. Study market conditions
5. Calculate profit distributions
6. Identify correlations

**Analysis includes**:

#### Symbol Performance
- Win rate by cryptocurrency
- Profit/loss by symbol
- Number of signals per symbol
- Best and worst performers

Example output:
```
🏆 Best Performing Symbols:
   AAVE: 83.3% win rate (5/6 signals)
   BNB: 80.0% win rate (4/5 signals)
   DOGE: 66.7% win rate (8/12 signals)
```

#### Timing Analysis
- Performance by hour of day
- Performance by day of week
- Optimal trading windows
- Time to target statistics

Example output:
```
⏰ Optimal Trading Hours:
   05:00 UTC: 100% win rate
   15:00 UTC: 85.7% win rate
   22:00 UTC: 71.4% win rate
```

#### Market Conditions
- Performance during different volatility periods
- Correlation with market trends
- Volume analysis

#### Profit Distribution
- Risk/reward analysis
- Profit ranges
- Loss ranges
- Statistical distributions

#### Target Analysis
- Which targets hit most often
- Average time to each target
- Target hit progression

**When to use**: After running full_backtest.py to understand patterns

---

### methodology_investigation.py 🔬

**Purpose**: Reverse engineer signal generation algorithm

**Usage**:
```bash
python methodology_investigation.py
```

**What it does**:
1. Analyze entry conditions
2. Calculate risk/reward ratios
3. Identify systematic patterns
4. Discover algorithmic rules
5. Study entry timing

**Discoveries**:

#### Risk/Reward Structure
- Average R/R for Target 1: 1.37x
- Average R/R for Target 2: 3.22x
- Average R/R for Target 3: 6.31x

#### Pattern Recognition
- Systematic target progression
- T2 ≈ 2.47 × T1
- T3 ≈ 4.61 × T1
- Most common R/R: 1.0 for Target 1

#### Entry Analysis
- Price patterns at entry
- Volume conditions
- Technical indicator correlations

**Output**:
```
🎯 Meta Signals Algorithm Analysis:
   Average R/R Target 1: 1.37
   Average R/R Target 2: 3.22
   Average R/R Target 3: 6.31
   
   Systematic Pattern: T2 ≈ 2.5 × T1
   Most Common R/R: 1.0 for Target 1 (40% of signals)
```

**When to use**: 
- Understanding signal methodology
- Optimizing target placement
- Developing similar strategies

---

## Utility Scripts

### setup.py

**Purpose**: Environment configuration and setup

**Usage**:
```bash
python setup.py
```

**What it does**:
- Create directory structure
- Validate Python version
- Check dependencies
- Create config templates
- Initialize database

**When to use**: First-time setup (or use setup.ps1/setup.sh)

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
