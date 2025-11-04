"""
Discord Bot Client for Meta Signals

This module provides a Discord bot client to connect to the Meta Signals server
and extract historical signals from the Free Alerts channel.
Includes fallback to web API if discord.py library fails.
"""

import discord
from discord.ext import commands
import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ..parsers.discord_parser import DiscordMetaSignalsParser
from ..parsers.base_parser import Signal
from .discord_web_client import DiscordWebClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaSignalsBot:
    """Discord bot client for Meta Signals server"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize the Meta Signals bot
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.parser = DiscordMetaSignalsParser()
        self.client = None
        self.signals_data = []
        
        # Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        self.client = discord.Client(intents=intents)
        
        # Setup event handlers
        self._setup_events()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Return template structure if config doesn't exist
                return {
                    "discord": {
                        "token": "YOUR_BOT_TOKEN_OR_USER_TOKEN",
                        "servers": [
                            {
                                "name": "Meta Signals",
                                "server_id": "SERVER_ID",
                                "channels": ["Free Alerts"],
                                "description": "Meta Signals Free Alerts channel"
                            }
                        ]
                    }
                }
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _setup_events(self):
        """Setup Discord client event handlers"""
        
        @self.client.event
        async def on_ready():
            logger.info(f'Bot logged in as {self.client.user}')
            logger.info(f'Bot is in {len(self.client.guilds)} guilds')
            
            # List available guilds and channels
            for guild in self.client.guilds:
                logger.info(f'Guild: {guild.name} (ID: {guild.id})')
                for channel in guild.text_channels:
                    if 'alert' in channel.name.lower() or 'free' in channel.name.lower():
                        logger.info(f'  - Channel: {channel.name} (ID: {channel.id})')
        
        @self.client.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == self.client.user:
                return
            
            # Process messages from target channels
            if self._is_target_channel(message.channel):
                await self._process_message(message)
    
    def _is_target_channel(self, channel) -> bool:
        """Check if channel is a target channel for signal extraction"""
        channel_name = channel.name.lower()
        return any(target in channel_name for target in ['free alerts', 'alert', 'signal'])
    
    async def _process_message(self, message):
        """Process a Discord message for signals"""
        try:
            # Prepare attachments info
            attachments = []
            for attachment in message.attachments:
                attachments.append({
                    'filename': attachment.filename,
                    'url': attachment.url,
                    'content_type': getattr(attachment, 'content_type', ''),
                    'size': attachment.size
                })
            
            # Parse the message
            signals = self.parser.parse_message(
                message.content,
                message_id=str(message.id),
                timestamp=message.created_at,
                attachments=attachments
            )
            
            # Store parsed signals
            for signal in signals:
                signal_data = {
                    'signal': signal,
                    'channel_name': message.channel.name,
                    'author': str(message.author),
                    'message_url': message.jump_url,
                    'guild_name': message.guild.name if message.guild else None
                }
                self.signals_data.append(signal_data)
                logger.info(f"Extracted signal: {signal.symbol} - {signal.action} @ {signal.entry_price}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def fetch_historical_messages(self, channel_name: str = "Free Alerts", 
                                      limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Fetch historical messages from a specific channel
        
        Args:
            channel_name: Name of the channel to fetch from
            limit: Maximum number of messages to fetch
            
        Returns:
            List of message data with parsed signals
        """
        logger.info(f"Fetching historical messages from '{channel_name}' channel...")
        
        target_channel = None
        
        # Find the target channel
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                if channel_name.lower() in channel.name.lower():
                    target_channel = channel
                    logger.info(f"Found channel: {channel.name} in guild: {guild.name}")
                    break
            if target_channel:
                break
        
        if not target_channel:
            logger.error(f"Channel '{channel_name}' not found!")
            return []
        
        messages_data = []
        message_count = 0
        
        try:
            # Fetch messages
            async for message in target_channel.history(limit=limit):
                message_count += 1
                
                # Prepare attachments info
                attachments = []
                for attachment in message.attachments:
                    attachments.append({
                        'filename': attachment.filename,
                        'url': attachment.url,
                        'content_type': getattr(attachment, 'content_type', ''),
                        'size': attachment.size
                    })
                
                # Parse the message for signals
                signals = self.parser.parse_message(
                    message.content,
                    message_id=str(message.id),
                    timestamp=message.created_at,
                    attachments=attachments
                )
                
                # Store message data
                message_data = {
                    'message_id': str(message.id),
                    'content': message.content,
                    'author': str(message.author),
                    'timestamp': message.created_at,
                    'channel_name': message.channel.name,
                    'guild_name': message.guild.name if message.guild else None,
                    'attachments': attachments,
                    'signals': signals,
                    'message_url': message.jump_url
                }
                
                messages_data.append(message_data)
                
                # Log progress
                if message_count % 100 == 0:
                    logger.info(f"Processed {message_count} messages...")
                
                # Log found signals
                if signals:
                    for signal in signals:
                        logger.info(f"Found signal: {signal.symbol} - {signal.action} @ {signal.entry_price}")
        
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to read message history")
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
        
        logger.info(f"Finished fetching {message_count} messages")
        return messages_data
    
    async def connect_and_fetch(self, channel_name: str = "Free Alerts", 
                               limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Connect to Discord and fetch historical signals
        
        Args:
            channel_name: Name of the channel to fetch from
            limit: Maximum number of messages to fetch
            
        Returns:
            List of message data with parsed signals
        """
        token = self.config.get('discord', {}).get('token')
        
        if not token or token == "YOUR_BOT_TOKEN_OR_USER_TOKEN":
            logger.error("Discord token not configured! Please update config/config.json")
            return []
        
        try:
            # Start the client
            await self.client.start(token)
        except discord.LoginFailure:
            logger.error("Invalid Discord token!")
            return []
        except Exception as e:
            logger.error(f"Error connecting to Discord: {e}")
            return []
    
    def extract_with_web_client(self, channel_name: str = "Free Alerts", 
                                limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Extract signals using direct web API (fallback method)
        
        Args:
            channel_name: Name of the channel to extract from
            limit: Maximum number of messages to fetch
            
        Returns:
            List of message data with parsed signals
        """
        token = self.config.get('discord', {}).get('token')
        
        logger.info("🌐 Using web API fallback method...")
        web_client = DiscordWebClient(token)
        
        # Test connection
        if not web_client.test_connection():
            logger.error("Web client connection failed!")
            return []
        
        # Find Meta Signals server
        logger.info("🔍 Looking for Meta Signals server...")
        guild = web_client.find_guild_by_name("Meta Signals")
        if not guild:
            logger.error("Could not find Meta Signals server!")
            logger.info("Available servers:")
            for g in web_client.get_guilds():
                logger.info(f"  - {g['name']}")
            return []
        
        logger.info(f"✅ Found server: {guild['name']}")
        
        # Find channel
        logger.info(f"🔍 Looking for '{channel_name}' channel...")
        channel = web_client.find_channel_by_name(guild['id'], channel_name)
        if not channel:
            logger.error(f"Could not find '{channel_name}' channel!")
            logger.info("Available channels:")
            all_channels = web_client.get_guild_channels(guild['id'])
            for ch in all_channels:
                if ch.get('type') == 0:  # Text channel
                    logger.info(f"  - {ch.get('name')} (ID: {ch.get('id')})")
            return []
        
        logger.info(f"✅ Found channel: {channel['name']}")
        
        # Fetch messages
        logger.info(f"📥 Fetching up to {limit} messages...")
        raw_messages = web_client.get_messages_bulk(channel['id'], limit)
        logger.info(f"✅ Fetched {len(raw_messages)} messages")
        
        # Parse messages for signals
        messages_data = []
        for raw_msg in raw_messages:
            formatted_msg = web_client.format_message_for_parser(raw_msg)
            
            # Parse signals from content
            signals = self.parser.parse_message(
                formatted_msg['content'],
                message_id=formatted_msg['message_id'],
                timestamp=formatted_msg['timestamp'],
                attachments=formatted_msg['attachments']
            )
            
            # Add parsed data
            formatted_msg['signals'] = signals
            formatted_msg['channel_name'] = channel['name']
            formatted_msg['guild_name'] = guild['name']
            
            messages_data.append(formatted_msg)
            
            if signals:
                for signal in signals:
                    logger.info(f"Found signal: {signal.symbol} - {signal.action} @ {signal.entry_price}")
        
        return messages_data
    
    async def run_signal_extraction(self, channel_name: str = "Free Alerts", 
                                   limit: int = 1000):
        """
        Main method to run signal extraction
        Tries discord.py first, falls back to web API if that fails
        
        Args:
            channel_name: Name of the channel to extract from
            limit: Maximum number of messages to process
        """
        token = self.config.get('discord', {}).get('token')
        
        if not token or token == "YOUR_BOT_TOKEN_OR_USER_TOKEN":
            logger.error("Discord token not configured! Please update config/config.json")
            print("\n🚨 CONFIGURATION REQUIRED:")
            print("1. Copy config/config.template.json to config/config.json")
            print("2. Add your Discord token to the 'discord.token' field")
            print("3. You can use either a bot token or user token")
            print("\nFor bot token: Create a bot at https://discord.com/developers/applications")
            print("For user token: Use browser dev tools to get your user token (be careful!)")
            return []
        
        async def fetch_and_close():
            try:
                await self.client.wait_until_ready()
                messages_data = await self.fetch_historical_messages(channel_name, limit)
                await self.client.close()
                return messages_data
            except Exception as e:
                logger.error(f"Error in fetch_and_close: {e}")
                await self.client.close()
                return []
        
        # Try discord.py library first
        try:
            logger.info("📡 Attempting connection with discord.py library...")
            await self.client.start(token)
        except discord.LoginFailure:
            logger.warning("discord.py login failed, trying web API fallback...")
            # Use web client fallback
            return self.extract_with_web_client(channel_name, limit)
        except Exception as e:
            logger.warning(f"discord.py error: {e}, trying web API fallback...")
            # Use web client fallback
            return self.extract_with_web_client(channel_name, limit)


async def main():
    """Main function to run the Meta Signals extraction"""
    bot = MetaSignalsBot()
    messages_data = await bot.run_signal_extraction(channel_name="Free Alerts", limit=500)
    
    # Print summary
    total_signals = sum(len(msg['signals']) for msg in messages_data)
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"Total messages processed: {len(messages_data)}")
    print(f"Total signals found: {total_signals}")
    
    # Show sample signals
    if total_signals > 0:
        print(f"\n🎯 SAMPLE SIGNALS:")
        count = 0
        for msg in messages_data:
            for signal in msg['signals']:
                if count < 5:  # Show first 5 signals
                    summary = bot.parser.get_signal_summary(signal)
                    print(f"  {summary['symbol']} - {summary['action']} @ {summary['entry_price']}")
                    if summary['targets']:
                        print(f"    Targets: {summary['targets']}")
                    if summary['stop_loss']:
                        print(f"    Stop Loss: {summary['stop_loss']}")
                    if summary['timeframe']:
                        print(f"    Timeframe: {summary['timeframe']}")
                    print()
                    count += 1
    
    return messages_data


if __name__ == "__main__":
    asyncio.run(main())