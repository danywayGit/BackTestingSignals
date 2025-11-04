""""""

Quick Meta Signals Extraction using Web API fallbackQuick Meta Signals Extraction using Web API fallback



Direct extraction script that works with your token.Direct extraction script that works with your token.

""""""



import sysimport sys

import osimport os

import asyncioimport asyncio



# Add src to path# Add src to path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))



from src.data.discord_client import MetaSignalsBotfrom src.data.discord_client import MetaSignalsBot

from src.data.storage import SignalStoragefrom src.data.storage import SignalStorage



async def extract_meta_signals():async def extract_meta_signals():

    """Extract Meta Signals using web API fallback"""    """Extract Meta Signals using web API fallback"""

        

    print("🚀 Quick Meta Signals Extraction")    print("🚀 Quick Meta Signals Extraction")

    print("=" * 60)    print("=" * 60)

        

    bot = MetaSignalsBot()    bot = MetaSignalsBot()

    storage = SignalStorage()    storage = SignalStorage()

        

    # Extract using the correct channel name    # Extract using the correct channel name

    print("📡 Extracting from 'limited-free-alerts' channel...")    print("📡 Extracting from 'limited-free-alerts' channel...")

    messages_data = await bot.run_signal_extraction(    messages_data = await bot.run_signal_extraction(

        channel_name="limited-free-alerts",  # Correct channel name        channel_name="limited-free-alerts",  # Correct channel name

        limit=500  # Get last 500 messages        limit=500  # Get last 500 messages

    )    )

        

    if messages_data:    if messages_data:

        print(f"\n✅ Extraction successful!")        print(f"\n✅ Extraction successful!")

        print(f"📊 Extracted {len(messages_data)} messages")        print(f"📊 Extracted {len(messages_data)} messages")

                

        # Count signals        # Count signals

        total_signals = sum(len(msg.get('signals', [])) for msg in messages_data)        total_signals = sum(len(msg.get('signals', [])) for msg in messages_data)

        print(f"🎯 Found {total_signals} trading signals")        print(f"🎯 Found {total_signals} trading signals")

                

        if total_signals > 0:        if total_signals > 0:

            # Store in database            # Store in database

            print("\n💾 Storing signals in database...")            print("\n💾 Storing signals in database...")

            stored_count = storage.store_signals(messages_data)            stored_count = storage.store_signals(messages_data)

            print(f"✅ Stored {stored_count} signals")            print(f"✅ Stored {stored_count} signals")

                        

            # Export to CSV            # Export to CSV

            csv_file = storage.export_to_csv()            csv_file = storage.export_to_csv()

            print(f"✅ Exported to CSV: {csv_file}")            print(f"✅ Exported to CSV: {csv_file}")

                        

            # Show summary            # Show summary

            summary = storage.get_signals_summary()            summary = storage.get_signals_summary()

            print(f"\n📈 Signal Summary:")            print(f"\n📈 Signal Summary:")

            print(f"Total signals: {summary['total_signals']}")            print(f"Total signals: {summary['total_signals']}")

            print(f"Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")            print(f"Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")

                        

            print(f"\n📊 Top Symbols:")            print(f"\n📊 Top Symbols:")

            for symbol, count in list(summary['top_symbols'].items())[:10]:            for symbol, count in list(summary['top_symbols'].items())[:10]:

                print(f"  {symbol}: {count}")                print(f"  {symbol}: {count}")

                        

            print(f"\n🎯 Actions:")            print(f"\n🎯 Actions:")

            for action, count in summary['action_counts'].items():            for action, count in summary['action_counts'].items():

                print(f"  {action}: {count}")                print(f"  {action}: {count}")

                        

            # Show sample signals            # Show sample signals

            print(f"\n🎯 Sample Signals:")            print(f"\n🎯 Sample Signals:")

            sample_signals = storage.search_signals(limit=5)            sample_signals = storage.search_signals(limit=5)

            for i, signal in enumerate(sample_signals, 1):            for i, signal in enumerate(sample_signals, 1):

                print(f"\n{i}. {signal['symbol']} - {signal['action']} @ ${signal['entry_price']}")                print(f"\n{i}. {signal['symbol']} - {signal['action']} @ ${signal['entry_price']}")

                if signal['target1']:                if signal['target1']:

                    targets = [f"${signal['target1']}"]                    targets = [f"${signal['target1']}"]

                    if signal['target2']:                    if signal['target2']:

                        targets.append(f"${signal['target2']}")                        targets.append(f"${signal['target2']}")

                    if signal['target3']:                    if signal['target3']:

                        targets.append(f"${signal['target3']}")                        targets.append(f"${signal['target3']}")

                    print(f"   Targets: {', '.join(targets)}")                    print(f"   Targets: {', '.join(targets)}")

                if signal['stop_loss']:                if signal['stop_loss']:

                    print(f"   Stop Loss: ${signal['stop_loss']}")                    print(f"   Stop Loss: ${signal['stop_loss']}")

                if signal['timeframe']:                if signal['timeframe']:

                    print(f"   Timeframe: {signal['timeframe']}")                    print(f"   Timeframe: {signal['timeframe']}")

                        

            print(f"\n🎉 Extraction complete!")            print(f"\n🎉 Extraction complete!")

            print(f"📁 Database: data/signals/signals.db")            print(f"📁 Database: data/signals/signals.db")

            print(f"📄 CSV: {csv_file}")            print(f"📄 CSV: {csv_file}")

        else:        else:

            print("\n⚠️  No signals found in messages")            print("\n⚠️  No signals found in messages")

    else:    else:

        print("\n❌ No messages extracted")        print("\n❌ No messages extracted")



if __name__ == "__main__":if __name__ == "__main__":

    asyncio.run(extract_meta_signals())    asyncio.run(extract_meta_signals())

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