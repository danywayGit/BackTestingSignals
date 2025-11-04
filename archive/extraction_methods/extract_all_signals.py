"""
Extract signals since October 12 using web API fallback
"""
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.discord_client import MetaSignalsBot
from src.data.storage import SignalStorage

async def main():
    print("🚀 Extracting signals from limited-free-alerts channel...")
    print("📅 Getting all signals since October 12, 2025")
    print("=" * 60)
    
    bot = MetaSignalsBot()
    storage = SignalStorage()
    
    # Extract with increased limit to get all signals since Oct 12
    messages_data = await bot.run_signal_extraction(
        channel_name='limited-free-alerts',
        limit=1000
    )
    
    if messages_data:
        print(f"\n✅ Extracted {len(messages_data)} messages")
        
        signals = sum(len(msg.get('signals', [])) for msg in messages_data)
        print(f"🎯 Found {signals} signals")
        
        # Store in database
        stored = storage.store_signals(messages_data)
        print(f"💾 Stored {stored} signals in database")
        
        # Export to CSV
        csv_file = storage.export_to_csv()
        print(f"📄 Exported to: {csv_file}")
        
        # Show summary
        summary = storage.get_signals_summary()
        print(f"\n📊 Signal Summary:")
        print(f"Total signals: {summary['total_signals']}")
        print(f"Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
        
        print(f"\n📈 Top 10 Symbols:")
        for symbol, count in list(summary['top_symbols'].items())[:10]:
            print(f"  {symbol}: {count}")
        
        print(f"\n🎯 Actions:")
        for action, count in summary['action_counts'].items():
            print(f"  {action}: {count}")
        
        return csv_file
    else:
        print("\n❌ No messages extracted")
        return None

if __name__ == "__main__":
    csv_file = asyncio.run(main())
    if csv_file:
        print(f"\n✅ Extraction complete! Ready for backtesting.")
        print(f"📝 Next step: Run backtest on {csv_file}")
