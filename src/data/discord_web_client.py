"""
Discord Web API Client - Fallback for when discord.py doesn't work

This module uses direct HTTP requests to Discord's REST API as a fallback
when the discord.py library fails to authenticate.
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DiscordWebClient:
    """Direct HTTP client for Discord REST API"""
    
    BASE_URL = "https://discord.com/api/v10"
    
    def __init__(self, token: str):
        """
        Initialize the web client
        
        Args:
            token: Discord user token or bot token
        """
        self.token = token
        self.session = requests.Session()
        
        # Setup headers to mimic browser/official client
        self.session.headers.update({
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-Super-Properties': self._get_super_properties(),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://discord.com/channels/@me',
            'Origin': 'https://discord.com',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
    
    def _get_super_properties(self) -> str:
        """Generate X-Super-Properties header"""
        import base64
        props = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "browser_version": "120.0.0.0",
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": 250000,
            "client_event_source": None
        }
        return base64.b64encode(json.dumps(props).encode()).decode()
    
    def test_connection(self) -> bool:
        """
        Test if the token is valid
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/users/@me")
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Connected as: {user_data.get('username')}#{user_data.get('discriminator')}")
                return True
            else:
                logger.error(f"Connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_guilds(self) -> List[Dict[str, Any]]:
        """
        Get list of guilds (servers) the user is in
        
        Returns:
            List of guild data
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/users/@me/guilds")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited
                retry_after = response.json().get('retry_after', 1)
                logger.warning(f"Rate limited on get_guilds, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.get_guilds()
            else:
                logger.error(f"Failed to get guilds: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting guilds: {e}")
            return []
    
    def get_guild_channels(self, guild_id: str) -> List[Dict[str, Any]]:
        """
        Get channels for a specific guild
        
        Args:
            guild_id: The guild/server ID
            
        Returns:
            List of channel data
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/guilds/{guild_id}/channels")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited
                retry_after = response.json().get('retry_after', 1)
                logger.warning(f"Rate limited on get_guild_channels, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.get_guild_channels(guild_id)
            else:
                logger.error(f"Failed to get channels: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
    
    def get_channel_messages(self, channel_id: str, limit: int = 100, 
                           before: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages from a channel
        
        Args:
            channel_id: The channel ID
            limit: Maximum number of messages (max 100 per request)
            before: Get messages before this message ID
            
        Returns:
            List of message data
        """
        try:
            params = {'limit': min(limit, 100)}
            if before:
                params['before'] = before
            
            response = self.session.get(
                f"{self.BASE_URL}/channels/{channel_id}/messages",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited
                retry_after = response.json().get('retry_after', 1)
                logger.warning(f"Rate limited, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.get_channel_messages(channel_id, limit, before)
            else:
                logger.error(f"Failed to get messages: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    def get_messages_bulk(self, channel_id: str, total_limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get multiple batches of messages from a channel
        
        Args:
            channel_id: The channel ID
            total_limit: Total number of messages to fetch
            
        Returns:
            List of all message data
        """
        all_messages = []
        before_id = None
        
        while len(all_messages) < total_limit:
            batch_limit = min(100, total_limit - len(all_messages))
            messages = self.get_channel_messages(channel_id, batch_limit, before_id)
            
            if not messages:
                break
            
            all_messages.extend(messages)
            before_id = messages[-1]['id']
            
            logger.info(f"Fetched {len(all_messages)}/{total_limit} messages...")
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        return all_messages
    
    def find_guild_by_name(self, guild_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a guild by name
        
        Args:
            guild_name: Name of the guild to find
            
        Returns:
            Guild data or None if not found
        """
        guilds = self.get_guilds()
        for guild in guilds:
            if guild_name.lower() in guild.get('name', '').lower():
                return guild
        return None
    
    def find_channel_by_name(self, guild_id: str, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a channel by name in a guild
        
        Args:
            guild_id: The guild ID
            channel_name: Name of the channel to find
            
        Returns:
            Channel data or None if not found
        """
        channels = self.get_guild_channels(guild_id)
        for channel in channels:
            if channel.get('type') == 0:  # Text channel
                if channel_name.lower() in channel.get('name', '').lower():
                    return channel
        return None
    
    def format_message_for_parser(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format Discord API message to match parser expectations
        
        Args:
            message: Raw message data from API
            
        Returns:
            Formatted message data
        """
        # Parse timestamp
        timestamp_str = message.get('timestamp', '')
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            timestamp = datetime.now()
        
        # Format attachments
        attachments = []
        for att in message.get('attachments', []):
            attachments.append({
                'filename': att.get('filename', ''),
                'url': att.get('url', ''),
                'content_type': att.get('content_type', ''),
                'size': att.get('size', 0)
            })
        
        return {
            'message_id': message.get('id'),
            'content': message.get('content', ''),
            'author': f"{message.get('author', {}).get('username', 'Unknown')}#{message.get('author', {}).get('discriminator', '0000')}",
            'timestamp': timestamp,
            'attachments': attachments,
            'message_url': f"https://discord.com/channels/{message.get('guild_id', '@me')}/{message.get('channel_id')}/{message.get('id')}"
        }


def test_web_client():
    """Test the web client"""
    import sys
    import os
    
    # Load config
    config_path = "config/config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        token = config.get('discord', {}).get('token', '')
        
        if token and token != "YOUR_BOT_TOKEN_OR_USER_TOKEN":
            print("Testing Discord Web Client...")
            client = DiscordWebClient(token)
            
            if client.test_connection():
                print("✅ Connection successful!")
                
                # List guilds
                guilds = client.get_guilds()
                print(f"\n📚 Found {len(guilds)} servers:")
                for guild in guilds:
                    print(f"  - {guild['name']} (ID: {guild['id']})")
                
                # Try to find Meta Signals
                meta_guild = client.find_guild_by_name("Meta Signals")
                if meta_guild:
                    print(f"\n✅ Found Meta Signals server!")
                    
                    # Get channels
                    channel = client.find_channel_by_name(meta_guild['id'], "Free Alerts")
                    if channel:
                        print(f"✅ Found Free Alerts channel!")
                        print(f"\nFetching messages...")
                        
                        messages = client.get_messages_bulk(channel['id'], 10)
                        print(f"✅ Fetched {len(messages)} messages")
                        
                        if messages:
                            print("\nSample message:")
                            print(f"  Author: {messages[0]['author']['username']}")
                            print(f"  Content: {messages[0]['content'][:100]}...")
                    else:
                        print("❌ Could not find Free Alerts channel")
                else:
                    print("❌ Could not find Meta Signals server")
            else:
                print("❌ Connection failed")
        else:
            print("❌ No token configured")
    else:
        print("❌ Config file not found")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_web_client()
