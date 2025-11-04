# Telegram Signal Extraction Setup Guide

Complete guide to setting up Telegram signal extraction from trading signal channels.

---

## 📋 Prerequisites

- Python 3.8+ installed
- Active Telegram account
- Phone number registered with Telegram
- Access to the Telegram channel you want to extract from

---

## 🔧 Step 1: Install Telethon Library

Install the required Telegram client library:

```powershell
pip install telethon
```

Or add to your `requirements.txt`:
```
telethon>=1.35.0
```

---

## 🔑 Step 2: Get Telegram API Credentials

### 2.1 Visit Telegram API Portal

1. Open browser and go to: **https://my.telegram.org**
2. Enter your phone number (with country code, e.g., `+1234567890`)
3. Click **Next**
4. Enter the confirmation code sent to your Telegram app

### 2.2 Create Application

1. Click **API development tools**
2. Fill in the form:
   - **App title**: `BacktestingSignals` (or any name)
   - **Short name**: `backtesting` (or any short name)
   - **Platform**: Select appropriate platform
   - **Description**: Optional
3. Click **Create application**

### 2.3 Save Credentials

You'll receive:
- **api_id**: 8-digit number (e.g., `12345678`)
- **api_hash**: 32-character string (e.g., `1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`)

⚠️ **KEEP THESE SECURE!** Don't share or commit to Git.

---

## 📝 Step 3: Configure Extraction Script

### 3.1 Edit `extract_telegram.py`

Find the CONFIG section:

```python
CONFIG = {
    'api_id': 12345678,  # Replace with your API ID
    'api_hash': 'your_api_hash_here',  # Replace with your API hash
    'phone': '+1234567890',  # Replace with your phone number
    'channel': 'channel_username',  # Replace with channel username
    'days_back': 30,  # How many days to look back
    'limit': 5000  # Maximum messages to retrieve
}
```

### 3.2 Example Configuration

```python
CONFIG = {
    'api_id': 87654321,
    'api_hash': 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
    'phone': '+15551234567',
    'channel': 'metasignalsbot',  # Without @ symbol
    'days_back': 30,
    'limit': 5000
}
```

---

## 🚀 Step 4: Run Extraction

### 4.1 First Run (Authentication)

```powershell
python extract_telegram.py
```

On first run, you'll be prompted:
1. **Enter the code**: Check your Telegram app for login code
2. **Enter 2FA password** (if enabled): Enter your Two-Factor Authentication password

The script will save session to avoid re-authentication.

### 4.2 Subsequent Runs

After first authentication, the script runs without prompts:

```powershell
python extract_telegram.py
```

---

## 📊 Output Files

The script creates:

1. **CSV File**: `telegram_signals_YYYYMMDD_HHMMSS.csv`
   - Structured data for analysis
   - Compatible with backtesting scripts

2. **JSON File**: `telegram_signals_YYYYMMDD_HHMMSS.json`
   - Full signal details
   - Preserves all metadata

3. **Session File**: `telegram_session.session`
   - Stores authentication
   - Prevents re-login each time
   - ⚠️ Keep secure, contains auth tokens

---

## 🔍 Finding Channel Username

### Method 1: From Telegram App
1. Open channel in Telegram
2. Tap channel name at top
3. Look for username (starts with `@`)
4. Use without `@` symbol in config

### Method 2: From Channel Link
- Link format: `https://t.me/channel_username`
- Use `channel_username` in config

### Method 3: Private Channels
For private channels:
```python
# Instead of username, use channel ID
channel = -1001234567890  # Numeric ID
```

Find channel ID:
1. Forward a message from channel to @userinfobot
2. Bot will show channel ID

---

## 🛠️ Advanced Usage

### Custom Date Range

```python
from datetime import datetime, timedelta, timezone

# Last 7 days
start_date = datetime.now(timezone.utc) - timedelta(days=7)

signals = await extractor.extract_signals(
    channel_identifier='channel_username',
    start_date=start_date,
    limit=1000
)
```

### Specific Date Range

```python
# Between specific dates
start_date = datetime(2024, 11, 1, tzinfo=timezone.utc)
end_date = datetime(2024, 11, 30, tzinfo=timezone.utc)

signals = await extractor.extract_signals(
    channel_identifier='channel_username',
    start_date=start_date,
    end_date=end_date,
    limit=10000
)
```

### Multiple Channels

```python
channels = ['channel1', 'channel2', 'channel3']

all_signals = []
for channel in channels:
    signals = await extractor.extract_signals(
        channel_identifier=channel,
        limit=5000
    )
    all_signals.extend(signals)

print(f"Total signals from all channels: {len(all_signals)}")
```

---

## 🐛 Troubleshooting

### Issue: "Invalid phone number"
**Solution**: Include country code with `+` sign
```python
phone = '+15551234567'  # Correct
phone = '5551234567'    # Wrong
```

### Issue: "Could not find the input entity"
**Solution**: 
- Verify channel username is correct
- Make sure you're a member of the channel
- For private channels, use numeric ID

### Issue: "Import telethon could not be resolved"
**Solution**: Install telethon library
```powershell
pip install telethon
```

### Issue: "SessionPasswordNeededError"
**Solution**: Enter your 2FA password when prompted
- Set up in Telegram: Settings → Privacy → Two-Step Verification

### Issue: "FloodWaitError: A wait of X seconds is required"
**Solution**: Telegram rate limit - wait and retry
- Reduce `limit` parameter
- Add delays between requests

### Issue: "Session file errors"
**Solution**: Delete session file and re-authenticate
```powershell
del telegram_session.session
python extract_telegram.py
```

---

## 🔒 Security Best Practices

### 1. Protect Credentials
```python
# ❌ Don't commit credentials to Git
CONFIG = {
    'api_id': 12345678,  # Hardcoded - BAD
    'api_hash': 'abc123'
}

# ✅ Use environment variables
import os
CONFIG = {
    'api_id': int(os.getenv('TELEGRAM_API_ID')),
    'api_hash': os.getenv('TELEGRAM_API_HASH')
}
```

### 2. Add to .gitignore
```
# Telegram credentials
telegram_session.session
telegram_*.session
.env
```

### 3. Use Environment Variables

Create `.env` file:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
TELEGRAM_CHANNEL=channel_username
```

Load in script:
```python
from dotenv import load_dotenv
import os

load_dotenv()

CONFIG = {
    'api_id': int(os.getenv('TELEGRAM_API_ID')),
    'api_hash': os.getenv('TELEGRAM_API_HASH'),
    'phone': os.getenv('TELEGRAM_PHONE'),
    'channel': os.getenv('TELEGRAM_CHANNEL'),
}
```

Install python-dotenv:
```powershell
pip install python-dotenv
```

---

## 📚 Additional Resources

### Telethon Documentation
- Official docs: https://docs.telethon.dev/
- API reference: https://tl.telethon.dev/

### Telegram API
- API portal: https://my.telegram.org
- Bot API docs: https://core.telegram.org/api

### Rate Limits
- Message retrieval: ~20-30 requests/second
- Account limits: Telegram enforced (varies)
- Best practice: Add delays for large extractions

---

## 🎯 Quick Start Checklist

- [ ] Install telethon: `pip install telethon`
- [ ] Get API credentials from https://my.telegram.org
- [ ] Find channel username or ID
- [ ] Edit `extract_telegram.py` CONFIG section
- [ ] Run first time: `python extract_telegram.py`
- [ ] Enter authentication code from Telegram app
- [ ] Verify CSV/JSON output files created
- [ ] Add session file to .gitignore

---

## 💡 Tips

1. **Start small**: Test with `days_back=7` and `limit=100` first
2. **Join channel first**: Must be member to extract messages
3. **Check output**: Verify CSV format matches expected structure
4. **Session persistence**: Keeps authentication for 1 year
5. **Multiple accounts**: Use different session names for each account
6. **Parser compatibility**: Uses same parser as Discord extraction

---

## 🆘 Support

If you encounter issues:
1. Check troubleshooting section above
2. Verify Telegram credentials are correct
3. Ensure you're a channel member
4. Check Telegram app for any security alerts
5. Try deleting session file and re-authenticating

---

## 📝 Notes

- Session file contains auth tokens - keep secure
- First run requires interactive authentication
- Telegram may show "New login" notification - this is normal
- Rate limits apply - be respectful with API usage
- Some channels may restrict message history access
- Public channels are easier to access than private ones

---

*Last updated: November 2025*
