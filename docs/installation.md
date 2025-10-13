# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Git
- Access to Meta Signals Discord server

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd BackTestingSignals
```

### 2. Create Virtual Environment

Creating a virtual environment is **highly recommended** to avoid conflicts with other Python projects.

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Upgrade pip and Install Dependencies

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 4. Install Additional Dependencies (Optional)

For image processing (Algo version extraction):

**Windows:**
1. Download Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the .exe file
3. Add Tesseract to your system PATH

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

### 5. Run Setup Script

```bash
python setup.py
```

This will:
- Check your environment
- Create necessary directories
- Create configuration file
- Verify dependencies
- Provide Discord setup instructions

### 6. Configure Discord Access

#### Option A: User Token (Easier, but against Discord ToS for automation)

1. Open Discord in your web browser
2. Press F12 to open Developer Tools
3. Go to Network tab
4. Refresh the page or send a message
5. Look for any request and check Headers
6. Find 'authorization' header and copy the token
7. Add this token to `config/config.json`

#### Option B: Bot Token (Official method)

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to Bot section and create a bot
4. Copy the bot token
5. Invite bot to Meta Signals server with permissions:
   - Read Message History
   - View Channel
6. Add bot token to `config/config.json`

### 7. Join Meta Signals Discord

Make sure you have access to the Meta Signals Discord server and can see the "Free Alerts" channel.

### 8. Extract Signals

```bash
python extract_signals.py
```

## Troubleshooting

### Virtual Environment Issues

**Problem:** "venv not activating"
```bash
# Windows alternative
venv\Scripts\activate.bat

# Check if activated
where python
```

**Problem:** "pip not found"
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Discord Issues

**Problem:** "Bot doesn't have permission"
- Ensure bot has "Read Message History" permission
- Check bot is in the correct server
- Verify channel name is correct

**Problem:** "Invalid token"
- Regenerate token from Discord Developer Portal
- Ensure no extra spaces in config.json
- For user tokens, make sure you copied the full token

### Dependencies Issues

**Problem:** "Module not found"
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Problem:** "Tesseract not found"
- Install Tesseract OCR (see step 4)
- Add to system PATH
- Restart terminal/IDE

## Verification

After installation, verify everything works:

```bash
# Check virtual environment
python -c "import sys; print(sys.prefix)"

# Check key dependencies
python -c "import discord; print('Discord.py:', discord.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"

# Run setup check
python setup.py
```

## Project Structure After Installation

```
BackTestingSignals/
├── venv/                  # Virtual environment (don't commit)
├── config/
│   ├── config.template.json
│   └── config.json        # Your configuration (don't commit)
├── data/
│   ├── signals/          # Extracted signals database
│   ├── images/           # Downloaded images
│   └── results/          # Export files
├── src/                  # Source code
├── requirements.txt      # Dependencies
├── setup.py             # Setup script
├── extract_signals.py   # Main extraction script
└── README.md
```

## Next Steps

1. Run `python extract_signals.py` to start extracting signals
2. Check `data/signals/signals.db` for the SQLite database
3. View exported CSV/JSON files in `data/signals/`
4. Analyze signals using the backtesting engine