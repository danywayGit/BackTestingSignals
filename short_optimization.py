"""
SHORT Signal Optimization Analysis
Analyzes SHORT signal performance by day, hour, coin, month to identify optimal patterns
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Load the detailed backtest results
results_file = "data/backtest_results/meta_signals_backtest_detailed_20251013_200942.csv"
df = pd.read_csv(results_file)

# Filter for SHORT signals only
short_df = df[df['action'] == 'SHORT'].copy()

# Add won column based on final_outcome
short_df['won'] = short_df['final_outcome'].str.startswith('TARGET')

print("="*80)
print("🔻 SHORT SIGNALS OPTIMIZATION ANALYSIS")
print("="*80)
print(f"\n📊 Dataset: {len(short_df)} SHORT signals")
print(f"Overall SHORT Win Rate: {short_df['won'].sum() / len(short_df) * 100:.1f}%")
print(f"Wins: {short_df['won'].sum()} | Losses: {(~short_df['won']).sum()}")
print("="*80)

# Parse timestamps
short_df['signal_time'] = pd.to_datetime(short_df['signal_time'])
short_df['day_of_week'] = short_df['signal_time'].dt.day_name()
short_df['hour_utc'] = short_df['signal_time'].dt.hour
short_df['month'] = short_df['signal_time'].dt.month_name()
short_df['date'] = short_df['signal_time'].dt.date

# Analysis storage
analysis_results = {
    'timestamp': datetime.now().isoformat(),
    'total_short_signals': len(short_df),
    'overall_short_wr': float(short_df['won'].sum() / len(short_df)),
    'overall_short_wins': int(short_df['won'].sum()),
    'overall_short_losses': int((~short_df['won']).sum()),
}

# ============================================================================
# 1. DAY OF WEEK ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📅 SHORT PERFORMANCE BY DAY OF WEEK")
print("="*80)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_stats = []

for day in day_order:
    day_data = short_df[short_df['day_of_week'] == day]
    if len(day_data) > 0:
        wins = day_data['won'].sum()
        total = len(day_data)
        wr = wins / total
        avg_profit = day_data[day_data['won']]['max_profit_pct'].mean()
        avg_loss = day_data[~day_data['won']]['max_drawdown_pct'].mean()
        
        day_stats.append({
            'day': day,
            'signals': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': wr,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'pf': (avg_profit * wins) / (abs(avg_loss) * (total - wins)) if (total - wins) > 0 else float('inf')
        })
        
        emoji = "✅" if wr > 0.50 else "⚠️" if wr > 0.45 else "❌"
        print(f"{emoji} {day:9s}: {wr*100:5.1f}% WR ({wins:3d}/{total:3d}) | "
              f"Avg Profit: {avg_profit:5.2f}% | Avg Loss: {avg_loss:5.2f}% | PF: {day_stats[-1]['pf']:.2f}")

analysis_results['by_day'] = day_stats

# ============================================================================
# 2. HOUR OF DAY ANALYSIS (UTC)
# ============================================================================
print("\n" + "="*80)
print("⏰ SHORT PERFORMANCE BY HOUR (UTC)")
print("="*80)

hour_stats = []
for hour in range(24):
    hour_data = short_df[short_df['hour_utc'] == hour]
    if len(hour_data) >= 5:  # Minimum 5 signals for meaningful analysis
        wins = hour_data['won'].sum()
        total = len(hour_data)
        wr = wins / total
        avg_profit = hour_data[hour_data['won']]['max_profit_pct'].mean()
        avg_loss = hour_data[~hour_data['won']]['max_drawdown_pct'].mean()
        
        hour_stats.append({
            'hour': hour,
            'signals': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': wr,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'pf': (avg_profit * wins) / (abs(avg_loss) * (total - wins)) if (total - wins) > 0 else float('inf'),
            'improvement_vs_baseline': (wr - analysis_results['overall_short_wr']) * 100
        })
        
        emoji = "🌟" if wr > 0.55 else "✅" if wr > 0.48 else "⚠️" if wr > 0.40 else "❌"
        improvement = (wr - analysis_results['overall_short_wr']) * 100
        print(f"{emoji} {hour:02d}:00: {wr*100:5.1f}% WR ({wins:2d}/{total:2d}) | "
              f"PF: {hour_stats[-1]['pf']:.2f} | vs Baseline: {improvement:+5.1f}%")

# Sort by win rate
hour_stats_sorted = sorted(hour_stats, key=lambda x: x['win_rate'], reverse=True)
analysis_results['by_hour'] = hour_stats

print("\n🏆 TOP 5 SHORT HOURS:")
for i, stat in enumerate(hour_stats_sorted[:5], 1):
    print(f"{i}. {stat['hour']:02d}:00 UTC: {stat['win_rate']*100:.1f}% WR "
          f"({stat['wins']}/{stat['signals']}) PF: {stat['pf']:.2f}")

# ============================================================================
# 3. COIN ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("🪙 SHORT PERFORMANCE BY COIN")
print("="*80)

coin_stats = []
coin_groups = short_df.groupby('symbol')

for coin, coin_data in coin_groups:
    if len(coin_data) >= 3:  # Minimum 3 signals
        wins = coin_data['won'].sum()
        total = len(coin_data)
        wr = wins / total
        avg_profit = coin_data[coin_data['won']]['max_profit_pct'].mean()
        avg_loss = coin_data[~coin_data['won']]['max_drawdown_pct'].mean()
        
        coin_stats.append({
            'coin': coin,
            'signals': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': wr,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'pf': (avg_profit * wins) / (abs(avg_loss) * (total - wins)) if (total - wins) > 0 else float('inf')
        })

# Sort by win rate, then by signal count
coin_stats_sorted = sorted(coin_stats, key=lambda x: (x['win_rate'], x['signals']), reverse=True)
analysis_results['by_coin'] = coin_stats

print("\n🏆 TOP SHORT COINS (sorted by WR, then signal count):")
for i, stat in enumerate(coin_stats_sorted[:15], 1):
    emoji = "🌟" if stat['win_rate'] > 0.60 else "✅" if stat['win_rate'] > 0.48 else "⚠️"
    print(f"{emoji} {i:2d}. {stat['coin']:6s}: {stat['win_rate']*100:5.1f}% WR "
          f"({stat['wins']:2d}/{stat['signals']:2d}) | "
          f"Avg Profit: {stat['avg_profit']:5.2f}% | PF: {stat['pf']:.2f}")

# ============================================================================
# 4. MONTH ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📆 SHORT PERFORMANCE BY MONTH")
print("="*80)

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
month_stats = []

for month in month_order:
    month_data = short_df[short_df['month'] == month]
    if len(month_data) > 0:
        wins = month_data['won'].sum()
        total = len(month_data)
        wr = wins / total
        avg_profit = month_data[month_data['won']]['max_profit_pct'].mean()
        avg_loss = month_data[~month_data['won']]['max_drawdown_pct'].mean()
        
        month_stats.append({
            'month': month,
            'signals': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': wr,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'pf': (avg_profit * wins) / (abs(avg_loss) * (total - wins)) if (total - wins) > 0 else float('inf')
        })
        
        emoji = "✅" if wr > 0.48 else "⚠️" if wr > 0.40 else "❌"
        print(f"{emoji} {month:9s}: {wr*100:5.1f}% WR ({wins:3d}/{total:3d}) | "
              f"Avg Profit: {avg_profit:5.2f}% | PF: {month_stats[-1]['pf']:.2f}")

analysis_results['by_month'] = month_stats

# ============================================================================
# 5. COMBINATION ANALYSIS - Find perfect SHORT setups
# ============================================================================
print("\n" + "="*80)
print("🎯 PERFECT SHORT COMBINATIONS (100% Win Rate with 3+ signals)")
print("="*80)

perfect_combos = []

# Coin + Day combinations
for coin in short_df['symbol'].unique():
    for day in day_order:
        combo_data = short_df[(short_df['symbol'] == coin) & (short_df['day_of_week'] == day)]
        if len(combo_data) >= 3 and combo_data['won'].all():
            wins = combo_data['won'].sum()
            total = len(combo_data)
            avg_profit = combo_data['max_profit_pct'].mean()
            perfect_combos.append({
                'type': 'Coin+Day',
                'combo': f"{coin} on {day}",
                'signals': total,
                'wins': wins,
                'avg_profit': avg_profit
            })
            print(f"🌟 {coin} on {day}: {total}/{total} wins | Avg Profit: {avg_profit:.2f}%")

# Coin + Hour combinations
for coin in short_df['symbol'].unique():
    for hour in range(24):
        combo_data = short_df[(short_df['symbol'] == coin) & (short_df['hour_utc'] == hour)]
        if len(combo_data) >= 3 and combo_data['won'].all():
            wins = combo_data['won'].sum()
            total = len(combo_data)
            avg_profit = combo_data['max_profit_pct'].mean()
            perfect_combos.append({
                'type': 'Coin+Hour',
                'combo': f"{coin} at {hour:02d}:00",
                'signals': total,
                'wins': wins,
                'avg_profit': avg_profit
            })
            print(f"🌟 {coin} at {hour:02d}:00: {total}/{total} wins | Avg Profit: {avg_profit:.2f}%")

# Day + Hour combinations
for day in day_order:
    for hour in range(24):
        combo_data = short_df[(short_df['day_of_week'] == day) & (short_df['hour_utc'] == hour)]
        if len(combo_data) >= 3 and combo_data['won'].all():
            wins = combo_data['won'].sum()
            total = len(combo_data)
            avg_profit = combo_data['max_profit_pct'].mean()
            perfect_combos.append({
                'type': 'Day+Hour',
                'combo': f"{day} at {hour:02d}:00",
                'signals': total,
                'wins': wins,
                'avg_profit': avg_profit
            })
            print(f"🌟 {day} at {hour:02d}:00: {total}/{total} wins | Avg Profit: {avg_profit:.2f}%")

if not perfect_combos:
    print("No perfect combinations found with 3+ signals.")

analysis_results['perfect_combinations'] = perfect_combos

# ============================================================================
# 6. HIGH-PERFORMANCE SHORT COMBINATIONS (>60% WR with 5+ signals)
# ============================================================================
print("\n" + "="*80)
print("🎯 HIGH-PERFORMANCE SHORT COMBINATIONS (>60% WR, 5+ signals)")
print("="*80)

high_perf_combos = []

# Coin + Day combinations
for coin in short_df['symbol'].unique():
    for day in day_order:
        combo_data = short_df[(short_df['symbol'] == coin) & (short_df['day_of_week'] == day)]
        if len(combo_data) >= 5:
            wins = combo_data['won'].sum()
            total = len(combo_data)
            wr = wins / total
            if wr > 0.60:
                avg_profit = combo_data[combo_data['won']]['max_profit_pct'].mean()
                high_perf_combos.append({
                    'type': 'Coin+Day',
                    'combo': f"{coin} on {day}",
                    'signals': total,
                    'wins': wins,
                    'win_rate': wr,
                    'avg_profit': avg_profit
                })
                print(f"✅ {coin} on {day}: {wr*100:.1f}% WR ({wins}/{total}) | Avg Profit: {avg_profit:.2f}%")

# Coin + Hour combinations
for coin in short_df['symbol'].unique():
    for hour in range(24):
        combo_data = short_df[(short_df['symbol'] == coin) & (short_df['hour_utc'] == hour)]
        if len(combo_data) >= 5:
            wins = combo_data['won'].sum()
            total = len(combo_data)
            wr = wins / total
            if wr > 0.60:
                avg_profit = combo_data[combo_data['won']]['max_profit_pct'].mean()
                high_perf_combos.append({
                    'type': 'Coin+Hour',
                    'combo': f"{coin} at {hour:02d}:00",
                    'signals': total,
                    'wins': wins,
                    'win_rate': wr,
                    'avg_profit': avg_profit
                })
                print(f"✅ {coin} at {hour:02d}:00: {wr*100:.1f}% WR ({wins}/{total}) | Avg Profit: {avg_profit:.2f}%")

if not high_perf_combos:
    print("No high-performance combinations found with 5+ signals.")

analysis_results['high_performance_combinations'] = high_perf_combos

# ============================================================================
# 7. FILTERED SHORT STRATEGY
# ============================================================================
print("\n" + "="*80)
print("🎯 OPTIMIZED SHORT STRATEGY")
print("="*80)

# Identify best filters based on analysis
best_days = [stat['day'] for stat in day_stats if stat['win_rate'] > 0.48]
best_hours = [stat['hour'] for stat in hour_stats if stat['win_rate'] > 0.50 and stat['signals'] >= 5]
best_coins = [stat['coin'] for stat in coin_stats if stat['win_rate'] > 0.55 and stat['signals'] >= 3]

print(f"\n📋 FILTER CRITERIA:")
print(f"Best Days (>48% WR): {', '.join(best_days) if best_days else 'None'}")
print(f"Best Hours (>50% WR, 5+ signals): {', '.join([f'{h:02d}:00' for h in best_hours]) if best_hours else 'None'}")
print(f"Best Coins (>55% WR, 3+ signals): {', '.join(best_coins) if best_coins else 'None'}")

# Apply progressive filters
filters = []

# Filter 1: Best days only
if best_days:
    filtered_df = short_df[short_df['day_of_week'].isin(best_days)]
    wins = filtered_df['won'].sum()
    total = len(filtered_df)
    wr = wins / total if total > 0 else 0
    filters.append({
        'name': 'Best Days Only',
        'criteria': f"Days in {best_days}",
        'signals': total,
        'wins': wins,
        'win_rate': wr,
        'pct_of_total': total / len(short_df) * 100
    })
    print(f"\n✅ Filter 1 - Best Days: {wr*100:.1f}% WR ({wins}/{total}) - {total/len(short_df)*100:.1f}% of signals")

# Filter 2: Best days + Best hours
if best_days and best_hours:
    filtered_df = short_df[short_df['day_of_week'].isin(best_days) & short_df['hour_utc'].isin(best_hours)]
    wins = filtered_df['won'].sum()
    total = len(filtered_df)
    wr = wins / total if total > 0 else 0
    filters.append({
        'name': 'Best Days + Hours',
        'criteria': f"Days {best_days} + Hours {best_hours}",
        'signals': total,
        'wins': wins,
        'win_rate': wr,
        'pct_of_total': total / len(short_df) * 100
    })
    print(f"✅ Filter 2 - Best Days + Hours: {wr*100:.1f}% WR ({wins}/{total}) - {total/len(short_df)*100:.1f}% of signals")

# Filter 3: Best coins only
if best_coins:
    filtered_df = short_df[short_df['symbol'].isin(best_coins)]
    wins = filtered_df['won'].sum()
    total = len(filtered_df)
    wr = wins / total if total > 0 else 0
    filters.append({
        'name': 'Best Coins Only',
        'criteria': f"Coins in {best_coins}",
        'signals': total,
        'wins': wins,
        'win_rate': wr,
        'pct_of_total': total / len(short_df) * 100
    })
    print(f"✅ Filter 3 - Best Coins: {wr*100:.1f}% WR ({wins}/{total}) - {total/len(short_df)*100:.1f}% of signals")

# Filter 4: Best days + Best coins
if best_days and best_coins:
    filtered_df = short_df[short_df['day_of_week'].isin(best_days) & short_df['symbol'].isin(best_coins)]
    wins = filtered_df['won'].sum()
    total = len(filtered_df)
    wr = wins / total if total > 0 else 0
    filters.append({
        'name': 'Best Days + Coins',
        'criteria': f"Days {best_days} + Coins {best_coins}",
        'signals': total,
        'wins': wins,
        'win_rate': wr,
        'pct_of_total': total / len(short_df) * 100
    })
    print(f"✅ Filter 4 - Best Days + Coins: {wr*100:.1f}% WR ({wins}/{total}) - {total/len(short_df)*100:.1f}% of signals")

# Filter 5: Ultra-filtered (Best days + hours + coins)
if best_days and best_hours and best_coins:
    filtered_df = short_df[
        short_df['day_of_week'].isin(best_days) & 
        short_df['hour_utc'].isin(best_hours) & 
        short_df['symbol'].isin(best_coins)
    ]
    wins = filtered_df['won'].sum()
    total = len(filtered_df)
    wr = wins / total if total > 0 else 0
    filters.append({
        'name': 'Ultra-Filtered',
        'criteria': f"Days {best_days} + Hours {best_hours} + Coins {best_coins}",
        'signals': total,
        'wins': wins,
        'win_rate': wr,
        'pct_of_total': total / len(short_df) * 100
    })
    print(f"✅ Filter 5 - Ultra-Filtered: {wr*100:.1f}% WR ({wins}/{total}) - {total/len(short_df)*100:.1f}% of signals")

analysis_results['filtered_strategies'] = filters

# ============================================================================
# 8. WORST PERFORMERS - What to avoid
# ============================================================================
print("\n" + "="*80)
print("❌ WORST SHORT PERFORMERS - AVOID THESE")
print("="*80)

print("\n📅 Worst Days:")
worst_days = sorted(day_stats, key=lambda x: x['win_rate'])[:3]
for stat in worst_days:
    print(f"❌ {stat['day']:9s}: {stat['win_rate']*100:5.1f}% WR ({stat['wins']}/{stat['signals']})")

print("\n⏰ Worst Hours (with 5+ signals):")
worst_hours = sorted([h for h in hour_stats if h['signals'] >= 5], key=lambda x: x['win_rate'])[:5]
for stat in worst_hours:
    print(f"❌ {stat['hour']:02d}:00: {stat['win_rate']*100:5.1f}% WR ({stat['wins']}/{stat['signals']})")

print("\n🪙 Worst Coins (with 3+ signals):")
worst_coins = sorted([c for c in coin_stats if c['signals'] >= 3], key=lambda x: x['win_rate'])[:10]
for stat in worst_coins:
    print(f"❌ {stat['coin']:6s}: {stat['win_rate']*100:5.1f}% WR ({stat['wins']}/{stat['signals']})")

print("\n📆 Worst Months:")
worst_months = sorted(month_stats, key=lambda x: x['win_rate'])[:3]
for stat in worst_months:
    print(f"❌ {stat['month']:9s}: {stat['win_rate']*100:5.1f}% WR ({stat['wins']}/{stat['signals']})")

# ============================================================================
# SAVE RESULTS
# ============================================================================
# Convert numpy types to native Python types for JSON serialization
def convert_to_native_types(obj):
    if isinstance(obj, dict):
        return {k: convert_to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    else:
        return obj

output_file = "short_optimization_results.json"
with open(output_file, 'w') as f:
    json.dump(convert_to_native_types(analysis_results), f, indent=2)

print("\n" + "="*80)
print(f"✅ Analysis complete! Results saved to {output_file}")
print("="*80)
