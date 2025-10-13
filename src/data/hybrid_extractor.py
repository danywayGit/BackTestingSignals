"""
Enhanced Discord Client with Multiple Access Methods

This module provides both direct API access and authenticated access,
automatically choosing the best method based on what works.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

# Import our existing components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.parsers.discord_parser import DiscordMetaSignalsParser
from src.data.storage import SignalStorage

logger = logging.getLogger(__name__)


class HybridDiscordExtractor:
    """
    Discord signal extractor that tries multiple access methods
    """
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize the hybrid extractor
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.parser = DiscordMetaSignalsParser()
        self.token = self.config.get('discord', {}).get('token', '')
        
        # Setup session for direct API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        # Add token if available
        if self.token and self.token != "YOUR_BOT_TOKEN_OR_USER_TOKEN":
            self.session.headers['Authorization'] = self.token
            self.authenticated = True
            logger.info("Using authenticated API access")
        else:
            self.authenticated = False
            logger.info("Using direct API access (no authentication)")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def extract_channel_id_from_url(self, url_or_id: str) -> str:
        """
        Extract channel ID from Discord URL or return ID if already provided
        
        Args:
            url_or_id: Discord channel URL or ID
            
        Returns:
            Channel ID string
        """
        if url_or_id.startswith('http'):
            # Extract from URL like: https://discord.com/channels/SERVER_ID/CHANNEL_ID
            parts = url_or_id.strip('/').split('/')
            if len(parts) >= 2:
                return parts[-1]  # Last part should be channel ID
        
        # Already a channel ID
        return url_or_id.strip()
    
    def fetch_messages_from_api(self, channel_id: str, limit: int = 100, 
                               before: str = None) -> Optional[List[Dict]]:
        """
        Fetch messages using direct API calls
        
        Args:
            channel_id: Discord channel ID
            limit: Number of messages to fetch (max 100 per request)
            before: Message ID to fetch messages before (for pagination)
            
        Returns:
            List of message objects or None if failed
        """
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        
        params = {
            'limit': min(limit, 100)
        }
        
        if before:
            params['before'] = before
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                messages = response.json()
                logger.info(f"Successfully fetched {len(messages)} messages from API")
                return messages
            elif response.status_code == 401:
                logger.error("Unauthorized - invalid token or private channel")
                return None
            elif response.status_code == 403:
                logger.error("Forbidden - no access to this channel")
                return None
            elif response.status_code == 404:
                logger.error("Channel not found")
                return None
            elif response.status_code == 429:
                logger.error("Rate limited - need to slow down requests")
                return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching messages from API: {e}")
            return None
    
    def fetch_all_messages(self, channel_identifier: str, max_messages: int = 500) -> List[Dict]:
        """
        Fetch all messages from a channel with pagination
        
        Args:
            channel_identifier: Channel ID or URL
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of all message objects with parsed signals
        """
        channel_id = self.extract_channel_id_from_url(channel_identifier)
        logger.info(f"Extracting messages from channel ID: {channel_id}")
        
        all_messages = []
        before_id = None
        fetched_count = 0
        
        while fetched_count < max_messages:
            batch_size = min(100, max_messages - fetched_count)
            
            messages = self.fetch_messages_from_api(
                channel_id=channel_id,
                limit=batch_size,
                before=before_id
            )
            
            if not messages:
                logger.warning("No more messages or error occurred")
                break
            
            # Process each message for signals
            processed_messages = []
            for msg in messages:
                # Convert Discord API message to our format
                processed_msg = self._convert_discord_message(msg)
                processed_messages.append(processed_msg)
            
            all_messages.extend(processed_messages)
            fetched_count += len(messages)
            
            # Update pagination cursor
            before_id = messages[-1]['id']
            
            logger.info(f"Processed {fetched_count}/{max_messages} messages")
            
            # Rate limiting
            import time
            time.sleep(0.5)
            
            # Check if we've reached the end
            if len(messages) < batch_size:
                logger.info("Reached end of channel history")
                break
        
        logger.info(f"Total messages processed: {len(all_messages)}")
        return all_messages
    
    def _convert_discord_message(self, discord_msg: Dict) -> Dict:
        """
        Convert Discord API message format to our internal format
        
        Args:
            discord_msg: Raw Discord API message object
            
        Returns:
            Converted message with parsed signals
        """
        # Parse timestamp
        timestamp = datetime.fromisoformat(discord_msg['timestamp'].replace('Z', '+00:00'))
        
        # Extract attachments
        attachments = []
        for attachment in discord_msg.get('attachments', []):
            attachments.append({
                'filename': attachment.get('filename', ''),
                'url': attachment.get('url', ''),
                'content_type': attachment.get('content_type', ''),
                'size': attachment.get('size', 0)
            })
        
        # Parse signals from message content
        signals = self.parser.parse_message(
            discord_msg.get('content', ''),
            message_id=discord_msg['id'],
            timestamp=timestamp,
            attachments=attachments
        )
        
        # Convert to our format
        message_data = {
            'message_id': discord_msg['id'],
            'content': discord_msg.get('content', ''),
            'author': f"{discord_msg['author'].get('username', 'Unknown')}#{discord_msg['author'].get('discriminator', '0000')}",
            'timestamp': timestamp,
            'channel_name': 'Unknown',  # We don't have this from API
            'guild_name': 'Meta Signals',  # Assume it's Meta Signals
            'attachments': attachments,
            'signals': signals,
            'message_url': f"https://discord.com/channels/@me/{discord_msg['id']}"  # Approximation
        }
        
        return message_data
    
    def run_extraction(self, channel_identifier: str = "1190457613394137178", 
                      max_messages: int = 500) -> List[Dict]:
        """
        Main method to run signal extraction
        
        Args:
            channel_identifier: Channel ID or URL to extract from
            max_messages: Maximum number of messages to process
            
        Returns:
            List of processed messages with signals
        """
        print(f"\n🔍 Starting signal extraction...")
        print(f"Channel: {channel_identifier}")
        print(f"Max messages: {max_messages}")
        print(f"Authentication: {'Yes' if self.authenticated else 'No'}")
        
        try:
            messages_data = self.fetch_all_messages(channel_identifier, max_messages)
            
            if not messages_data:
                print("❌ No messages extracted")
                return []
            
            # Count signals
            total_signals = sum(len(msg.get('signals', [])) for msg in messages_data)
            
            print(f"\n📊 Extraction Results:")
            print(f"Messages processed: {len(messages_data)}")
            print(f"Signals found: {total_signals}")
            
            # Show sample signals
            if total_signals > 0:
                print(f"\n🎯 Sample Signals:")
                count = 0
                for msg in messages_data:
                    for signal in msg.get('signals', []):
                        if count < 3:
                            summary = self.parser.get_signal_summary(signal)
                            print(f"  {summary['symbol']} - {summary['action']} @ {summary['entry_price']}")
                            count += 1
            
            return messages_data
            
        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            print(f"❌ Error during extraction: {e}")
            return []


def main():
    """Test the hybrid extractor"""
    extractor = HybridDiscordExtractor()
    
    # Use the channel ID you found
    channel_id = "1190457613394137178"
    
    messages_data = extractor.run_extraction(channel_id, max_messages=50)
    
    if messages_data:
        # Store in database
        storage = SignalStorage()
        stored_count = storage.store_signals(messages_data)
        print(f"\n💾 Stored {stored_count} signals in database")
        
        # Export data
        csv_file = storage.export_to_csv()
        print(f"📤 Exported to: {csv_file}")


if __name__ == "__main__":
    main()