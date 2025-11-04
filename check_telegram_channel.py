"""
Check Telegram Channel Statistics

Quick script to see how many messages are in a Telegram channel.
"""

import asyncio
import json
from pathlib import Path
from src.data.telegram_client import TelegramSignalExtractor


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config" / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


async def check_channel():
    """Check channel statistics"""
    # Load config
    config = load_config()
    telegram_config = config.get('telegram', {})
    
    # Extract credentials
    api_id = int(telegram_config.get('api_id', 0))
    api_hash = telegram_config.get('api_hash', '')
    phone = telegram_config.get('phone_number', '')
    
    # Get channel
    channels = telegram_config.get('channels', [])
    if not channels:
        print("❌ No channels configured")
        return
    
    channel_info = channels[0]
    channel_username = channel_info.get('username', '')
    
    # Extract username from URL if needed
    if 'https://t.me/' in channel_username:
        channel_username = channel_username.replace('https://t.me/', '')
    elif channel_username.startswith('@'):
        channel_username = channel_username[1:]
    
    print("\n" + "="*80)
    print("📊 TELEGRAM CHANNEL STATISTICS")
    print("="*80)
    print(f"\n📡 Channel: {channel_info.get('name')} (@{channel_username})")
    print()
    
    # Create extractor
    extractor = TelegramSignalExtractor(api_id, api_hash, phone)
    
    try:
        await extractor.connect()
        
        # Get channel entity
        channel = await extractor.get_channel_entity(channel_username)
        
        if not channel:
            print("❌ Channel not found")
            return
        
        print(f"✅ Found channel: {channel.title}")
        
        # Get full channel info
        from telethon.tl.functions.channels import GetFullChannelRequest
        full_channel = await extractor.client(GetFullChannelRequest(channel))
        
        # Display stats
        print(f"\n📊 Channel Information:")
        print(f"   Title: {channel.title}")
        print(f"   Username: @{channel.username if channel.username else 'N/A'}")
        print(f"   Participants: {full_channel.full_chat.participants_count:,}")
        
        # Try to get message count by fetching with high limit
        print(f"\n📥 Checking message count...")
        messages = await extractor.extract_messages(
            channel_identifier=channel_username,
            limit=None  # Get all messages
        )
        
        print(f"   Total messages: {len(messages):,}")
        
        # Count signals (messages with emojis)
        signal_count = sum(1 for msg in messages if ('🔴🔴' in msg['text'] or '🟢🟢' in msg['text']))
        print(f"   Estimated signals: {signal_count:,}")
        
        # Date range
        if messages:
            dates = [msg['date'] for msg in messages]
            print(f"   Date range: {min(dates)} to {max(dates)}")
        
        await extractor.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_channel())
