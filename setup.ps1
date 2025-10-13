# Meta Signals Extraction - PowerShell Setup Script
# Run with: .\setup.ps1

Write-Host "🚀 Meta Signals Extraction - Quick Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Python is available
Write-Host ""
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment already exists
if (Test-Path "venv") {
    Write-Host ""
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to recreate it? (y/N)"
    if ($overwrite -eq "y" -or $overwrite -eq "Y") {
        Write-Host "🗑️  Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    }
    else {
        Write-Host "📋 Using existing virtual environment..." -ForegroundColor Green
        goto ActivateVenv
    }
}

# Create virtual environment
Write-Host ""
Write-Host "📋 Step 1: Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Write-Host "Please ensure Python is installed correctly" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Virtual environment created" -ForegroundColor Green

:ActivateVenv
# Activate virtual environment
Write-Host ""
Write-Host "📋 Step 2: Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You may need to change execution policy:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "📋 Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}
else {
    Write-Host "✅ Pip upgraded successfully" -ForegroundColor Green
}

# Install dependencies
Write-Host ""
Write-Host "📋 Step 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan

pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install some dependencies" -ForegroundColor Red
    Write-Host "Please check your internet connection and requirements.txt" -ForegroundColor Red
    Read-Host "Press Enter to continue anyway"
}
else {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}

# Run Python setup script
Write-Host ""
Write-Host "📋 Step 5: Running Python setup script..." -ForegroundColor Yellow
python setup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Setup script had issues, but continuing..." -ForegroundColor Yellow
}

# Final instructions
Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Your virtual environment is now active" -ForegroundColor White
Write-Host "2. Edit config/config.json and add your Discord token" -ForegroundColor White  
Write-Host "3. Run: python extract_signals.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 To reactivate the virtual environment later:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To extract signals:" -ForegroundColor Cyan
Write-Host "   python extract_signals.py" -ForegroundColor White
Write-Host ""

# Check if config file exists
if (-not (Test-Path "config/config.json")) {
    Write-Host "⚠️  Don't forget to configure your Discord token!" -ForegroundColor Yellow
    Write-Host "   Copy config/config.template.json to config/config.json" -ForegroundColor White
    Write-Host "   Then edit it with your Discord credentials" -ForegroundColor White
    Write-Host ""
}

Write-Host "Virtual environment is ready for Python package installation!" -ForegroundColor Green