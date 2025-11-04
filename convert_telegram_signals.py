"""
Convert Telegram Signals to Backtest Format

Converts DaviddTech Telegram signal format to the format expected by
the backtesting scripts (Meta Signals format).
"""

import pandas as pd
import sys
from pathlib import Path


def convert_telegram_to_backtest_format(input_file: str, output_file: str = None):
    """
    Convert Telegram signal CSV to backtest-compatible format.
    
    Args:
        input_file: Path to Telegram signals CSV
        output_file: Path for output CSV (optional)
    """
    print("="*80)
    print("🔄 TELEGRAM SIGNALS FORMAT CONVERSION")
    print("="*80)
    print(f"\n📥 Input: {input_file}")
    
    # Read Telegram signals
    df = pd.read_csv(input_file)
    
    print(f"✅ Loaded {len(df)} signals")
    print(f"   Columns: {list(df.columns)}")
    
    # Create new DataFrame with required columns
    converted = pd.DataFrame()
    
    # Map columns
    converted['message_id'] = df['message_id']
    converted['symbol'] = df['symbol']
    converted['action'] = df['action']
    
    # Rename entry to entry_price
    converted['entry_price'] = df['entry']
    
    # Map targets
    converted['stop_loss'] = df['stop_loss']
    converted['target1'] = df['target1']  # Same as take_profit
    converted['target2'] = None  # DaviddTech only has 1 target
    converted['target3'] = None  # DaviddTech only has 1 target
    converted['take_profit'] = df['take_profit']
    
    # Other fields
    converted['timeframe'] = df['timeframe']
    converted['timestamp'] = df['timestamp']
    converted['source'] = df['source']
    
    # Optional fields from Telegram
    if 'strategy' in df.columns:
        converted['strategy_version'] = df['strategy']
    if 'risk_reward' in df.columns:
        converted['risk_reward'] = df['risk_reward']
    
    # Fields expected by backtest but not in Telegram (set to None/defaults)
    converted['algo_version'] = None
    converted['channel_name'] = 'DaviddTech'
    converted['author'] = 'DaviddTech Bot'
    converted['guild_name'] = 'Telegram'
    converted['message_url'] = None
    converted['has_attachments'] = False
    converted['attachment_count'] = 0
    converted['created_at'] = df['timestamp']
    
    # Add raw message if available
    if 'raw_message' in df.columns:
        # Truncate raw message to avoid CSV issues
        converted['raw_message'] = df['raw_message'].str[:200]
    
    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_backtest.csv"
    
    # Save converted file
    converted.to_csv(output_file, index=False)
    
    print(f"\n✅ Converted to backtest format")
    print(f"   Output: {output_file}")
    print(f"   Signals: {len(converted)}")
    print(f"\n📊 Signal breakdown:")
    print(f"   Actions: {dict(converted['action'].value_counts())}")
    print(f"   Symbols: {dict(converted['symbol'].value_counts())}")
    print(f"   Timeframes: {dict(converted['timeframe'].value_counts())}")
    
    print(f"\n⚠️  Note: DaviddTech signals have only 1 target (target1)")
    print(f"   Target2 and Target3 are set to None")
    print(f"   Backtest will focus on target1 vs stop_loss outcomes")
    
    print(f"\n🚀 Ready for backtesting!")
    print(f"   Run: python full_backtest.py \"{output_file}\"")
    print("="*80)
    
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_telegram_signals.py <telegram_signals.csv> [output.csv]")
        print("\nExample:")
        print("  python convert_telegram_signals.py data/signals/telegram_signals_export_20251104_040729.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_telegram_to_backtest_format(input_file, output_file)
