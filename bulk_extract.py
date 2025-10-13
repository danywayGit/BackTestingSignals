"""
Meta Signals Bulk Extraction Script

This script extracts a large number of signals from Meta Signals
using our working hybrid extractor method.
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from data.hybrid_extractor import HybridDiscordExtractor
from data.storage import SignalStorage

def extract_bulk_signals():
    """Extract a large number of signals and store them"""
    
    print("🚀 Meta Signals Bulk Extraction")
    print("=" * 50)
    
    # Initialize extractor
    extractor = HybridDiscordExtractor()
    
    # Configuration
    channel_id = "1190457613394137178"  # Meta Signals Free Alerts
    max_messages = 1000  # Extract up to 1000 messages
    
    print(f"📡 Channel ID: {channel_id}")
    print(f"📊 Max messages: {max_messages}")
    print(f"🔐 Authentication: {'Yes' if extractor.authenticated else 'No'}")
    
    # Extract signals
    print(f"\n🔍 Starting bulk extraction...")
    messages_data = extractor.fetch_all_messages(channel_id, max_messages)
    
    if not messages_data:
        print("❌ No messages extracted")
        return
    
    # Count signals
    total_signals = sum(len(msg.get('signals', [])) for msg in messages_data)
    
    print(f"\n📊 Extraction Results:")
    print(f"Messages processed: {len(messages_data)}")
    print(f"Signals found: {total_signals}")
    print(f"Success rate: {total_signals/len(messages_data)*100:.1f}%")
    
    if total_signals == 0:
        print("⚠️  No signals found - this might indicate an issue")
        return
    
    # Store in database
    print(f"\n💾 Storing signals in database...")
    storage = SignalStorage()
    stored_count = storage.store_signals(messages_data)
    print(f"✅ Stored {stored_count} signals")
    
    # Export data
    print(f"\n📤 Exporting data...")
    csv_file = storage.export_to_csv()
    json_file = storage.export_to_json()
    
    print(f"✅ CSV export: {csv_file}")
    print(f"✅ JSON export: {json_file}")
    
    # Generate summary
    print(f"\n📈 Signal Analysis:")
    summary = storage.get_signals_summary()
    
    print(f"Total signals in database: {summary['total_signals']}")
    print(f"Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
    
    print(f"\nTop symbols:")
    for symbol, count in list(summary['top_symbols'].items())[:10]:
        print(f"  {symbol}: {count}")
    
    print(f"\nActions:")
    for action, count in summary['action_counts'].items():
        print(f"  {action}: {count}")
    
    if summary['timeframe_counts']:
        print(f"\nTimeframes:")
        for timeframe, count in summary['timeframe_counts'].items():
            print(f"  {timeframe}: {count}")
    
    # Show sample signals
    print(f"\n🎯 Recent Signals:")
    recent_signals = storage.search_signals(limit=5)
    for i, signal in enumerate(recent_signals, 1):
        print(f"\n{i}. {signal['symbol']} - {signal['action']} @ ${signal['entry_price']:,.2f}")
        if signal['target1']:
            targets = [signal['target1']]
            if signal['target2']:
                targets.append(signal['target2'])
            if signal['target3']:
                targets.append(signal['target3'])
            print(f"   Targets: ${', '.join(f'{t:,.2f}' for t in targets)}")
        if signal['stop_loss']:
            print(f"   Stop Loss: ${signal['stop_loss']:,.2f}")
        if signal['timeframe']:
            print(f"   Timeframe: {signal['timeframe']}")
        print(f"   Date: {signal['timestamp']}")
    
    print(f"\n🎉 Bulk extraction complete!")
    print(f"Database: data/signals/signals.db")
    print(f"CSV: {csv_file}")
    print(f"JSON: {json_file}")


if __name__ == "__main__":
    try:
        extract_bulk_signals()
    except KeyboardInterrupt:
        print("\n\n⏹️  Extraction stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()