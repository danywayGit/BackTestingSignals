"""
Corrected Optimization Analysis

Re-runs optimization analysis with proper LONG/SHORT detection.
Uses the re-parsed signals with corrected position types.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import defaultdict

print("=" * 80)
print("🔄 OPTIMIZATION ANALYSIS - CORRECTED LONG/SHORT")
print("=" * 80)
print()

# Load corrected signals
signals_file = "data/signals/meta_signals_corrected_20251013_195448.csv"
print(f"📂 Loading: {signals_file}")
df = pd.read_csv(signals_file)
print(f"📊 Total signals: {len(df)}")
print()

# We need to simulate backtest results for corrected signals
# Since we don't have actual backtest results yet, let's use the old backtest data
# but with corrected position types

old_backtest = "data/backtest_results/intermediate_results_900_035455.csv"
print(f"📂 Loading old backtest results: {old_backtest}")
bt_df = pd.read_csv(old_backtest)
print(f"📊 Backtest signals: {len(bt_df)}")
print()

# Correct the action column based on entry vs target comparison
bt_df['true_action'] = bt_df.apply(
    lambda row: 'SHORT' if row['entry_price'] > row['target1'] else 'LONG',
    axis=1
)

# Show correction stats
original_long = len(bt_df[bt_df['action'] == 'LONG'])
original_short = len(bt_df[bt_df['action'] == 'SHORT'])
true_long = len(bt_df[bt_df['true_action'] == 'LONG'])
true_short = len(bt_df[bt_df['true_action'] == 'SHORT'])

print("📊 POSITION TYPE CORRECTION:")
print(f"   Original: {original_long} LONG, {original_short} SHORT")
print(f"   Corrected: {true_long} LONG, {true_short} SHORT")
print(f"   Fixed: {abs(true_short - original_short)} signals")
print()

# Parse datetime
bt_df['signal_time'] = pd.to_datetime(bt_df['signal_time'], format='mixed')
bt_df['day_of_week'] = bt_df['signal_time'].dt.day_name()
bt_df['hour'] = bt_df['signal_time'].dt.hour
bt_df['month'] = bt_df['signal_time'].dt.month
bt_df['month_name'] = bt_df['signal_time'].dt.month_name()

# For SHORT signals, we need to recalculate wins/losses with correct logic
# SHORT wins when: price goes DOWN to hit targets (entry > target)
# SHORT loses when: price goes UP to hit stop loss (stop loss > entry)

def recalculate_short_outcome(row):
    """Recalculate outcome for SHORT signals with correct logic"""
    if row['true_action'] == 'LONG':
        # LONG signals are already correct
        return row['hit_target1']
    else:
        # SHORT signal - needs recalculation
        # For now, we'll mark them as needing re-backtest
        # We can't accurately recalculate without re-running price checks
        return None  # Unknown until proper backtest

bt_df['corrected_win'] = bt_df.apply(recalculate_short_outcome, axis=1)

# Separate analysis for LONG (where we have accurate data) and SHORT (needs re-backtest)
long_signals = bt_df[bt_df['true_action'] == 'LONG'].copy()
short_signals = bt_df[bt_df['true_action'] == 'SHORT'].copy()

print("=" * 80)
print("📈 LONG SIGNALS ANALYSIS (ACCURATE)")
print("=" * 80)
print(f"Total LONG signals: {len(long_signals)}")
print()

# LONG Performance
long_wins = long_signals['hit_target1'].sum()
long_wr = (long_wins / len(long_signals)) * 100

print(f"🏆 LONG Overall Performance:")
print(f"   Win Rate: {long_wr:.1f}%")
print(f"   Wins: {long_wins}, Losses: {len(long_signals) - long_wins}")
print()

# LONG by Day of Week
print("📅 LONG Performance by Day:")
print("-" * 80)
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
long_day_stats = []

for day in days_order:
    day_data = long_signals[long_signals['day_of_week'] == day]
    if len(day_data) > 0:
        wins = day_data['hit_target1'].sum()
        total = len(day_data)
        wr = (wins / total) * 100
        long_day_stats.append({
            'day': day,
            'wr': wr,
            'wins': wins,
            'total': total
        })
        emoji = "🔥" if wr > 60 else "✅" if wr > 50 else "⚠️" if wr > 40 else "🚫"
        print(f"{emoji} {day:10s} | WR: {wr:5.1f}% | Signals: {total:3d} | Wins: {wins:3d}")

print()

# LONG by Hour
print("⏰ LONG Performance by Hour (Top 10):")
print("-" * 80)
long_hour_stats = []

for hour in range(24):
    hour_data = long_signals[long_signals['hour'] == hour]
    if len(hour_data) >= 5:  # Minimum 5 signals
        wins = hour_data['hit_target1'].sum()
        total = len(hour_data)
        wr = (wins / total) * 100
        long_hour_stats.append({
            'hour': hour,
            'wr': wr,
            'wins': wins,
            'total': total
        })

long_hour_stats.sort(key=lambda x: x['wr'], reverse=True)

for stat in long_hour_stats[:10]:
    emoji = "🔥" if stat['wr'] > 60 else "✅" if stat['wr'] > 50 else "⚠️"
    print(f"{emoji} {stat['hour']:02d}:00 UTC | WR: {stat['wr']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")

print()

# LONG by Coin
print("🪙 LONG Performance by Coin (Top 15):")
print("-" * 80)
long_coin_stats = []

for symbol in long_signals['symbol'].unique():
    coin_data = long_signals[long_signals['symbol'] == symbol]
    if len(coin_data) >= 5:  # Minimum 5 signals
        wins = coin_data['hit_target1'].sum()
        total = len(coin_data)
        wr = (wins / total) * 100
        
        # Calculate profit factor
        profits = coin_data[coin_data['hit_target1'] == True]['max_profit_pct'].sum()
        losses = abs(coin_data[coin_data['hit_stop_loss'] == True]['max_drawdown_pct'].sum())
        pf = profits / losses if losses > 0 else 0
        
        long_coin_stats.append({
            'symbol': symbol,
            'wr': wr,
            'wins': wins,
            'total': total,
            'pf': pf
        })

long_coin_stats.sort(key=lambda x: x['wr'], reverse=True)

for stat in long_coin_stats[:15]:
    emoji = "🔥" if stat['wr'] > 60 else "✅" if stat['wr'] > 50 else "⚠️"
    print(f"{emoji} {stat['symbol']:6s} | WR: {stat['wr']:5.1f}% | PF: {stat['pf']:5.2f} | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")

print()

# LONG by Month
print("📆 LONG Performance by Month:")
print("-" * 80)
long_month_stats = []

for month_name in long_signals['month_name'].unique():
    month_data = long_signals[long_signals['month_name'] == month_name]
    if len(month_data) > 0:
        wins = month_data['hit_target1'].sum()
        total = len(month_data)
        wr = (wins / total) * 100
        long_month_stats.append({
            'month': month_name,
            'wr': wr,
            'wins': wins,
            'total': total
        })

long_month_stats.sort(key=lambda x: x['wr'], reverse=True)

for stat in long_month_stats:
    emoji = "🔥" if stat['wr'] > 50 else "✅" if stat['wr'] > 45 else "⚠️" if stat['wr'] > 35 else "🚫"
    print(f"{emoji} {stat['month']:10s} | WR: {stat['wr']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")

print()

# LONG by Timeframe (if column exists)
if 'timeframe' in long_signals.columns:
    print("📊 LONG Performance by Timeframe:")
    print("-" * 80)
    for tf in long_signals['timeframe'].unique():
        tf_data = long_signals[long_signals['timeframe'] == tf]
        if len(tf_data) >= 5:
            wins = tf_data['hit_target1'].sum()
            total = len(tf_data)
            wr = (wins / total) * 100
            print(f"  {tf:6s} | WR: {wr:5.1f}% | Signals: {total:3d} | Wins: {wins:3d}")

print()

# LONG Optimal Combinations
print("🎯 LONG OPTIMAL COMBINATIONS:")
print("-" * 80)

# Best coin + day combinations
print("\n📊 Best Coin + Day Combinations (100% WR):")
for symbol in long_coin_stats[:10]:  # Top 10 coins
    for day in days_order:
        combo_data = long_signals[
            (long_signals['symbol'] == symbol['symbol']) &
            (long_signals['day_of_week'] == day)
        ]
        if len(combo_data) >= 3:  # Minimum 3 signals
            wins = combo_data['hit_target1'].sum()
            if wins == len(combo_data):  # 100% win rate
                print(f"  🔥 {symbol['symbol']} on {day}: {wins}/{len(combo_data)} wins")

# Best coin + hour combinations
print("\n⏰ Best Coin + Hour Combinations (100% WR):")
for symbol in long_coin_stats[:10]:
    for hour_stat in long_hour_stats[:5]:  # Top 5 hours
        combo_data = long_signals[
            (long_signals['symbol'] == symbol['symbol']) &
            (long_signals['hour'] == hour_stat['hour'])
        ]
        if len(combo_data) >= 3:
            wins = combo_data['hit_target1'].sum()
            if wins == len(combo_data):
                print(f"  🔥 {symbol['symbol']} at {hour_stat['hour']:02d}:00: {wins}/{len(combo_data)} wins")

print()
print("=" * 80)
print("📉 SHORT SIGNALS ANALYSIS (NEEDS RE-BACKTEST)")
print("=" * 80)
print(f"Total SHORT signals: {len(short_signals)}")
print()
print("⚠️  WARNING: SHORT signals were backtested with LONG logic!")
print("   Current data shows 0.5% WR for SHORT (incorrect)")
print("   Need to re-run backtest with corrected parser to get accurate SHORT performance")
print()

# SHORT distribution
print("📊 SHORT Signal Distribution:")
print(f"   By Day: {dict(short_signals['day_of_week'].value_counts())}")
print(f"   Top Coins: {dict(short_signals['symbol'].value_counts().head())}")
print()

# Thursday Analysis
print("=" * 80)
print("📅 THURSDAY DEEP DIVE - CORRECTED POSITIONS")
print("=" * 80)

thursday_long = long_signals[long_signals['day_of_week'] == 'Thursday']
thursday_short = short_signals[short_signals['day_of_week'] == 'Thursday']

print(f"\nThursday LONG: {len(thursday_long)} signals")
if len(thursday_long) > 0:
    thurs_long_wins = thursday_long['hit_target1'].sum()
    thurs_long_wr = (thurs_long_wins / len(thursday_long)) * 100
    print(f"   Win Rate: {thurs_long_wr:.1f}%")
    print(f"   Wins: {thurs_long_wins}, Losses: {len(thursday_long) - thurs_long_wins}")
    print(f"   Top Coins: {dict(thursday_long['symbol'].value_counts().head())}")

print(f"\nThursday SHORT: {len(thursday_short)} signals")
print(f"   ⚠️  Needs re-backtest for accurate performance")
print(f"   Top Coins: {dict(thursday_short['symbol'].value_counts().head())}")

print()

# Generate trading rules for LONG signals
print("=" * 80)
print("💡 CORRECTED LONG TRADING RULES")
print("=" * 80)
print()

print("🎯 OPTIMAL LONG SETUP:")
print("-" * 80)
# Filter for best performance
best_days = [stat['day'] for stat in long_day_stats if stat['wr'] > 55]
best_hours = [stat['hour'] for stat in long_hour_stats[:3]]  # Top 3 hours
best_coins = [stat['symbol'] for stat in long_coin_stats if stat['wr'] > 65][:5]
best_months = [stat['month'] for stat in long_month_stats if stat['wr'] > 50]

print(f"✅ Trade LONG When:")
print(f"   Days: {', '.join(best_days)}")
print(f"   Hours: {', '.join([f'{h:02d}:00' for h in best_hours])} UTC")
print(f"   Coins: {', '.join(best_coins)}")
print(f"   Months: {', '.join(best_months)}")
print()

worst_days = [stat['day'] for stat in long_day_stats if stat['wr'] < 40]
worst_months = [stat['month'] for stat in long_month_stats if stat['wr'] < 35]

print(f"🚫 Avoid LONG When:")
print(f"   Days: {', '.join(worst_days)}")
print(f"   Months: {', '.join(worst_months)}")
print()

# Calculate expected performance with filters
filtered_signals = long_signals[
    (long_signals['day_of_week'].isin(best_days)) &
    (long_signals['hour'].isin(best_hours))
]

if len(filtered_signals) > 0:
    filtered_wins = filtered_signals['hit_target1'].sum()
    filtered_wr = (filtered_wins / len(filtered_signals)) * 100
    improvement = filtered_wr - long_wr
    
    print(f"📊 FILTERED PERFORMANCE:")
    print(f"   Signals: {len(filtered_signals)} ({len(filtered_signals)/len(long_signals)*100:.1f}% of LONG signals)")
    print(f"   Win Rate: {filtered_wr:.1f}%")
    print(f"   Improvement: +{improvement:.1f}%")
    print()

# Save results
output = {
    'analysis_date': datetime.now().isoformat(),
    'total_signals': len(bt_df),
    'long_signals': len(long_signals),
    'short_signals': len(short_signals),
    'long_wr': float(long_wr),
    'long_best_days': best_days,
    'long_best_hours': best_hours,
    'long_best_coins': best_coins,
    'long_best_months': best_months,
    'long_worst_days': worst_days,
    'long_worst_months': worst_months,
    'filtered_wr': float(filtered_wr) if len(filtered_signals) > 0 else 0,
    'filtered_signals': len(filtered_signals),
    'note': 'SHORT signals need re-backtest with corrected logic'
}

with open('corrected_optimization_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print()
print("📝 Results saved to: corrected_optimization_results.json")
print()
print("🔄 NEXT STEPS:")
print("1. Re-run full backtest on corrected signals to get accurate SHORT performance")
print("2. Analyze SHORT-specific patterns once backtest is complete")
print("3. Create separate LONG and SHORT trading strategies")
