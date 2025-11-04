"""
Telegram Signal Extraction Client

Extracts trading signals from Telegram channels using Telethon library.
Supports both public and private channels with user authentication.
"""

import asyncio
import json
import csv
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.tl.types import Message

class TelegramSignalExtractor:
    """
    Extract trading signals from Telegram channels.
    
    Supports:
    - Public channels
    - Private channels (with access)
    - Message history retrieval
    - Signal parsing and CSV export
    """
    
    def __init__(self, api_id: int, api_hash: str, phone: str, session_name: str = 'signal_extractor'):
        """
        Initialize Telegram client.
        
        Args:
            api_id: Telegram API ID (get from https://my.telegram.org)
            api_hash: Telegram API hash
            phone: Your phone number with country code (e.g., +1234567890)
            session_name: Session file name for authentication persistence
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.client = TelegramClient(session_name, api_id, api_hash)
        
    async def connect(self):
        """Connect and authenticate with Telegram"""
        await self.client.start(phone=self.phone)
        print("✅ Connected to Telegram")
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        await self.client.disconnect()
        print("✅ Disconnected from Telegram")
    
    async def get_channel_entity(self, channel_identifier: str):
        """
        Get channel entity by username or ID.
        
        Args:
            channel_identifier: Channel username (without @) or ID
            
        Returns:
            Channel entity
        """
        try:
            # Try as username
            if not channel_identifier.startswith('@'):
                channel_identifier = f'@{channel_identifier}'
            entity = await self.client.get_entity(channel_identifier)
            print(f"✅ Found channel: {entity.title}")
            return entity
        except Exception as e:
            print(f"❌ Error finding channel: {e}")
            raise
    
    async def extract_messages(
        self,
        channel_identifier: str,
        limit: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Extract messages from a Telegram channel.
        
        Args:
            channel_identifier: Channel username or ID
            limit: Maximum number of messages to retrieve
            start_date: Start date for message retrieval
            end_date: End date for message retrieval
            
        Returns:
            List of message dictionaries
        """
        await self.connect()
        
        try:
            channel = await self.get_channel_entity(channel_identifier)
            
            print(f"\n📥 Extracting messages from {channel.title}...")
            print(f"   Limit: {limit} messages")
            if start_date:
                print(f"   From: {start_date}")
            if end_date:
                print(f"   To: {end_date}")
            
            messages = []
            count = 0
            
            # Iterate through messages
            async for message in self.client.iter_messages(
                channel,
                limit=limit,
                offset_date=end_date,
                reverse=False
            ):
                # Skip if before start_date
                if start_date and message.date < start_date:
                    continue
                
                # Extract message data
                msg_data = {
                    'id': message.id,
                    'date': message.date,
                    'text': message.text or '',
                    'sender_id': message.sender_id,
                    'views': message.views,
                    'forwards': message.forwards,
                    'replies': message.replies.replies if message.replies else 0,
                    'has_media': message.media is not None,
                    'media_type': type(message.media).__name__ if message.media else None
                }
                
                messages.append(msg_data)
                count += 1
                
                if count % 100 == 0:
                    print(f"   Progress: {count} messages extracted...")
            
            print(f"\n✅ Extracted {len(messages)} messages")
            return messages
            
        except Exception as e:
            print(f"❌ Error extracting messages: {e}")
            raise
        finally:
            await self.disconnect()
    
    async def extract_signals(
        self,
        channel_identifier: str,
        limit: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        parser = None
    ) -> List[Dict]:
        """
        Extract and parse trading signals from channel.
        
        Args:
            channel_identifier: Channel username or ID
            limit: Maximum messages to retrieve
            start_date: Start date filter
            end_date: End date filter
            parser: Signal parser object with parse_message method
            
        Returns:
            List of parsed signals
        """
        messages = await self.extract_messages(
            channel_identifier, 
            limit, 
            start_date, 
            end_date
        )
        
        if not parser:
            print("⚠️ No parser provided, returning raw messages")
            return messages
        
        print(f"\n🔍 Parsing signals...")
        signals = []
        
        for msg in messages:
            try:
                # Parse signal from message text
                signal = parser.parse_message(msg['text'], msg['id'], msg['date'])
                if signal:
                    signals.append(signal)
            except Exception as e:
                print(f"⚠️ Error parsing message {msg['id']}: {e}")
                continue
        
        print(f"✅ Parsed {len(signals)} signals from {len(messages)} messages")
        return signals
    
    def save_to_csv(self, signals: List[Dict], output_dir: str = "data/signals"):
        """
        Save signals to CSV file.
        
        Args:
            signals: List of signal dictionaries
            output_dir: Output directory path
            
        Returns:
            Path to saved file
        """
        if not signals:
            print("⚠️ No signals to save")
            return None
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"telegram_signals_export_{timestamp}.csv"
        filepath = output_path / filename
        
        # Convert to DataFrame and save
        df = pd.DataFrame(signals)
        df.to_csv(filepath, index=False)
        
        print(f"\n💾 Saved {len(signals)} signals to: {filepath}")
        return filepath
    
    def save_to_json(self, signals: List[Dict], output_dir: str = "data/signals"):
        """
        Save signals to JSON file.
        
        Args:
            signals: List of signal dictionaries
            output_dir: Output directory path
            
        Returns:
            Path to saved file
        """
        if not signals:
            print("⚠️ No signals to save")
            return None
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"telegram_signals_export_{timestamp}.json"
        filepath = output_path / filename
        
        # Save as JSON
        with open(filepath, 'w') as f:
            json.dump(signals, f, indent=2, default=str)
        
        print(f"\n💾 Saved {len(signals)} signals to: {filepath}")
        return filepath


async def main_example():
    """
    Example usage of TelegramSignalExtractor.
    
    Replace with your actual credentials and channel.
    """
    # Configuration (replace with your values)
    API_ID = 12345678  # Get from https://my.telegram.org
    API_HASH = "your_api_hash_here"
    PHONE = "+1234567890"  # Your phone number
    CHANNEL = "channel_username"  # Channel username without @
    
    # Create extractor
    extractor = TelegramSignalExtractor(API_ID, API_HASH, PHONE)
    
    # Extract messages
    try:
        messages = await extractor.extract_messages(
            channel_identifier=CHANNEL,
            limit=1000,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
        
        # Save raw messages
        extractor.save_to_json(messages)
        
        # If you have a parser, use extract_signals instead:
        # from src.parsers.discord_parser import MetaSignalsParser
        # parser = MetaSignalsParser()
        # signals = await extractor.extract_signals(CHANNEL, limit=1000, parser=parser)
        # extractor.save_to_csv(signals)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("="*80)
    print("📱 TELEGRAM SIGNAL EXTRACTOR")
    print("="*80)
    print("\n⚠️  This is an example. Edit the configuration before running.")
    print("    Get API credentials from: https://my.telegram.org")
    print("\n" + "="*80)
    
    # Uncomment to run example
    # asyncio.run(main_example())
