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
- Ask for Discord token and channel ID
- Generate `config/config.json`

---

## Step 2: Get Discord Token (1 minute)

1. Open Discord in **Chrome/Firefox** browser
2. Press **F12** (open Developer Tools)
3. Go to **Console** tab
4. Paste this code and press Enter:

```javascript
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```

5. Copy the token (it's a long string starting with `MT` or `NZ`)
6. Paste into `config/config.json` under `"discord_token"`

> **Full guide:** `docs/discord-token-guide.md`

---

## Step 3: Extract Signals (1 minute)

```bash
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source venv/bin/activate  # Linux/Mac

# Extract signals
python extract_signals.py
```

Enter your Discord channel ID when prompted. Signals saved to `data/signals/`.

---

## Step 4: Run Backtest (1 minute)

```bash
python full_backtest.py
```

Select the CSV file you just extracted. Backtest results saved to `data/backtest_results/`.

---

## Step 5: Analyze & Optimize (<1 minute)

```bash
# Analyze LONG signals
python corrected_optimization.py

# Analyze SHORT signals
python short_optimization.py
```

Results show:
- Best days/hours/coins
- Win rates by category
- Optimized strategies

---

## 🎯 What's Next?

### Read the Strategies
Open `FINAL_TRADING_STRATEGIES.md` to see:
- Complete LONG/SHORT trading rules
- Entry/exit criteria
- Risk management
- Expected performance

### Key Insights

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

**Discord token doesn't work:**
- Re-extract (tokens expire)
- Remove quotes/spaces
- Make sure you have channel access

**No signals extracted:**
- Check channel ID is correct
- Verify token is valid
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
- **Trading Strategies:** `FINAL_TRADING_STRATEGIES.md`

---

**Need Help?** Open an issue on GitHub with your error message and steps to reproduce.

**Version:** 2.0 | **Last Updated:** October 13, 2025
