"""
LONG & SHORT Optimization Analysis

Comprehensive optimization analysis for both LONG and SHORT signals.
Finds optimal trading patterns by day/hour/coin/month for each position type.
Uses BacktestAnalyzer class to eliminate code duplication.
"""

import pandas as pd
from datetime import datetime
import json
import sys
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from src.analytics.backtest_analyzer import BacktestAnalyzer

print("=" * 80)
print("📊 LONG & SHORT OPTIMIZATION ANALYSIS")
print("=" * 80)
print()

# Find backtest file - either from command line argument or latest
from pathlib import Path

if len(sys.argv) > 1:
    # Use specified file
    backtest_file = Path(sys.argv[1])
    if not backtest_file.exists():
        print(f"❌ File not found: {backtest_file}")
        sys.exit(1)
else:
    # Find latest backtest results
    results_dir = Path('data/backtest_results')
    detailed_files = sorted(results_dir.glob('*_backtest_detailed_*.csv'), key=lambda x: x.stat().st_mtime, reverse=True)

    if not detailed_files:
        print("❌ No backtest results found in data/backtest_results/")
        print("   Please run full_backtest.py first")
        sys.exit(1)

    # Find latest file with actual data (more than 1 line)
    backtest_file = None
    for file in detailed_files:
        try:
            test_df = pd.read_csv(file)
            if len(test_df) > 10:  # Need at least 10 signals
                backtest_file = file
                break
        except:
            continue

    if not backtest_file:
        print("❌ No backtest results with sufficient data found")
        sys.exit(1)

print(f"📂 Loading backtest results: {backtest_file.name}")
df = pd.read_csv(backtest_file)
print(f"📊 Total signals: {len(df)}")

# Check if action column exists
if 'action' not in df.columns:
    print("❌ 'action' column not found in backtest results")
    sys.exit(1)

print()

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
            total = combo.get('total', combo.get('count', '?'))
            wins = combo.get('wins', combo.get('count', '?'))
            print(f"  🔥 {combo['day']} at {combo['hour']:02d}:00: {wins}/{total} wins")
    else:
        print("\n⏰ No perfect Day + Hour combinations found (min 3 signals)")
    
    if day_coin_combos:
        print("\n🪙 Best Day + Coin Combinations (100% WR):")
        for combo in day_coin_combos[:5]:
            total = combo.get('total', combo.get('count', '?'))
            wins = combo.get('wins', combo.get('count', '?'))
            print(f"  🔥 {combo['symbol']} on {combo['day']}: {wins}/{total} wins")
    else:
        print("\n🪙 No perfect Day + Coin combinations found (min 3 signals)")
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
print("📉 SHORT SIGNALS ANALYSIS (DETAILED)")
print("=" * 80)

if short_analyzer:
    short_stats = short_analyzer.get_overall_stats()
    print(f"Total SHORT signals: {short_stats['total']}")
    print(f"Win Rate: {short_stats['win_rate']:.1f}%")
    print(f"Wins: {short_stats['wins']}, Losses: {short_stats['losses']}")
    print(f"Profit Factor: {short_stats['profit_factor']:.2f}")
    print()
    
    # Day analysis
    print("📅 SHORT Performance by Day:")
    print("-" * 80)
    short_day_stats = short_analyzer.analyze_by_day_of_week()
    for stat in sorted(short_day_stats, key=lambda x: x['win_rate'], reverse=True):
        emoji = "🔥" if stat['win_rate'] > 60 else "✅" if stat['win_rate'] > 50 else "⚠️" if stat['win_rate'] > 40 else "🚫"
        print(f"{emoji} {stat['day']:10s} | WR: {stat['win_rate']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Hour analysis
    print("⏰ SHORT Performance by Hour (Top 10):")
    print("-" * 80)
    short_hour_stats = short_analyzer.analyze_by_hour(min_signals=5)
    for stat in sorted(short_hour_stats, key=lambda x: x['win_rate'], reverse=True)[:10]:
        emoji = "🔥" if stat['win_rate'] > 60 else "✅" if stat['win_rate'] > 50 else "⚠️"
        print(f"{emoji} {stat['hour']:02d}:00 UTC | WR: {stat['win_rate']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Coin analysis
    print("🪙 SHORT Performance by Coin (Top 15):")
    print("-" * 80)
    short_coin_stats = short_analyzer.analyze_by_coin(min_signals=5)
    for stat in sorted(short_coin_stats, key=lambda x: x['win_rate'], reverse=True)[:15]:
        emoji = "🔥" if stat['win_rate'] > 60 else "✅" if stat['win_rate'] > 50 else "⚠️"
        print(f"{emoji} {stat['symbol']:6s} | WR: {stat['win_rate']:5.1f}% | PF: {stat['profit_factor']:5.2f} | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Month analysis
    print("📆 SHORT Performance by Month:")
    print("-" * 80)
    short_month_stats = short_analyzer.analyze_by_month()
    for stat in sorted(short_month_stats, key=lambda x: x['win_rate'], reverse=True):
        emoji = "🔥" if stat['win_rate'] > 50 else "✅" if stat['win_rate'] > 45 else "⚠️" if stat['win_rate'] > 35 else "🚫"
        print(f"{emoji} {stat['month']:10s} | WR: {stat['win_rate']:5.1f}% | Signals: {stat['total']:3d} | Wins: {stat['wins']:3d}")
    print()
    
    # Perfect combinations
    print("🎯 SHORT OPTIMAL COMBINATIONS:")
    print("-" * 80)
    short_day_hour_combos, short_day_coin_combos = short_analyzer.find_perfect_combinations(min_signals=3)
    
    if short_day_hour_combos:
        print("\n⏰ Best Day + Hour Combinations (100% WR):")
        for combo in short_day_hour_combos[:5]:
            total = combo.get('total', combo.get('count', '?'))
            wins = combo.get('wins', combo.get('count', '?'))
            print(f"  🔥 {combo['day']} at {combo['hour']:02d}:00: {wins}/{total} wins")
    else:
        print("\n⏰ No perfect Day + Hour combinations found (min 3 signals)")
    
    if short_day_coin_combos:
        print("\n🪙 Best Day + Coin Combinations (100% WR):")
        for combo in short_day_coin_combos[:5]:
            total = combo.get('total', combo.get('count', '?'))
            wins = combo.get('wins', combo.get('count', '?'))
            print(f"  🔥 {combo['symbol']} on {combo['day']}: {wins}/{total} wins")
    else:
        print("\n🪙 No perfect Day + Coin combinations found (min 3 signals)")
    print()
    
    # Generate trading rules
    print("=" * 80)
    print("💡 SHORT TRADING RULES")
    print("=" * 80)
    
    # Get best filters
    short_best_days = [s['day'] for s in sorted(short_day_stats, key=lambda x: x['win_rate'], reverse=True) 
                 if s['win_rate'] > 55 and s['total'] >= 10]
    short_best_hours = [s['hour'] for s in sorted(short_hour_stats, key=lambda x: x['win_rate'], reverse=True)[:3] 
                  if s['total'] >= 10]
    short_best_coins = [s['symbol'] for s in sorted(short_coin_stats, key=lambda x: x['win_rate'], reverse=True) 
                  if s['win_rate'] > 65 and s['total'] >= 5][:5]
    short_best_months = [s['month'] for s in sorted(short_month_stats, key=lambda x: x['win_rate'], reverse=True) 
                   if s['win_rate'] > 50]
    
    short_worst_days = [s['day'] for s in short_day_stats if s['win_rate'] < 40 and s['total'] >= 10]
    short_worst_months = [s['month'] for s in short_month_stats if s['win_rate'] < 35]
    
    print(f"✅ Trade SHORT When:")
    if short_best_days:
        print(f"   Days: {', '.join(short_best_days)}")
    if short_best_hours:
        print(f"   Hours: {', '.join([f'{h:02d}:00' for h in short_best_hours])} UTC")
    if short_best_coins:
        print(f"   Coins: {', '.join(short_best_coins)}")
    if short_best_months:
        print(f"   Months: {', '.join(short_best_months)}")
    print()
    
    print(f"🚫 Avoid SHORT When:")
    if short_worst_days:
        print(f"   Days: {', '.join(short_worst_days)}")
    if short_worst_months:
        print(f"   Months: {', '.join(short_worst_months)}")
    print()
    
    # Apply filters and show improvement
    if short_best_days and short_best_hours:
        short_filtered_df = short_analyzer.apply_filters(days=short_best_days, hours=short_best_hours)
        short_filtered_analyzer = BacktestAnalyzer(short_filtered_df) if len(short_filtered_df) > 0 else None
        
        if short_filtered_analyzer:
            short_filtered_stats = short_filtered_analyzer.get_overall_stats()
            short_improvement = short_filtered_stats['win_rate'] - short_stats['win_rate']
            
            print(f"📊 FILTERED PERFORMANCE:")
            print(f"   Signals: {short_filtered_stats['total']} ({short_filtered_stats['total']/short_stats['total']*100:.1f}% of SHORT signals)")
            print(f"   Win Rate: {short_filtered_stats['win_rate']:.1f}%")
            print(f"   Improvement: +{short_improvement:.1f}%")
            print()
else:
    print("No SHORT signals found")
    short_best_days = []
    short_best_hours = []
    short_best_coins = []
    short_best_months = []
    short_worst_days = []
    short_worst_months = []

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
    'short_wr': float(short_stats['win_rate']) if short_analyzer else 0,
    'long_best_days': best_days if long_analyzer else [],
    'long_best_hours': best_hours if long_analyzer else [],
    'long_best_coins': best_coins if long_analyzer else [],
    'long_best_months': best_months if long_analyzer else [],
    'long_worst_days': worst_days if long_analyzer else [],
    'long_worst_months': worst_months if long_analyzer else [],
    'short_best_days': short_best_days if short_analyzer else [],
    'short_best_hours': short_best_hours if short_analyzer else [],
    'short_best_coins': short_best_coins if short_analyzer else [],
    'short_best_months': short_best_months if short_analyzer else [],
    'short_worst_days': short_worst_days if short_analyzer else [],
    'short_worst_months': short_worst_months if short_analyzer else [],
    'filtered_long_wr': float(filtered_stats['win_rate']) if long_analyzer and filtered_analyzer else 0,
    'filtered_long_signals': filtered_stats['total'] if long_analyzer and filtered_analyzer else 0,
    'filtered_short_wr': float(short_filtered_stats['win_rate']) if short_analyzer and short_filtered_analyzer else 0,
    'filtered_short_signals': short_filtered_stats['total'] if short_analyzer and short_filtered_analyzer else 0,
}

# Create output filename based on input file
output_dir = Path('data/analysis')
output_dir.mkdir(parents=True, exist_ok=True)

output_filename = 'long_short_optimization_results.json'
if len(sys.argv) > 1:
    # Extract base name from input file
    input_base = Path(sys.argv[1]).stem.replace('_backtest_detailed', '')
    output_filename = f'long_short_optimization_{input_base}.json'

output_path = output_dir / output_filename

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print("=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print()
print(f"📝 Results saved to: {output_path}")
print()
print("🔄 NEXT STEPS:")
print("1. Use LONG rules for entry when signal direction is LONG")
print("2. Use SHORT rules for entry when signal direction is SHORT")
print("3. Monitor performance and adjust filters based on ongoing results")
