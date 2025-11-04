"""
Corrected Optimization Analysis - Refactored

Re-runs optimization analysis with proper LONG/SHORT detection.
Uses BacktestAnalyzer class to eliminate code duplication.
"""

import pandas as pd
from datetime import datetime
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from analytics.backtest_analyzer import BacktestAnalyzer

print("=" * 80)
print("🔄 OPTIMIZATION ANALYSIS - CORRECTED LONG/SHORT")
print("=" * 80)
print()

# Load old backtest data (this was used in original script)
old_backtest = "data/backtest_results/intermediate_results_900_035455.csv"
print(f"📂 Loading old backtest results: {old_backtest}")
df = pd.read_csv(old_backtest)
print(f"📊 Total signals: {len(df)}")
print()

# Correct the action column based on entry vs target comparison
df['true_action'] = df.apply(
    lambda row: 'SHORT' if row['entry_price'] > row['target1'] else 'LONG',
    axis=1
)

# Show correction stats
original_long = len(df[df['action'] == 'LONG'])
original_short = len(df[df['action'] == 'SHORT'])
true_long = len(df[df['true_action'] == 'LONG'])
true_short = len(df[df['true_action'] == 'SHORT'])

print("📊 POSITION TYPE CORRECTION:")
print(f"   Original: {original_long} LONG, {original_short} SHORT")
print(f"   Corrected: {true_long} LONG, {true_short} SHORT")
print(f"   Fixed: {abs(true_short - original_short)} signals")
print()

# Replace action column with corrected version
df['action'] = df['true_action']

# Create analyzer
analyzer = BacktestAnalyzer(df)

# Get overall stats
overall = analyzer.get_overall_stats()

print("=" * 80)
print("📊 OVERALL PERFORMANCE (ALL SIGNALS)")
print("=" * 80)
print(f"Total Signals: {overall['total']}")
print(f"Win Rate: {overall['win_rate']:.1f}%")
print(f"Wins: {overall['wins']}, Losses: {overall['losses']}")
print(f"Profit Factor: {overall['profit_factor']:.2f}")
print()

# Separate LONG and SHORT analysis
long_df = analyzer.filter_by_action('LONG')
short_df = analyzer.filter_by_action('SHORT')

long_analyzer = BacktestAnalyzer(long_df) if len(long_df) > 0 else None
short_analyzer = BacktestAnalyzer(short_df) if len(short_df) > 0 else None

print("=" * 80)
print("📈 LONG SIGNALS ANALYSIS (ACCURATE)")
print("=" * 80)

if long_analyzer:
    long_stats = long_analyzer.get_overall_stats()
    print(f"Total LONG signals: {long_stats['total']}")
    print(f"Win Rate: {long_stats['win_rate']:.1f}%")
    print(f"Wins: {long_stats['wins']}, Losses: {long_stats['losses']}")
    print(f"Profit Factor: {long_stats['profit_factor']:.2f}")
    print()
    
    # Day analysis
    print("📅 LONG Performance by Day:")
    print("-" * 80)
    day_stats = long_analyzer.analyze_by_day_of_week()
    for stat in sorted(day_stats, key=lambda x: x['win_rate'], reverse=True):
        emoji = "🔥" if stat['win_rate'] > 60 else "✅" if stat['win_rate'] > 50 else "⚠️" if stat['win_rate'] > 40 else "🚫"
        print(f"{emoji} {stat['day']:10s} | WR: {stat['win_rate']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Hour analysis
    print("⏰ LONG Performance by Hour (Top 10):")
    print("-" * 80)
    hour_stats = long_analyzer.analyze_by_hour(min_signals=5)
    for stat in sorted(hour_stats, key=lambda x: x['win_rate'], reverse=True)[:10]:
        emoji = "🔥" if stat['win_rate'] > 60 else "✅" if stat['win_rate'] > 50 else "⚠️"
        print(f"{emoji} {stat['hour']:02d}:00 UTC | WR: {stat['win_rate']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Coin analysis
    print("🪙 LONG Performance by Coin (Top 15):")
    print("-" * 80)
    coin_stats = long_analyzer.analyze_by_coin(min_signals=5)
    for stat in sorted(coin_stats, key=lambda x: x['win_rate'], reverse=True)[:15]:
        emoji = "🔥" if stat['win_rate'] > 60 else "✅" if stat['win_rate'] > 50 else "⚠️"
        print(f"{emoji} {stat['symbol']:6s} | WR: {stat['win_rate']:5.1f}% | PF: {stat['profit_factor']:5.2f} | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Month analysis
    print("📆 LONG Performance by Month:")
    print("-" * 80)
    month_stats = long_analyzer.analyze_by_month()
    for stat in sorted(month_stats, key=lambda x: x['win_rate'], reverse=True):
        emoji = "🔥" if stat['win_rate'] > 50 else "✅" if stat['win_rate'] > 45 else "⚠️" if stat['win_rate'] > 35 else "🚫"
        print(f"{emoji} {stat['month']:10s} | WR: {stat['win_rate']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Perfect combinations
    print("🎯 LONG OPTIMAL COMBINATIONS:")
    print("-" * 80)
    day_hour_combos, day_coin_combos = long_analyzer.find_perfect_combinations(min_signals=3)
    
    if day_hour_combos:
        print("\n⏰ Best Day + Hour Combinations (100% WR):")
        for combo in day_hour_combos[:5]:
            print(f"  🔥 {combo['day']} at {combo['hour']:02d}:00: {combo['wins']}/{combo['total']} wins")
    
    if day_coin_combos:
        print("\n🪙 Best Day + Coin Combinations (100% WR):")
        for combo in day_coin_combos[:5]:
            print(f"  🔥 {combo['symbol']} on {combo['day']}: {combo['wins']}/{combo['total']} wins")
    print()
    
    # Generate trading rules
    print("=" * 80)
    print("💡 LONG TRADING RULES")
    print("=" * 80)
    
    # Get best filters
    best_days = [s['day'] for s in sorted(day_stats, key=lambda x: x['win_rate'], reverse=True) 
                 if s['win_rate'] > 55 and s['total'] >= 10]
    best_hours = [s['hour'] for s in sorted(hour_stats, key=lambda x: x['win_rate'], reverse=True)[:3] 
                  if s['total'] >= 10]
    best_coins = [s['symbol'] for s in sorted(coin_stats, key=lambda x: x['win_rate'], reverse=True) 
                  if s['win_rate'] > 65 and s['total'] >= 5][:5]
    best_months = [s['month'] for s in sorted(month_stats, key=lambda x: x['win_rate'], reverse=True) 
                   if s['win_rate'] > 50]
    
    worst_days = [s['day'] for s in day_stats if s['win_rate'] < 40 and s['total'] >= 10]
    worst_months = [s['month'] for s in month_stats if s['win_rate'] < 35]
    
    print(f"✅ Trade LONG When:")
    print(f"   Days: {', '.join(best_days)}")
    print(f"   Hours: {', '.join([f'{h:02d}:00' for h in best_hours])} UTC")
    print(f"   Coins: {', '.join(best_coins)}")
    print(f"   Months: {', '.join(best_months)}")
    print()
    
    print(f"🚫 Avoid LONG When:")
    print(f"   Days: {', '.join(worst_days) if worst_days else 'None'}")
    print(f"   Months: {', '.join(worst_months) if worst_months else 'None'}")
    print()
    
    # Apply filters and show improvement
    if best_days and best_hours:
        filtered_df = long_analyzer.apply_filters(days=best_days, hours=best_hours)
        filtered_analyzer = BacktestAnalyzer(filtered_df) if len(filtered_df) > 0 else None
        
        if filtered_analyzer:
            filtered_stats = filtered_analyzer.get_overall_stats()
            improvement = filtered_stats['win_rate'] - long_stats['win_rate']
            
            print(f"📊 FILTERED PERFORMANCE:")
            print(f"   Signals: {filtered_stats['total']} ({filtered_stats['total']/long_stats['total']*100:.1f}% of LONG signals)")
            print(f"   Win Rate: {filtered_stats['win_rate']:.1f}%")
            print(f"   Improvement: +{improvement:.1f}%")
            print()
else:
    print("No LONG signals found")
    print()

print("=" * 80)
print("📉 SHORT SIGNALS ANALYSIS (NEEDS RE-BACKTEST)")
print("=" * 80)

if short_analyzer:
    short_stats = short_analyzer.get_overall_stats()
    print(f"Total SHORT signals: {short_stats['total']}")
    print()
    print("⚠️  WARNING: SHORT signals were backtested with LONG logic!")
    print(f"   Current data shows {short_stats['win_rate']:.1f}% WR (incorrect)")
    print("   Need to re-run backtest with corrected parser to get accurate SHORT performance")
    print()
    
    # Show distribution
    day_stats = short_analyzer.analyze_by_day_of_week()
    coin_stats = short_analyzer.analyze_by_coin()
    
    print("📊 SHORT Signal Distribution:")
    day_list = ', '.join([f"{s['day']}: {s['total']}" for s in day_stats[:5]])
    print(f"   By Day: {day_list}")
    coin_list = ', '.join([f"{s['symbol']}: {s['total']}" for s in sorted(coin_stats, key=lambda x: x['total'], reverse=True)[:5]])
    print(f"   Top Coins: {coin_list}")
else:
    print("No SHORT signals found")

print()

# Thursday deep dive
print("=" * 80)
print("📅 THURSDAY DEEP DIVE - CORRECTED POSITIONS")
print("=" * 80)
print()

if long_analyzer:
    thursday_long = long_analyzer.apply_filters(days=['Thursday'])
    if len(thursday_long) > 0:
        thurs_analyzer = BacktestAnalyzer(thursday_long)
        thurs_stats = thurs_analyzer.get_overall_stats()
        
        print(f"Thursday LONG: {thurs_stats['total']} signals")
        print(f"   Win Rate: {thurs_stats['win_rate']:.1f}%")
        print(f"   Wins: {thurs_stats['wins']}, Losses: {thurs_stats['losses']}")
        
        # Top coins on Thursday
        thurs_coins = thurs_analyzer.analyze_by_coin()
        if thurs_coins:
            thurs_coin_list = ', '.join([f"{s['symbol']}: {s['total']}" for s in sorted(thurs_coins, key=lambda x: x['total'], reverse=True)[:5]])
            print(f"   Top Coins: {thurs_coin_list}")

if short_analyzer:
    thursday_short = short_analyzer.apply_filters(days=['Thursday'])
    print(f"\nThursday SHORT: {len(thursday_short)} signals")
    print(f"   ⚠️  Needs re-backtest for accurate performance")
    if len(thursday_short) > 0:
        thurs_short_analyzer = BacktestAnalyzer(thursday_short)
        thurs_short_coins = thurs_short_analyzer.analyze_by_coin()
        if thurs_short_coins:
            thurs_short_coin_list = ', '.join([f"{s['symbol']}: {s['total']}" for s in sorted(thurs_short_coins, key=lambda x: x['total'], reverse=True)[:5]])
            print(f"   Top Coins: {thurs_short_coin_list}")

print()

# Save results
output = {
    'analysis_date': datetime.now().isoformat(),
    'total_signals': overall['total'],
    'long_signals': long_stats['total'] if long_analyzer else 0,
    'short_signals': short_stats['total'] if short_analyzer else 0,
    'long_wr': float(long_stats['win_rate']) if long_analyzer else 0,
    'long_best_days': best_days if long_analyzer else [],
    'long_best_hours': best_hours if long_analyzer else [],
    'long_best_coins': best_coins if long_analyzer else [],
    'long_best_months': best_months if long_analyzer else [],
    'long_worst_days': worst_days if long_analyzer else [],
    'long_worst_months': worst_months if long_analyzer else [],
    'filtered_wr': float(filtered_stats['win_rate']) if long_analyzer and filtered_analyzer else 0,
    'filtered_signals': filtered_stats['total'] if long_analyzer and filtered_analyzer else 0,
    'note': 'SHORT signals need re-backtest with corrected logic'
}

with open('corrected_optimization_results_refactored.json', 'w') as f:
    json.dump(output, f, indent=2)

print("=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print()
print("📝 Results saved to: corrected_optimization_results_refactored.json")
print()
print("🔄 NEXT STEPS:")
print("1. Re-run full backtest on corrected signals to get accurate SHORT performance")
print("2. Analyze SHORT-specific patterns once backtest is complete")
print("3. Create separate LONG and SHORT trading strategies")
