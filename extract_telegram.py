"""
Extract Signals from Telegram Channels

Simple script to extract trading signals from Telegram channels.
Supports Meta Signals format and can be adapted for other formats.
"""

import asyncio
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.telegram_client import TelegramSignalExtractor
from src.parsers.davidtech_parser import DaviddTechParser  # DaviddTech Telegram format


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config" / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


async def extract_telegram_signals(
    api_id: int,
    api_hash: str,
    phone: str,
    channel: str,
    days_back: int = 30,
    limit: int = 5000
):
    """
    Extract signals from Telegram channel.
    
    Args:
        api_id: Telegram API ID
        api_hash: Telegram API hash
        phone: Phone number
        channel: Channel username (without @)
        days_back: How many days back to extract
        limit: Maximum messages to retrieve
    """
    print("="*80)
    print("📱 TELEGRAM SIGNAL EXTRACTION")
    print("="*80)
    print(f"\n📡 Channel: @{channel}")
    print(f"📅 Looking back: {days_back} days")
    print(f"📊 Limit: {limit} messages")
    print()
    
    # Calculate start date
    start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    # Create extractor
    extractor = TelegramSignalExtractor(api_id, api_hash, phone)
    
    # Create parser (DaviddTech format)
    parser = DaviddTechParser()
    
    try:
        # Extract and parse signals
        signals = await extractor.extract_signals(
            channel_identifier=channel,
            limit=limit,
            start_date=start_date,
            parser=parser
        )
        
        # Also save raw messages for debugging
        print(f"\n📥 Extracting raw messages for debugging...")
        messages = await extractor.extract_messages(
            channel_identifier=channel,
            limit=limit,
            start_date=start_date
        )
        
        if messages:
            # Save a sample of raw messages to see the format
            import json
            sample_file = Path("telegram_messages_sample.json")
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(messages[:10], f, indent=2, default=str, ensure_ascii=False)
            print(f"📝 Saved message sample to: {sample_file}")
        
        if not signals:
            print("\n⚠️ No signals found!")
            print("   Check telegram_messages_sample.json to see message format")
            
            # Debug: Try parsing the first message manually
            if messages:
                print(f"\n🔍 DEBUG: Testing parser on first message...")
                first_msg = messages[0]
                print(f"\n📝 Message {first_msg['id']}:")
                print("="*80)
                print(first_msg['text'][:500])  # Show first 500 chars
                print("="*80)
                
                # Try to parse it
                result = parser.parse_message(first_msg['text'], first_msg['id'], first_msg['date'])
                if result:
                    print(f"\n✅ Parser returned: {result}")
                else:
                    print(f"\n❌ Parser returned None - signal not detected")
                    
                    # Show what patterns we're looking for
                    print(f"\n🔎 Looking for these patterns:")
                    print(f"   - Action: 🔴🔴 SHORT 🔴🔴 or 🟢🟢 LONG 🟢🟢")
                    print(f"   - Pair: 👜 PAIR: XXXUSDT")
                    print(f"   - Entry: ✔️ ENTRY: X.XX")
                    
            return
        
        # Display summary
        print(f"\n📊 EXTRACTION SUMMARY")
        print(f"   Total signals: {len(signals)}")
        
        # Count by action
        long_count = sum(1 for s in signals if s.get('action') == 'LONG')
        short_count = sum(1 for s in signals if s.get('action') == 'SHORT')
        print(f"   LONG signals: {long_count}")
        print(f"   SHORT signals: {short_count}")
        
        # Count by symbol
        symbols = {}
        for signal in signals:
            sym = signal.get('symbol', 'UNKNOWN')
            symbols[sym] = symbols.get(sym, 0) + 1
        
        print(f"   Unique symbols: {len(symbols)}")
        print(f"   Top 5 symbols: {', '.join([f'{k} ({v})' for k, v in sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:5]])}")
        
        # Date range
        if signals:
            dates = [s.get('timestamp') for s in signals if s.get('timestamp')]
            if dates:
                print(f"   Date range: {min(dates)} to {max(dates)}")
        
        # Save to files
        csv_path = extractor.save_to_csv(signals)
        json_path = extractor.save_to_json(signals)
        
        print(f"\n✅ SUCCESS! Extracted {len(signals)} signals")
        print(f"   CSV: {csv_path}")
        print(f"   JSON: {json_path}")
        
        return signals
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """
    Main entry point.
    Reads configuration from config/config.json
    """
    try:
        # Load config
        config = load_config()
        telegram_config = config.get('telegram', {})
        
        # Extract credentials
        api_id = int(telegram_config.get('api_id', 0))
        api_hash = telegram_config.get('api_hash', '')
        phone = telegram_config.get('phone_number', '')
        
        # Get first channel
        channels = telegram_config.get('channels', [])
        if not channels:
            print("❌ ERROR: No channels configured in config.json")
            print("   Add channel details to config/config.json under telegram.channels")
            return
        
        channel_info = channels[0]
        channel_username = channel_info.get('username', '')
        
        # Extract username from URL if needed (https://t.me/DaviddTech -> DaviddTech)
        if 'https://t.me/' in channel_username:
            channel_username = channel_username.replace('https://t.me/', '')
        elif channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        # Configuration - FULL HISTORICAL EXTRACTION
        days_back = 365  # 1 year back to get all historical signals
        limit = 2000     # Increased to capture all ~840 signals
        
        print("\n" + "="*80)
        print("📱 TELEGRAM SIGNAL EXTRACTION")
        print("="*80)
        print(f"\n📋 Configuration loaded from config.json")
        print(f"   API ID: {api_id}")
        print(f"   Phone: {phone}")
        print(f"   Channel: {channel_info.get('name')} (@{channel_username})")
        print(f"   Days back: {days_back}")
        print(f"   Limit: {limit} messages")
        print("="*80 + "\n")
        
        # Validation
        if not api_id or not api_hash or not phone:
            print("❌ ERROR: Missing Telegram credentials in config.json")
            print("\n📖 Please configure in config/config.json:")
            print("   - telegram.api_id")
            print("   - telegram.api_hash")
            print("   - telegram.phone_number")
            return
        
        if not channel_username:
            print("❌ ERROR: Channel username not configured")
            print("   Add channel username to config/config.json")
            return
        
        # Run extraction
        asyncio.run(extract_telegram_signals(
            api_id=api_id,
            api_hash=api_hash,
            phone=phone,
            channel=channel_username,
            days_back=days_back,
            limit=limit
        ))
        
    except FileNotFoundError:
        print("❌ ERROR: config/config.json not found")
        print("   Create config file with Telegram credentials")
    except KeyboardInterrupt:
        print("\n\n⚠️ Extraction cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
