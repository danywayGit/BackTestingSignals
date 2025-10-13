"""
Re-parse Signals with Corrected Parser

This script re-parses signals using the corrected position type detection logic:
- If entry_price > target1 → SHORT
- If entry_price < target1 → LONG

This fixes the major bug where all signals were labeled as LONG.
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.parsers.discord_parser import DiscordMetaSignalsParser

# Load existing signals
print("=" * 80)
print("🔄 RE-PARSING SIGNALS WITH CORRECTED PARSER")
print("=" * 80)
print()

signals_file = "data/signals/meta_signals_quick_20251013_025440.csv"
df = pd.read_csv(signals_file)

print(f"📂 Loaded: {signals_file}")
print(f"📊 Total signals: {len(df)}")
print()

# Initialize corrected parser
parser = DiscordMetaSignalsParser()

# Track corrections
corrections = {
    'total': 0,
    'long_to_short': 0,
    'short_to_long': 0,
    'unchanged': 0
}

corrected_signals = []

print("🔍 Re-parsing each signal...")
for idx, row in df.iterrows():
    old_action = row['action']
    entry_price = float(row['entry_price'])
    target1 = float(row['target1']) if pd.notna(row['target1']) else None
    
    # Determine correct action based on entry vs target1
    if target1:
        if entry_price > target1:
            new_action = 'SHORT'
        else:
            new_action = 'LONG'
    else:
        # If no target1, keep original (should rarely happen)
        new_action = old_action
    
    # Track changes
    if old_action != new_action:
        if old_action == 'LONG' and new_action == 'SHORT':
            corrections['long_to_short'] += 1
        elif old_action == 'SHORT' and new_action == 'LONG':
            corrections['short_to_long'] += 1
    else:
        corrections['unchanged'] += 1
    
    corrections['total'] += 1
    
    # Create corrected signal
    corrected_row = row.copy()
    corrected_row['action'] = new_action
    corrected_signals.append(corrected_row)
    
    # Progress indicator
    if (idx + 1) % 100 == 0:
        print(f"  Processed {idx + 1}/{len(df)} signals...")

print()
print("=" * 80)
print("📊 CORRECTION SUMMARY")
print("=" * 80)
print(f"Total Signals: {corrections['total']}")
print(f"LONG → SHORT: {corrections['long_to_short']} signals")
print(f"SHORT → LONG: {corrections['short_to_long']} signals")
print(f"Unchanged: {corrections['unchanged']} signals")
print()

# Create corrected DataFrame
corrected_df = pd.DataFrame(corrected_signals)

# Show position type distribution
print("📊 POSITION TYPE DISTRIBUTION:")
print(corrected_df['action'].value_counts())
print()

# Verify with entry vs target comparison
verify_long = corrected_df[corrected_df['entry_price'] < corrected_df['target1']]
verify_short = corrected_df[corrected_df['entry_price'] > corrected_df['target1']]

print("✅ VERIFICATION (entry vs target comparison):")
print(f"LONG signals (entry < target1): {len(verify_long)}")
print(f"SHORT signals (entry > target1): {len(verify_short)}")
print()

# Save corrected signals
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"data/signals/meta_signals_corrected_{timestamp}.csv"
corrected_df.to_csv(output_file, index=False)

print(f"💾 Corrected signals saved to: {output_file}")
print()

# Show examples of corrected SHORT signals
print("=" * 80)
print("📋 EXAMPLE SHORT SIGNALS (corrected from LONG)")
print("=" * 80)

short_signals = corrected_df[corrected_df['action'] == 'SHORT'].head(5)
for idx, signal in short_signals.iterrows():
    print(f"\nSignal {idx + 1}:")
    print(f"  Symbol: {signal['symbol']}")
    print(f"  Entry: ${signal['entry_price']:,.2f}")
    print(f"  Target1: ${signal['target1']:,.2f}")
    print(f"  Target2: ${signal['target2']:,.2f}")
    print(f"  Stop Loss: ${signal['stop_loss']:,.2f}")
    print(f"  Timeframe: {signal['timeframe']}")
    print(f"  Strategy: {signal['strategy_version']}")
    print(f"  Note: Entry > Target1 = SHORT position")

print()
print("=" * 80)
print("✅ RE-PARSING COMPLETE!")
print("=" * 80)
print()
print("Next steps:")
print("1. Run full backtest with corrected signals")
print("2. Re-run optimization analysis")
print("3. Update LONG vs SHORT performance analysis")
