# ⚡ Quick Start Guide

**Get up and running with BackTesting Signals in 5 minutes.**

---

## Step 1: Install (2 minutes)

```bash
# Clone and navigate
git clone https://github.com/yourusername/BackTestingSignals.git
cd BackTestingSignals

# Run setup wizard
python setup.py
```

The wizard will:
- Create virtual environment
- Install dependencies
- Ask for Telegram/Discord credentials
- Generate `config/config.json`

---

## Step 2: Get API Credentials (2 minutes)

### For Telegram (DaviddTech Channel)

1. Get Telegram API credentials from https://my.telegram.org/apps
2. Add to `config/config.json`:

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

> **Full guide:** `docs/setup/telegram_setup.md`

### For Discord (Meta Signals)

1. Open Discord in **Chrome/Firefox** browser
2. Press **F12** (open Developer Tools)
3. Go to **Console** tab
4. Paste this code and press Enter:

```javascript
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```

5. Copy the token and add to `config/config.json`

> **Full guide:** `docs/setup/discord_token.md`

---

## Step 3: Extract Signals (1 minute)

```bash
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source venv/bin/activate  # Linux/Mac

# Extract from Telegram (DaviddTech)
python extract_telegram.py

# OR extract from Discord (archived methods available in archive/extraction_methods/)
```

Signals saved to `data/signals/`.

---

## Step 4: Run Backtest (1 minute)

```bash
python full_backtest.py
```

Select the CSV file you just extracted. Backtest results saved to `data/backtest_results/`.

---

## Step 5: Analyze & Optimize (<1 minute)

```bash
# Comprehensive analysis (uses latest backtest automatically)
python analyze_davidtech.py

# OR run individual analyses:

# Analyze LONG signals
python corrected_optimization.py

# Analyze SHORT signals
python short_optimization.py

# Compare LONG vs SHORT
python compare_long_short.py

# Compare different time periods
python compare_october_november.py
```

Results saved to `data/results/` showing:
- Best days/hours/coins
- Win rates by category
- Optimized strategies

---

## 🎯 What's Next?

### Read the Strategies
Open `docs/analysis/FINAL_TRADING_STRATEGIES.md` to see:
- Complete LONG/SHORT trading rules
- Entry/exit criteria
- Risk management
- Expected performance

### Recent Analysis Results

**DaviddTech (805 signals, 365 days):**
- Overall: **48.2% WR** (1.33 PF)
- Best Hours: 05:00 UTC (59.1% WR), 03:00 UTC (57.6% WR)
- Best Coins: LINKUSDT (61.8% WR), ADAUSDT (53.9% WR)

See `docs/analysis/DAVIDTECH_FULL_ANALYSIS_20251104.md` for complete details.

**Meta Signals Optimization:**
✅ **Use these filters for 83% win rate:**

**LONG Signals:**
- Days: Wed/Sat/Sun
- Hours: 01:00-03:00 UTC
- Coins: BNB, FET, DOGE, EOS, ETH
- **Skip Thursday!**

**SHORT Signals:**
- Days: Mon/Wed/Sat/Sun
- Hours: 04:00, 06:00, 10:00, 18:00 UTC
- Coins: FET, IMX, RUNE, TRX, DOT
- **Skip Thursday & Friday!**

---

## 🐛 Troubleshooting

**Telegram issues:**
- Verify API credentials at https://my.telegram.org/apps
- Session file stored in `data/cache/signal_extractor.session`
- First run requires phone verification

**Discord token doesn't work:**
- Re-extract (tokens expire)
- Remove quotes/spaces
- Make sure you have channel access

**No signals extracted:**
- Check channel username/ID is correct
- Verify credentials are valid
- Ensure channel has messages

**Backtest fails:**
- Check signal CSV has data
- Verify Binance can access symbol (BTCUSDT format)
- Check internet connection

---

## 📚 Learn More

- **Full README:** Complete documentation and features
- **Installation Guide:** `docs/installation.md`
- **Usage Examples:** `docs/usage.md`
- **Script Reference:** `docs/SCRIPT_REFERENCE.md`
- **Setup Guides:** `docs/setup/` (Telegram, Discord, Bot)
- **Analysis Reports:** `docs/analysis/` (DaviddTech, comparisons, strategies)
- **Project Docs:** `docs/project/` (completion, git history)

---

## 📁 Key File Locations

After reorganization (v2.1.0):
- **Signals:** `data/signals/`
- **Backtest results:** `data/backtest_results/`
- **Analysis results:** `data/results/`
- **Session files:** `data/cache/`
- **Logs:** `logs/`
- **Archived scripts:** `archive/extraction_methods/`

---

**Need Help?** Open an issue on GitHub with your error message and steps to reproduce.

**Version:** 2.1 | **Last Updated:** November 4, 2025
