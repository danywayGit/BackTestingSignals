"""
Quick Discord token validation script with web API fallback
"""
import json
import discord
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.data.discord_web_client import DiscordWebClient

async def test_token():
    # Load config
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    token = config.get('discord', {}).get('token', '')
    
    print(f"Token length: {len(token)}")
    print(f"Token starts with: {token[:20]}...")
    print(f"Token ends with: ...{token[-20:]}")
    
    print("\n" + "="*60)
    print("METHOD 1: Testing with discord.py library...")
    print("="*60)
    
    # Try to connect
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    client = discord.Client(intents=intents)
    discord_py_success = False
    
    @client.event
    async def on_ready():
        nonlocal discord_py_success
        discord_py_success = True
        print(f'\n✅ Successfully logged in as: {client.user}')
        print(f'User ID: {client.user.id}')
        print(f'In {len(client.guilds)} guilds:')
        for guild in client.guilds:
            print(f'  - {guild.name} (ID: {guild.id})')
            print(f'    Channels with "alert" or "free":')
            for channel in guild.text_channels:
                if 'alert' in channel.name.lower() or 'free' in channel.name.lower():
                    print(f'      • {channel.name}')
        
        await client.close()
    
    try:
        await client.start(token)
    except discord.LoginFailure:
        print('\n❌ discord.py login failed!')
    except Exception as e:
        print(f'\n❌ discord.py error: {e}')
    
    # Try web API fallback
    if not discord_py_success:
        print("\n" + "="*60)
        print("METHOD 2: Testing with Web API fallback...")
        print("="*60)
        
        web_client = DiscordWebClient(token)
        
        if web_client.test_connection():
            print("\n✅ Web API connection successful!")
            
            # Get guilds
            guilds = web_client.get_guilds()
            print(f"\n📚 Found {len(guilds)} servers:")
            
            meta_signals_guild = None
            for guild in guilds:
                print(f"  - {guild['name']} (ID: {guild['id']})")
                if 'meta signals' in guild['name'].lower():
                    meta_signals_guild = guild
            
            # If Meta Signals found, check channels
            if meta_signals_guild:
                print(f"\n✅ Found Meta Signals server!")
                print(f"🔍 Checking channels...")
                
                channels = web_client.get_guild_channels(meta_signals_guild['id'])
                text_channels = [ch for ch in channels if ch.get('type') == 0]
                
                print(f"\n📝 Text channels in Meta Signals ({len(text_channels)}):")
                for channel in text_channels:
                    print(f"  - {channel.get('name')} (ID: {channel.get('id')})")
                
                # Find Free Alerts
                free_alerts = None
                for channel in text_channels:
                    if 'free' in channel.get('name', '').lower() and 'alert' in channel.get('name', '').lower():
                        free_alerts = channel
                        break
                
                if free_alerts:
                    print(f"\n✅ Found Free Alerts channel: {free_alerts['name']}")
                    print(f"🔍 Testing message fetch (first 5 messages)...")
                    
                    messages = web_client.get_channel_messages(free_alerts['id'], 5)
                    print(f"✅ Fetched {len(messages)} messages")
                    
                    if messages:
                        print(f"\nSample message:")
                        msg = messages[0]
                        print(f"  Author: {msg['author']['username']}")
                        print(f"  Date: {msg['timestamp']}")
                        content_preview = msg['content'][:150] if msg['content'] else "[No content]"
                        print(f"  Content: {content_preview}...")
                else:
                    print(f"\n⚠️  Could not find 'Free Alerts' channel")
                    print("Available channels with 'alert' or 'free':")
                    for channel in text_channels:
                        name = channel.get('name', '').lower()
                        if 'alert' in name or 'free' in name:
                            print(f"  - {channel.get('name')}")
            else:
                print(f"\n⚠️  Meta Signals server not found in your server list")
        else:
            print("\n❌ Web API connection failed!")
            print("Token is invalid or expired.")
            print("\nPlease get a fresh token:")
            print("1. Open Discord in browser")
            print("2. Press F12 → Network tab")
            print("3. Click any channel → Find 'messages' request")
            print("4. Copy 'authorization' header value")

if __name__ == '__main__':
    asyncio.run(test_token())
