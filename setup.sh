#!/bin/bash

echo "🚀 Meta Signals Extraction - Quick Setup"
echo "====================================="

echo ""
echo "📋 Step 1: Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    echo "Please ensure Python 3 is installed"
    exit 1
fi

echo "✅ Virtual environment created"

echo ""
echo "📋 Step 2: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📋 Step 3: Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "📋 Step 4: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "Please check requirements.txt and internet connection"
    exit 1
fi

echo ""
echo "📋 Step 5: Running setup script..."
python setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/config.json and add your Discord token"
echo "2. Run: python extract_signals.py"
echo ""