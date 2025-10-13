"""
Quick Meta Signals Extraction

Direct extraction script that works with your token.
"""

import requests
import json
import re
from datetime import datetime
import csv
import os

def extract_meta_signals():
    """Extract Meta Signals using direct API calls"""
    
    print("🚀 Quick Meta Signals Extraction")
    print("=" * 40)
    
    # Read token from config
    config_path = "config/config.json"
    if not os.path.exists(config_path):
        print("❌ Config file not found!")
        print("Please make sure config/config.json exists with your Discord token")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    token = config.get('discord', {}).get('token', '')
    
    if not token or token == "YOUR_BOT_TOKEN_OR_USER_TOKEN":
        print("❌ Discord token not configured!")
        print("Please add your Discord token to config/config.json")
        return
    
    print(f"✅ Token loaded: {token[:20]}...")
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        'Authorization': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    
    # Meta Signals channel ID
    channel_id = "1190457613394137178"
    
    print(f"📡 Fetching from channel: {channel_id}")
    
    # Fetch messages
    all_messages = []
    before_id = None
    
    for batch in range(10):  # Fetch up to 1000 messages (10 batches of 100)
        print(f"📥 Fetching batch {batch + 1}...")
        
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        params = {'limit': 100}
        if before_id:
            params['before'] = before_id
        
        response = session.get(url, params=params)
        
        if response.status_code == 200:
            messages = response.json()
            if not messages:
                print("📜 No more messages")
                break
            
            all_messages.extend(messages)
            before_id = messages[-1]['id']
            print(f"   Got {len(messages)} messages (total: {len(all_messages)})")
            
            # Rate limiting
            import time
            time.sleep(0.5)
        else:
            print(f"❌ Error: {response.status_code} - {response.text[:200]}")
            break
    
    print(f"✅ Total messages fetched: {len(all_messages)}")
    
    # Parse signals
    print("🔍 Parsing signals...")
    
    signals = []
    pattern = r'📈\s*([A-Z]{2,10})\s*\|\s*USDT\s*@\s*\$?([\d,]+\.?\d*)\s*-\s*([^\-]+)\s*-\s*([\d\.]+)'
    target_pattern = r'Target\s*(\d):\s*\$?([\d,]+\.?\d*)'
    sl_pattern = r'SL\s*Close\s*(?:Below|Above):\s*\$?([\d,]+\.?\d*)'
    
    for msg in all_messages:
        content = msg.get('content', '')
        
        # Parse Meta Signals format
        match = re.search(pattern, content)
        if match:
            symbol = match.group(1)
            entry_price = float(match.group(2).replace(',', ''))
            timeframe = match.group(3).strip()
            strategy_version = match.group(4)
            
            # Extract targets
            targets = {}
            for target_match in re.finditer(target_pattern, content):
                target_num = target_match.group(1)
                target_price = float(target_match.group(2).replace(',', ''))
                targets[f'target{target_num}'] = target_price
            
            # Extract stop loss
            sl_match = re.search(sl_pattern, content)
            stop_loss = float(sl_match.group(1).replace(',', '')) if sl_match else None
            
            # Determine direction
            action = 'LONG' if '📈' in content else 'SHORT'
            
            signal = {
                'message_id': msg['id'],
                'timestamp': msg['timestamp'],
                'author': msg['author'].get('username', 'Unknown'),
                'symbol': symbol,
                'action': action,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target1': targets.get('target1'),
                'target2': targets.get('target2'),
                'target3': targets.get('target3'),
                'timeframe': timeframe,
                'strategy_version': strategy_version,
                'raw_message': content
            }
            
            signals.append(signal)
    
    print(f"🎯 Found {len(signals)} signals!")
    print(f"📊 Success rate: {len(signals)/len(all_messages)*100:.1f}%")
    
    if signals:
        # Save to CSV
        os.makedirs('data/signals', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"data/signals/meta_signals_quick_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=signals[0].keys())
            writer.writeheader()
            writer.writerows(signals)
        
        print(f"💾 Saved to: {csv_file}")
        
        # Show summary
        symbols = {}
        for signal in signals:
            symbol = signal['symbol']
            symbols[symbol] = symbols.get(symbol, 0) + 1
        
        print(f"\\n📈 Top Symbols:")
        for symbol, count in sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {symbol}: {count}")
        
        # Show recent signals
        print(f"\\n🎯 Recent Signals:")
        for i, signal in enumerate(signals[:5]):
            print(f"{i+1}. {signal['symbol']} {signal['action']} @ ${signal['entry_price']:,.2f}")
            print(f"   Targets: ${signal['target1']:,.2f}, ${signal['target2']:,.2f}, ${signal['target3']:,.2f}")
            print(f"   Stop Loss: ${signal['stop_loss']:,.2f}")
            print(f"   Time: {signal['timestamp']}")
            print()
    
    print("🎉 Extraction complete!")

if __name__ == "__main__":
    extract_meta_signals()