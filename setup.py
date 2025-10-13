"""
Setup Script for Meta Signals Extraction

This script helps set up the environment and configuration
for extracting signals from Meta Signals Discord server.
"""

import os
import json
import shutil


def create_config():
    """Create configuration file from template"""
    template_path = "config/config.template.json"
    config_path = "config/config.json"
    
    if os.path.exists(config_path):
        print("✅ Configuration file already exists")
        return True
    
    if not os.path.exists(template_path):
        print("❌ Template configuration file not found")
        return False
    
    try:
        shutil.copy(template_path, config_path)
        print("✅ Created config/config.json from template")
        return True
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        return False


def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/signals",
        "data/market_data", 
        "data/results",
        "data/images",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "discord.py",
        "pandas", 
        "numpy",
        "requests",
        "PIL",
        "pytesseract",
        "cv2"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "PIL":
                import PIL
            elif package == "cv2":
                import cv2
            else:
                __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install -r requirements.txt")
        return False
    
    return True


def setup_discord_instructions():
    """Provide Discord setup instructions"""
    print("\n🤖 Discord Setup Instructions:")
    print("=" * 40)
    
    print("\nOption 1: User Token (Recommended for this use case)")
    print("1. Open Discord in your web browser")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the Network tab")
    print("4. Refresh the page or send a message")
    print("5. Look for any request and check the Headers")
    print("6. Find 'authorization' header and copy the token")
    print("7. Add this token to config/config.json")
    
    print("\nOption 2: Bot Token")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Create a new application")
    print("3. Go to Bot section and create a bot")
    print("4. Copy the bot token")
    print("5. Invite the bot to Meta Signals server with:")
    print("   - Read Message History permission")
    print("   - View Channel permission")
    print("6. Add the bot token to config/config.json")
    
    print("\n⚠️  Important Notes:")
    print("- User tokens are easier but against Discord ToS for automated use")
    print("- Bot tokens are official but require server permissions")
    print("- For personal use/research, user token is usually fine")
    print("- Make sure you have access to Meta Signals server")


def setup_virtual_environment():
    """Check and guide virtual environment setup"""
    import sys
    
    print("\n🐍 Virtual Environment Check:")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        print(f"   Python path: {sys.executable}")
        return True
    else:
        print("❌ No virtual environment detected")
        print("\n📋 Virtual Environment Setup:")
        print("1. Create virtual environment:")
        print("   python -m venv venv")
        print("\n2. Activate virtual environment:")
        print("   Windows: .\\venv\\Scripts\\Activate.ps1")
        print("   macOS/Linux: source venv/bin/activate")
        print("\n3. Upgrade pip:")
        print("   python -m pip install --upgrade pip")
        print("\n4. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n5. Re-run this setup script")
        return False


def main():
    """Main setup function"""
    print("🚀 Meta Signals Extraction Setup")
    print("=" * 40)
    
    # Check virtual environment first
    venv_ok = setup_virtual_environment()
    if not venv_ok:
        print("\n❌ Please set up virtual environment first!")
        return
    
    # Create directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Create config file
    print("\n⚙️  Setting up configuration...")
    config_created = create_config()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    # Setup instructions
    if config_created:
        setup_discord_instructions()
    
    print("\n" + "=" * 40)
    
    if deps_ok and config_created and venv_ok:
        print("✅ Setup complete!")
        print("\nNext steps:")
        print("1. Edit config/config.json and add your Discord token")
        print("2. Join the Meta Signals Discord server")
        print("3. Run: python extract_signals.py")
    else:
        print("❌ Setup incomplete")
        if not venv_ok:
            print("- Set up virtual environment first")
        if not deps_ok:
            print("- Install dependencies: pip install -r requirements.txt")
        if not config_created:
            print("- Check config file creation")


if __name__ == "__main__":
    main()