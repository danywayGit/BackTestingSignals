"""
Direct Discord API Access Analysis

This module explores using Discord's direct API endpoints vs authenticated access
for extracting public channel messages.
"""

import requests
import json
from typing import List, Dict, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class DirectDiscordAPI:
    """
    Access Discord API directly using observed endpoints
    """
    
    def __init__(self):
        self.base_url = "https://discord.com/api/v9"
        self.session = requests.Session()
        
        # Set headers to mimic browser behavior
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
    
    def fetch_channel_messages_direct(self, channel_id: str, limit: int = 50, 
                                    before: str = None) -> Optional[List[Dict]]:
        """
        Fetch messages from a public channel using direct API call
        
        Args:
            channel_id: Discord channel ID (e.g., "1190457613394137178")
            limit: Number of messages to fetch (max 100)
            before: Message ID to fetch messages before (for pagination)
            
        Returns:
            List of message objects or None if failed
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        
        params = {
            'limit': min(limit, 100)  # Discord API limit
        }
        
        if before:
            params['before'] = before
        
        try:
            logger.info(f"Fetching {limit} messages from channel {channel_id}")
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                messages = response.json()
                logger.info(f"Successfully fetched {len(messages)} messages")
                return messages
            elif response.status_code == 401:
                logger.error("Unauthorized - channel may be private or require authentication")
                return None
            elif response.status_code == 403:
                logger.error("Forbidden - no access to this channel")
                return None
            elif response.status_code == 404:
                logger.error("Channel not found")
                return None
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return None
    
    def fetch_all_messages_paginated(self, channel_id: str, max_messages: int = 1000) -> List[Dict]:
        """
        Fetch all messages from a channel using pagination
        
        Args:
            channel_id: Discord channel ID
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of all message objects
        """
        all_messages = []
        before_id = None
        fetched_count = 0
        
        while fetched_count < max_messages:
            # Calculate how many to fetch in this batch
            batch_size = min(100, max_messages - fetched_count)
            
            messages = self.fetch_channel_messages_direct(
                channel_id=channel_id,
                limit=batch_size,
                before=before_id
            )
            
            if not messages:
                logger.warning("No more messages or error occurred")
                break
            
            all_messages.extend(messages)
            fetched_count += len(messages)
            
            # Update before_id for next iteration (oldest message ID)
            before_id = messages[-1]['id']
            
            logger.info(f"Fetched {fetched_count}/{max_messages} messages")
            
            # Rate limiting - be nice to Discord
            time.sleep(0.5)
            
            # If we got fewer messages than requested, we've reached the end
            if len(messages) < batch_size:
                logger.info("Reached end of channel history")
                break
        
        logger.info(f"Total messages fetched: {len(all_messages)}")
        return all_messages


class AuthenticatedDiscordAPI:
    """
    Access Discord API using authentication token
    """
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://discord.com/api/v9"
        self.session = requests.Session()
        
        # Set headers with authentication
        self.session.headers.update({
            'Authorization': f'{token}',  # User tokens don't need "Bearer" prefix
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
        })
    
    def fetch_channel_messages_auth(self, channel_id: str, limit: int = 50, 
                                  before: str = None) -> Optional[List[Dict]]:
        """
        Fetch messages using authenticated API access
        
        Args:
            channel_id: Discord channel ID
            limit: Number of messages to fetch
            before: Message ID to fetch messages before
            
        Returns:
            List of message objects or None if failed
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        
        params = {
            'limit': min(limit, 100)
        }
        
        if before:
            params['before'] = before
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                messages = response.json()
                logger.info(f"Successfully fetched {len(messages)} messages (authenticated)")
                return messages
            else:
                logger.error(f"Authenticated request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in authenticated request: {e}")
            return None


def test_both_methods(channel_id: str = "1190457613394137178", token: str = None):
    """
    Test both direct and authenticated methods
    
    Args:
        channel_id: Channel ID to test
        token: Discord token (optional)
    """
    print("🧪 Testing Discord API Access Methods")
    print("=" * 50)
    
    # Test 1: Direct API access (no authentication)
    print("\n📡 Testing Direct API Access (No Authentication)...")
    direct_api = DirectDiscordAPI()
    direct_messages = direct_api.fetch_channel_messages_direct(channel_id, limit=5)
    
    if direct_messages:
        print(f"✅ Direct access successful! Fetched {len(direct_messages)} messages")
        print(f"   Sample message: {direct_messages[0].get('content', 'No content')[:100]}...")
    else:
        print("❌ Direct access failed - channel may be private")
    
    # Test 2: Authenticated access (if token provided)
    if token and token != "YOUR_BOT_TOKEN_OR_USER_TOKEN":
        print("\n🔐 Testing Authenticated API Access...")
        auth_api = AuthenticatedDiscordAPI(token)
        auth_messages = auth_api.fetch_channel_messages_auth(channel_id, limit=5)
        
        if auth_messages:
            print(f"✅ Authenticated access successful! Fetched {len(auth_messages)} messages")
            print(f"   Sample message: {auth_messages[0].get('content', 'No content')[:100]}...")
        else:
            print("❌ Authenticated access failed")
    else:
        print("\n⏭️  Skipping authenticated test (no token provided)")
    
    # Comparison
    print("\n📊 Method Comparison:")
    print("Direct API (No Auth):")
    print("  ✅ No token required")
    print("  ✅ Works for public channels")
    print("  ❌ Limited to public content only")
    print("  ❌ May hit rate limits faster")
    print("  ❌ Less stable (Discord could block)")
    
    print("\nAuthenticated API:")
    print("  ✅ Access to all channels you can see")
    print("  ✅ More stable and official")
    print("  ✅ Better rate limiting")
    print("  ❌ Requires token")
    print("  ❌ Against ToS for user tokens")
    
    return direct_messages, auth_messages if token else None


if __name__ == "__main__":
    # Test with the Meta Signals channel ID you found
    test_both_methods("1190457613394137178")