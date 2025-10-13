"""
Position Type Verification Script

This script reveals the critical bug: signals are labeled as LONG but some 
are actually SHORT based on entry vs target comparison.

TRUE POSITION LOGIC:
- If entry_price > target1 → SHORT (sell high, buy back lower)
- If entry_price < target1 → LONG (buy low, sell higher)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

# Load the backtest results
df = pd.read_csv('data/backtest_results/intermediate_results_900_035455.csv')

# Parse datetime first
df['signal_time'] = pd.to_datetime(df['signal_time'], format='mixed')
df['day_of_week'] = df['signal_time'].dt.day_name()
df['hour'] = df['signal_time'].dt.hour

print("=" * 80)
print("🔍 POSITION TYPE VERIFICATION ANALYSIS")
print("=" * 80)
print()

# Determine TRUE position type based on entry vs target comparison
df['true_position'] = df.apply(
    lambda row: 'SHORT' if row['entry_price'] > row['target1'] else 'LONG',
    axis=1
)

# Count true positions
true_longs = df[df['true_position'] == 'LONG']
true_shorts = df[df['true_position'] == 'SHORT']

print(f"📊 TRUE POSITION DISTRIBUTION:")
print(f"   LONG:  {len(true_longs):3d} signals ({len(true_longs)/len(df)*100:.1f}%)")
print(f"   SHORT: {len(true_shorts):3d} signals ({len(true_shorts)/len(df)*100:.1f}%)")
print(f"   Total: {len(df):3d} signals")
print()

# Analyze what's labeled in the data
print(f"📋 LABELED POSITION TYPE (from CSV 'action' column):")
print(df['action'].value_counts())
print()

print("=" * 80)
print("⚠️  CRITICAL ISSUE IDENTIFIED:")
print("=" * 80)
print("All signals are labeled as 'LONG' in the CSV, but based on entry vs target")
print("comparison, 191 signals (21.2%) are actually SHORT positions!")
print()

# Calculate TRUE performance for each position type
print("=" * 80)
print("📈 TRUE LONG PERFORMANCE (entry < target1)")
print("=" * 80)
long_hit_target1 = true_longs['hit_target1'].sum()
long_hit_sl = true_longs['hit_stop_loss'].sum()
long_wr = (long_hit_target1 / len(true_longs)) * 100

print(f"Total Signals: {len(true_longs)}")
print(f"Hit Target 1: {long_hit_target1}")
print(f"Hit Stop Loss: {long_hit_sl}")
print(f"Win Rate: {long_wr:.1f}%")
print()

print("=" * 80)
print("📉 TRUE SHORT PERFORMANCE (entry > target1)")
print("=" * 80)
short_hit_target1 = true_shorts['hit_target1'].sum()
short_hit_sl = true_shorts['hit_stop_loss'].sum()
short_wr = (short_hit_target1 / len(true_shorts)) * 100

print(f"Total Signals: {len(true_shorts)}")
print(f"Hit Target 1: {short_hit_target1}")
print(f"Hit Stop Loss: {short_hit_sl}")
print(f"Win Rate: {short_wr:.1f}%")
print()

print("🚨 PROBLEM: SHORT signals have 0.5% win rate!")
print("   This is because they're being backtested with LONG logic:")
print("   - SHORT means: Sell at entry, buy back at target (price goes DOWN)")
print("   - But backtest checks if price goes UP to hit targets (LONG logic)")
print("   - Result: SHORT signals almost never 'win' in the current backtest")
print()

# Day of week analysis for TRUE positions
print("=" * 80)
print("📅 THURSDAY ANALYSIS - TRUE LONG vs SHORT")
print("=" * 80)

thursday_data = df[df['day_of_week'] == 'Thursday']
thursday_longs = thursday_data[thursday_data['true_position'] == 'LONG']
thursday_shorts = thursday_data[thursday_data['true_position'] == 'SHORT']

print(f"\nTotal Thursday Signals: {len(thursday_data)}")
print(f"   LONG:  {len(thursday_longs)} ({len(thursday_longs)/len(thursday_data)*100:.1f}%)")
print(f"   SHORT: {len(thursday_shorts)} ({len(thursday_shorts)/len(thursday_data)*100:.1f}%)")
print()

if len(thursday_longs) > 0:
    thurs_long_wins = thursday_longs['hit_target1'].sum()
    thurs_long_wr = (thurs_long_wins / len(thursday_longs)) * 100
    print(f"Thursday LONG Performance:")
    print(f"   Win Rate: {thurs_long_wr:.1f}%")
    print(f"   Wins: {thurs_long_wins}, Losses: {len(thursday_longs) - thurs_long_wins}")
    print()

if len(thursday_shorts) > 0:
    thurs_short_wins = thursday_shorts['hit_target1'].sum()
    thurs_short_wr = (thurs_short_wins / len(thursday_shorts)) * 100
    print(f"Thursday SHORT Performance:")
    print(f"   Win Rate: {thurs_short_wr:.1f}%")
    print(f"   Wins: {thurs_short_wins}, Losses: {len(thursday_shorts) - thurs_short_wins}")
    print()

# Day of week breakdown by TRUE position type
print("=" * 80)
print("📊 DAY OF WEEK BREAKDOWN - TRUE POSITIONS")
print("=" * 80)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

print("\nTRUE LONG by Day:")
print("-" * 80)
for day in days_order:
    day_longs = true_longs[true_longs['day_of_week'] == day]
    if len(day_longs) > 0:
        day_wins = day_longs['hit_target1'].sum()
        day_wr = (day_wins / len(day_longs)) * 100
        emoji = "🔥" if day_wr > 50 else "✅" if day_wr > 40 else "⚠️" if day_wr > 30 else "🚫"
        print(f"{emoji} {day:10s} | WR: {day_wr:5.1f}% | Signals: {len(day_longs):3d} | Wins: {day_wins:3d}")

print("\nTRUE SHORT by Day:")
print("-" * 80)
for day in days_order:
    day_shorts = true_shorts[true_shorts['day_of_week'] == day]
    if len(day_shorts) > 0:
        day_wins = day_shorts['hit_target1'].sum()
        day_wr = (day_wins / len(day_shorts)) * 100
        emoji = "🔥" if day_wr > 50 else "✅" if day_wr > 40 else "⚠️" if day_wr > 30 else "🚫"
        print(f"{emoji} {day:10s} | WR: {day_wr:5.1f}% | Signals: {len(day_shorts):3d} | Wins: {day_wins:3d}")

# Top coins by TRUE position type
print("\n" + "=" * 80)
print("🪙 TOP COINS BY TRUE POSITION TYPE")
print("=" * 80)

print("\nTRUE LONG - Top 10 Coins:")
print("-" * 80)
long_by_coin = true_longs.groupby('symbol').agg({
    'hit_target1': ['sum', 'count']
}).reset_index()
long_by_coin.columns = ['symbol', 'wins', 'total']
long_by_coin['wr'] = (long_by_coin['wins'] / long_by_coin['total']) * 100
long_by_coin = long_by_coin.sort_values('wr', ascending=False)

for _, row in long_by_coin.head(10).iterrows():
    emoji = "🔥" if row['wr'] > 60 else "✅" if row['wr'] > 50 else "⚠️"
    print(f"{emoji} {row['symbol']:6s} | WR: {row['wr']:5.1f}% | Signals: {int(row['total']):3d} | Wins: {int(row['wins']):3d}")

print("\nTRUE SHORT - Top 10 Coins:")
print("-" * 80)
if len(true_shorts) > 0:
    short_by_coin = true_shorts.groupby('symbol').agg({
        'hit_target1': ['sum', 'count']
    }).reset_index()
    short_by_coin.columns = ['symbol', 'wins', 'total']
    short_by_coin['wr'] = (short_by_coin['wins'] / short_by_coin['total']) * 100
    short_by_coin = short_by_coin.sort_values('wr', ascending=False)
    
    for _, row in short_by_coin.head(10).iterrows():
        emoji = "🔥" if row['wr'] > 60 else "✅" if row['wr'] > 50 else "⚠️" if row['wr'] > 0 else "🚫"
        print(f"{emoji} {row['symbol']:6s} | WR: {row['wr']:5.1f}% | Signals: {int(row['total']):3d} | Wins: {int(row['wins']):3d}")

# Example SHORT signals
print("\n" + "=" * 80)
print("📋 EXAMPLE SHORT SIGNALS (entry > target1)")
print("=" * 80)
print("\nFirst 5 SHORT signals:")
print(true_shorts[['symbol', 'entry_price', 'target1', 'target2', 'stop_loss', 
                   'day_of_week', 'hit_target1', 'hit_stop_loss']].head(5).to_string(index=False))
print()
print("Notice: entry_price > target1 (selling high, targeting lower price)")
print("        stop_loss > entry_price (stop loss ABOVE entry for SHORT)")
print()

# Summary and recommendations
print("=" * 80)
print("💡 KEY FINDINGS & REQUIRED FIXES")
print("=" * 80)
print()
print("1. PARSER BUG:")
print("   ❌ Current: Uses emoji (📈/📉) to determine position type")
print("   ✅ Should: Compare entry_price vs target1")
print("      - If entry > target1 → SHORT")
print("      - If entry < target1 → LONG")
print()
print("2. BACKTEST ENGINE BUG:")
print("   ❌ Current: Uses LONG logic for all signals")
print("      - Checks if price goes UP to hit targets")
print("   ✅ Should: Use SHORT logic for SHORT signals")
print("      - For SHORT: Check if price goes DOWN to hit targets")
print("      - For SHORT: Stop loss triggers when price goes UP")
print()
print("3. IMPACT:")
print("   - 191 SHORT signals (21.2%) are being evaluated incorrectly")
print("   - SHORT signals show 0.5% WR (should be much higher with correct logic)")
print("   - TRUE LONG signals: 51.5% WR (accurate)")
print("   - Overall metrics are severely distorted")
print()
print("4. THURSDAY ANALYSIS:")
print(f"   - Thursday LONG:  {len(thursday_longs):3d} signals")
print(f"   - Thursday SHORT: {len(thursday_shorts):3d} signals")
print("   - Cannot accurately assess Thursday curse until backtest is fixed")
print()
print("5. NEXT STEPS:")
print("   a) Fix discord_parser.py to detect position type correctly")
print("   b) Fix backtest_engine.py to handle SHORT positions")
print("   c) Re-run full backtest with corrected logic")
print("   d) Re-run all optimization analysis with accurate data")
print()

# Export corrected signal classification
output_data = {
    'analysis_date': datetime.now().isoformat(),
    'total_signals': len(df),
    'true_long_count': len(true_longs),
    'true_short_count': len(true_shorts),
    'true_long_wr': float(long_wr),
    'true_short_wr': float(short_wr),
    'thursday_long_count': len(thursday_longs),
    'thursday_short_count': len(thursday_shorts),
    'bug_description': 'Parser uses emoji for position type; should use entry vs target comparison',
    'impact': '191 SHORT signals misclassified and backtested with LONG logic'
}

with open('position_type_verification_results.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print("=" * 80)
print("✅ Analysis complete. Results saved to: position_type_verification_results.json")
print("=" * 80)
