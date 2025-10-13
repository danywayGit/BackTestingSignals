"""
Meta Signals Extraction Main Script

This script orchestrates the complete process of connecting to Discord,
extracting historical signals from Meta Signals, processing images for
Algo versions, and storing everything in the database.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.discord_client import MetaSignalsBot
from src.data.storage import SignalStorage
from src.analytics.image_processor import AlgoVersionExtractor, setup_tesseract

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('signal_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the complete signal extraction process"""
    
    print("🚀 Meta Signals Extraction System")
    print("=" * 50)
    
    # Check configuration
    config_path = "config/config.json"
    if not os.path.exists(config_path):
        print("❌ Configuration file not found!")
        print("Please copy config/config.template.json to config/config.json")
        print("and fill in your Discord token.")
        return
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    discord_token = config.get('discord', {}).get('token', '')
    if not discord_token or discord_token == "YOUR_BOT_TOKEN_OR_USER_TOKEN":
        print("❌ Discord token not configured!")
        print("Please add your Discord token to config/config.json")
        print("\nFor user token (recommended for this use case):")
        print("1. Open Discord in browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Network tab")
        print("4. Refresh the page")
        print("5. Look for any request and check headers for 'authorization'")
        print("6. Copy the token (without 'Bearer ' prefix)")
        print("\nFor bot token:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create a new application")
        print("3. Go to Bot section and create a bot")
        print("4. Copy the bot token")
        print("5. Invite the bot to Meta Signals server with read permissions")
        return
    
    # Setup components
    print("\n📋 Setting up components...")
    
    # Initialize storage
    storage = SignalStorage()
    print("✅ Storage system initialized")
    
    # Initialize image processor
    if not setup_tesseract():
        print("⚠️  Warning: Tesseract not available. Image processing will be skipped.")
        image_processor = None
    else:
        image_processor = AlgoVersionExtractor()
        print("✅ Image processor initialized")
    
    # Initialize Discord bot
    bot = MetaSignalsBot(config_path)
    print("✅ Discord bot initialized")
    
    # Configuration options
    print("\n⚙️  Extraction Configuration:")
    channel_name = input("Enter channel name (default: 'Free Alerts'): ").strip()
    if not channel_name:
        channel_name = "Free Alerts"
    
    message_limit = input("Enter message limit (default: 500): ").strip()
    if not message_limit:
        message_limit = 500
    else:
        try:
            message_limit = int(message_limit)
        except ValueError:
            message_limit = 500
    
    print(f"Channel: {channel_name}")
    print(f"Message limit: {message_limit}")
    
    # Start extraction
    print(f"\n🔍 Starting signal extraction from '{channel_name}'...")
    print("This may take a few minutes depending on the number of messages...")
    
    try:
        # Extract signals
        messages_data = await bot.run_signal_extraction(
            channel_name=channel_name, 
            limit=message_limit
        )
        
        if not messages_data:
            print("❌ No messages extracted. Please check your configuration and permissions.")
            return
        
        print(f"✅ Extracted {len(messages_data)} messages")
        
        # Count signals
        total_signals = sum(len(msg.get('signals', [])) for msg in messages_data)
        print(f"📊 Found {total_signals} trading signals")
        
        if total_signals == 0:
            print("⚠️  No trading signals found in the messages.")
            print("This might be due to:")
            print("- Different message format than expected")
            print("- No signals in the specified channel")
            print("- Parser needs adjustment for this specific format")
            return
        
        # Process images if available
        if image_processor:
            print("\n🖼️  Processing images for Algo versions...")
            
            messages_with_images = [msg for msg in messages_data if msg.get('attachments')]
            if messages_with_images:
                print(f"Found {len(messages_with_images)} messages with attachments")
                
                batch_results = image_processor.batch_process_signals(messages_data)
                
                print(f"✅ Processed {batch_results['total_images_processed']} images")
                print(f"📋 Found {batch_results['algo_versions_found']} Algo versions")
                
                if batch_results['processing_errors']:
                    print(f"⚠️  {len(batch_results['processing_errors'])} processing errors")
            else:
                print("No images found in messages")
        
        # Store signals in database
        print("\n💾 Storing signals in database...")
        stored_count = storage.store_signals(messages_data)
        print(f"✅ Stored {stored_count} signals in database")
        
        # Export data
        print("\n📤 Exporting data...")
        
        # Export to CSV
        csv_file = storage.export_to_csv()
        print(f"✅ Exported to CSV: {csv_file}")
        
        # Export to JSON
        json_file = storage.export_to_json()
        print(f"✅ Exported to JSON: {json_file}")
        
        # Generate summary
        print("\n📈 Signal Summary:")
        summary = storage.get_signals_summary()
        
        print(f"Total signals: {summary['total_signals']}")
        print(f"Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
        print(f"Signals with images: {summary['signals_with_attachments']} ({summary['attachment_percentage']:.1f}%)")
        
        print("\nTop symbols:")
        for symbol, count in list(summary['top_symbols'].items())[:5]:
            print(f"  {symbol}: {count}")
        
        print("\nActions:")
        for action, count in summary['action_counts'].items():
            print(f"  {action}: {count}")
        
        if summary['timeframe_counts']:
            print("\nTimeframes:")
            for timeframe, count in summary['timeframe_counts'].items():
                print(f"  {timeframe}: {count}")
        
        # Show sample signals
        print("\n🎯 Sample Signals:")
        sample_signals = storage.search_signals(limit=3)
        for i, signal in enumerate(sample_signals, 1):
            print(f"\n{i}. {signal['symbol']} - {signal['action']}")
            print(f"   Entry: {signal['entry_price']}")
            if signal['target1']:
                targets = [signal['target1']]
                if signal['target2']:
                    targets.append(signal['target2'])
                if signal['target3']:
                    targets.append(signal['target3'])
                print(f"   Targets: {targets}")
            if signal['stop_loss']:
                print(f"   Stop Loss: {signal['stop_loss']}")
            if signal['timeframe']:
                print(f"   Timeframe: {signal['timeframe']}")
            if signal['strategy_version']:
                print(f"   Strategy: {signal['strategy_version']}")
        
        print(f"\n🎉 Extraction complete!")
        print(f"Database: data/signals/signals.db")
        print(f"CSV Export: {csv_file}")
        print(f"JSON Export: {json_file}")
        print(f"Logs: signal_extraction.log")
        
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        print(f"❌ Error during extraction: {e}")
        print("Check signal_extraction.log for detailed error information")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Extraction stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)