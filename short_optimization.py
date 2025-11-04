"""
SHORT Signal Optimization Analysis (Refactored)
Uses shared BacktestAnalyzer to avoid code duplication
"""

import json
import sys
from datetime import datetime
from src.analytics import BacktestAnalyzer, load_latest_backtest

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load latest backtest results
df = load_latest_backtest()

# Filter for SHORT signals only
short_df = df[df['action'] == 'SHORT'].copy()

# Initialize analyzer
analyzer = BacktestAnalyzer(short_df)

print("="*80)
print("🔻 SHORT SIGNALS OPTIMIZATION ANALYSIS")
print("="*80)

# Overall stats
overall = analyzer.get_overall_stats()
print(f"\n📊 Dataset: {overall['total']} SHORT signals")
print(f"Overall SHORT Win Rate: {overall['win_rate']:.1f}%")
print(f"Wins: {overall['wins']} | Losses: {overall['losses']}")
print("="*80)

# Analysis results storage
analysis_results = {
    'timestamp': datetime.now().isoformat(),
    'total_short_signals': overall['total'],
    'overall_short_wr': overall['win_rate'] / 100,
    'overall_short_wins': overall['wins'],
    'overall_short_losses': overall['losses'],
}

# ============================================================================
# 1. DAY OF WEEK ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📅 SHORT PERFORMANCE BY DAY OF WEEK")
print("="*80)

day_stats = analyzer.analyze_by_day_of_week()
for day in day_stats:
    emoji = "✅" if day['win_rate'] > 48 else "⚠️" if day['win_rate'] > 42 else "❌"
    print(f"{emoji} {day['day']:9s}: {day['win_rate']:5.1f}% WR ({day['wins']:3d}/{day['total']:3d}) | "
          f"Avg Profit: {day['avg_profit']:5.2f}% | Avg Loss: {day['avg_loss']:5.2f}% | PF: {day['profit_factor']:.2f}")

analysis_results['by_day'] = day_stats

# ============================================================================
# 2. HOUR OF DAY ANALYSIS (UTC)
# ============================================================================
print("\n" + "="*80)
print("⏰ SHORT PERFORMANCE BY HOUR (UTC)")
print("="*80)

hour_stats = analyzer.analyze_by_hour(min_signals=5)
overall_wr = overall['win_rate']

for hour in hour_stats:
    diff_vs_baseline = hour['win_rate'] - overall_wr
    
    if hour['win_rate'] > 55:
        emoji = "🌟"
    elif hour['win_rate'] > 48:
        emoji = "✅"
    elif hour['win_rate'] > 42:
        emoji = "⚠️"
    else:
        emoji = "❌"
    
    print(f"{emoji} {hour['hour']:02d}:00: {hour['win_rate']:5.1f}% WR ({hour['wins']:2d}/{hour['total']:2d}) | "
          f"PF: {hour['profit_factor']:.2f} | vs Baseline: {diff_vs_baseline:+5.1f}%")

# Top 5 hours
print(f"\n🏆 TOP 5 SHORT HOURS:")
top_hours = analyzer.get_best_performers('hour', top_n=5, min_signals=5)
for i, h in enumerate(top_hours, 1):
    print(f"{i}. {h['hour']:02d}:00 UTC: {h['win_rate']:.1f}% WR ({h['wins']}/{h['total']}) PF: {h['profit_factor']:.2f}")

analysis_results['by_hour'] = hour_stats

# ============================================================================
# 3. COIN PERFORMANCE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("🪙 SHORT PERFORMANCE BY COIN")
print("="*80)

coin_stats = analyzer.analyze_by_coin(min_signals=3)

print(f"\n🏆 TOP SHORT COINS (sorted by WR, then signal count):")
for i, coin in enumerate(coin_stats[:15], 1):
    emoji = "🌟" if coin['win_rate'] > 65 else "✅" if coin['win_rate'] > 55 else "⚠️"
    pf_str = "inf" if coin['profit_factor'] == float('inf') else f"{coin['profit_factor']:.2f}"
    print(f"{emoji} {i:2d}. {coin['symbol']:<6s}: {coin['win_rate']:5.1f}% WR ({coin['wins']:2d}/{coin['total']:2d}) | "
          f"Avg Profit: {coin['avg_profit']:5.2f}% | PF: {pf_str}")

analysis_results['by_coin'] = coin_stats

# ============================================================================
# 4. MONTH PERFORMANCE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📆 SHORT PERFORMANCE BY MONTH")
print("="*80)

month_stats = analyzer.analyze_by_month()
for month in month_stats:
    emoji = "✅" if month['win_rate'] > 48 else "⚠️" if month['win_rate'] > 42 else "❌"
    print(f"{emoji} {month['month']:9s}: {month['win_rate']:5.1f}% WR ({month['wins']:3d}/{month['total']:3d}) | "
          f"Avg Profit: {month['avg_profit']:5.2f}% | PF: {month['profit_factor']:.2f}")

analysis_results['by_month'] = month_stats

# ============================================================================
# 5. PERFECT COMBINATIONS
# ============================================================================
print("\n" + "="*80)
print("🎯 PERFECT SHORT COMBINATIONS (100% Win Rate with 3+ signals)")
print("="*80)

day_hour_combos, day_coin_combos = analyzer.find_perfect_combinations(min_signals=3)

if day_hour_combos:
    for combo in day_hour_combos:
        print(f"🌟 {combo['day']} at {combo['hour']:02d}:00: {combo['wins']}/{combo['signals']} wins | "
              f"Avg Profit: {combo['avg_profit']:.2f}%")
else:
    print("No perfect day+hour combinations found.")

# ============================================================================
# 6. OPTIMIZED STRATEGY
# ============================================================================
print("\n" + "="*80)
print("🎯 OPTIMIZED SHORT STRATEGY")
print("="*80)

# Get best performers for filters
best_days = [d['day'] for d in day_stats if d['win_rate'] > overall_wr]
best_hours = [h['hour'] for h in hour_stats if h['win_rate'] > 50 and h['total'] >= 5]
best_coins = [c['symbol'] for c in coin_stats if c['win_rate'] > 55 and c['total'] >= 3]

print(f"\n📋 FILTER CRITERIA:")
print(f"Best Days (>{overall_wr:.0f}% WR): {', '.join(best_days)}")
print(f"Best Hours (>50% WR, 5+ signals): {', '.join([f'{h:02d}:00' for h in best_hours])}")
print(f"Best Coins (>55% WR, 3+ signals): {', '.join(best_coins)}")

# Apply progressive filters
tier1 = analyzer.apply_filters(days=best_days)
tier1_stats = analyzer.get_overall_stats(tier1)

tier2 = analyzer.apply_filters(days=best_days, hours=best_hours)
tier2_stats = analyzer.get_overall_stats(tier2)

tier3 = analyzer.apply_filters(coins=best_coins)
tier3_stats = analyzer.get_overall_stats(tier3)

tier4 = analyzer.apply_filters(days=best_days, coins=best_coins)
tier4_stats = analyzer.get_overall_stats(tier4)

tier5 = analyzer.apply_filters(days=best_days, hours=best_hours, coins=best_coins)
tier5_stats = analyzer.get_overall_stats(tier5)

print(f"\n✅ Filter 1 - Best Days: {tier1_stats['win_rate']:.1f}% WR ({tier1_stats['wins']}/{tier1_stats['total']}) - {tier1_stats['total']/overall['total']*100:.1f}% of signals")
print(f"✅ Filter 2 - Best Days + Hours: {tier2_stats['win_rate']:.1f}% WR ({tier2_stats['wins']}/{tier2_stats['total']}) - {tier2_stats['total']/overall['total']*100:.1f}% of signals")
print(f"✅ Filter 3 - Best Coins: {tier3_stats['win_rate']:.1f}% WR ({tier3_stats['wins']}/{tier3_stats['total']}) - {tier3_stats['total']/overall['total']*100:.1f}% of signals")
print(f"✅ Filter 4 - Best Days + Coins: {tier4_stats['win_rate']:.1f}% WR ({tier4_stats['wins']}/{tier4_stats['total']}) - {tier4_stats['total']/overall['total']*100:.1f}% of signals")
print(f"✅ Filter 5 - Ultra-Filtered: {tier5_stats['win_rate']:.1f}% WR ({tier5_stats['wins']}/{tier5_stats['total']}) - {tier5_stats['total']/overall['total']*100:.1f}% of signals")

analysis_results['strategy_tiers'] = {
    'tier1_best_days': tier1_stats,
    'tier2_days_hours': tier2_stats,
    'tier3_best_coins': tier3_stats,
    'tier4_days_coins': tier4_stats,
    'tier5_ultra_filtered': tier5_stats
}

# ============================================================================
# 7. WORST PERFORMERS - AVOID THESE
# ============================================================================
print("\n" + "="*80)
print("❌ WORST SHORT PERFORMERS - AVOID THESE")
print("="*80)

worst_days = analyzer.get_worst_performers('day', bottom_n=3)
print(f"\n📅 Worst Days:")
for day in worst_days:
    print(f"❌ {day['day']:9s}: {day['win_rate']:5.1f}% WR ({day['wins']}/{day['total']})")

worst_hours = analyzer.get_worst_performers('hour', bottom_n=5, min_signals=5)
print(f"\n⏰ Worst Hours (with 5+ signals):")
for hour in worst_hours:
    print(f"❌ {hour['hour']:02d}:00: {hour['win_rate']:5.1f}% WR ({hour['wins']}/{hour['total']})")

worst_coins = analyzer.get_worst_performers('coin', bottom_n=10, min_signals=3)
print(f"\n🪙 Worst Coins (with 3+ signals):")
for coin in worst_coins:
    print(f"❌ {coin['symbol']:<6s}: {coin['win_rate']:5.1f}% WR ({coin['wins']}/{coin['total']})")

worst_months = analyzer.get_worst_performers('month', bottom_n=3)
print(f"\n📆 Worst Months:")
for month in worst_months:
    print(f"❌ {month['month']:9s}: {month['win_rate']:5.1f}% WR ({month['wins']}/{month['total']})")

# Save results
output_file = 'short_optimization_results.json'
with open(output_file, 'w') as f:
    json.dump(analysis_results, f, indent=2, default=str)

print(f"\n✅ Analysis complete! Results saved to {output_file}")
print("="*80)
