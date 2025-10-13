"""
Meta Signals Message Inspector

This script inspects actual messages from Meta Signals to understand
their format and adjust our parser accordingly.
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.hybrid_extractor import HybridDiscordExtractor


def inspect_messages(channel_id: str = "1190457613394137178", limit: int = 20):
    """
    Inspect actual messages from Meta Signals channel
    
    Args:
        channel_id: Channel ID to inspect
        limit: Number of messages to inspect
    """
    print("🔍 Meta Signals Message Inspector")
    print("=" * 50)
    
    extractor = HybridDiscordExtractor()
    
    # Fetch raw messages using API
    messages = extractor.fetch_messages_from_api(channel_id, limit)
    
    if not messages:
        print("❌ Could not fetch messages")
        return
    
    print(f"📨 Inspecting {len(messages)} messages...")
    print()
    
    signal_indicators = [
        'BUY', 'SELL', 'LONG', 'SHORT', 'ENTRY', 'TARGET', 'TP', 'SL', 'STOP',
        'USDT', 'BTC', 'ETH', 'SIGNAL', 'ALERT'
    ]
    
    for i, msg in enumerate(messages[:10]):  # Show first 10 messages
        print(f"📨 Message {i+1}:")
        print(f"   ID: {msg['id']}")
        print(f"   Author: {msg['author'].get('username', 'Unknown')}")
        print(f"   Timestamp: {msg['timestamp']}")
        
        content = msg.get('content', '')
        print(f"   Content: {content[:200]}...")
        
        # Check for signal indicators
        has_indicators = any(indicator in content.upper() for indicator in signal_indicators)
        print(f"   Has signal indicators: {'Yes' if has_indicators else 'No'}")
        
        # Check attachments
        attachments = msg.get('attachments', [])
        if attachments:
            print(f"   Attachments: {len(attachments)}")
            for att in attachments:
                print(f"     - {att.get('filename', 'Unknown')} ({att.get('size', 0)} bytes)")
        
        # Check embeds (Discord embeds often contain structured data)
        embeds = msg.get('embeds', [])
        if embeds:
            print(f"   Embeds: {len(embeds)}")
            for embed in embeds:
                print(f"     - Title: {embed.get('title', 'No title')}")
                print(f"     - Description: {embed.get('description', 'No description')[:100]}...")
        
        print()
    
    # Analysis
    print("📊 Analysis:")
    total_with_content = sum(1 for msg in messages if msg.get('content', '').strip())
    total_with_attachments = sum(1 for msg in messages if msg.get('attachments'))
    total_with_embeds = sum(1 for msg in messages if msg.get('embeds'))
    total_with_indicators = sum(1 for msg in messages 
                               if any(indicator in msg.get('content', '').upper() 
                                     for indicator in signal_indicators))
    
    print(f"Total messages: {len(messages)}")
    print(f"Messages with text content: {total_with_content}")
    print(f"Messages with attachments: {total_with_attachments}")
    print(f"Messages with embeds: {total_with_embeds}")
    print(f"Messages with signal indicators: {total_with_indicators}")
    
    # Save detailed analysis
    analysis_file = "message_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(messages[:5], f, indent=2, default=str)  # Save first 5 for detailed analysis
    
    print(f"\n💾 Detailed analysis saved to: {analysis_file}")
    
    # Suggest parser improvements
    if total_with_embeds > 0:
        print("\n💡 Suggestion: Many messages have embeds - consider parsing embed content")
    if total_with_attachments > 0:
        print("💡 Suggestion: Messages have attachments - image processing may be important")
    if total_with_indicators == 0:
        print("⚠️  Warning: No obvious signal indicators found - signals may be in embeds or images")


if __name__ == "__main__":
    inspect_messages()