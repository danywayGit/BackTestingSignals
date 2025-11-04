"""
Compare Signal Sources Analysis

Comprehensive comparison between different signal sources (Telegram vs Discord).
Compares overall performance, LONG/SHORT metrics, and optimal patterns.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("⚖️  SIGNAL SOURCES COMPARISON")
print("=" * 80)
print()

# Load both analysis results
telegram_file = 'long_short_optimization_meta_signals_20251104_050221.json'
discord_file = 'long_short_optimization_meta_signals_20251104_031305.json'

try:
    with open(telegram_file, 'r') as f:
        telegram = json.load(f)
    print(f"✅ Loaded Telegram analysis: {telegram_file}")
except FileNotFoundError:
    print(f"❌ Telegram analysis not found: {telegram_file}")
    sys.exit(1)

try:
    with open(discord_file, 'r') as f:
        discord = json.load(f)
    print(f"✅ Loaded Discord analysis: {discord_file}")
except FileNotFoundError:
    print(f"❌ Discord analysis not found: {discord_file}")
    sys.exit(1)

print()

def print_comparison(metric, telegram_val, discord_val, higher_is_better=True, is_percentage=False, decimal_places=1):
    """Print a comparison row with winner indication"""
    format_str = f"{{:.{decimal_places}f}}"
    
    if is_percentage:
        tg_str = f"{format_str.format(telegram_val)}%"
        dc_str = f"{format_str.format(discord_val)}%"
    else:
        tg_str = str(telegram_val)
        dc_str = str(discord_val)
    
    # Determine winner
    if telegram_val == discord_val:
        winner = "TIE"
        tg_icon = "⚖️ "
        dc_icon = "⚖️ "
    elif (telegram_val > discord_val and higher_is_better) or (telegram_val < discord_val and not higher_is_better):
        winner = "TELEGRAM"
        tg_icon = "🏆 "
        dc_icon = "   "
    else:
        winner = "DISCORD"
        tg_icon = "   "
        dc_icon = "🏆 "
    
    print(f"{metric:<30} | {tg_icon}{tg_str:<12} | {dc_icon}{dc_str:<12}")

print("=" * 80)
print("📊 OVERALL PERFORMANCE")
print("=" * 80)
print(f"{'Metric':<30} | {'Telegram (DT)':<15} | {'Discord (MS)':<15}")
print("-" * 80)

print_comparison("Total Signals", telegram['total_signals'], discord['total_signals'], higher_is_better=True, is_percentage=False)
print_comparison("LONG Signals", telegram['long_signals'], discord['long_signals'], higher_is_better=True, is_percentage=False)
print_comparison("SHORT Signals", telegram['short_signals'], discord['short_signals'], higher_is_better=True, is_percentage=False)
print()
print_comparison("Overall Win Rate", 
                (telegram['long_signals']*telegram['long_wr'] + telegram['short_signals']*telegram['short_wr']) / telegram['total_signals'],
                (discord['long_signals']*discord['long_wr'] + discord['short_signals']*discord['short_wr']) / discord['total_signals'],
                higher_is_better=True, is_percentage=True)
print()

print("=" * 80)
print("📈 LONG SIGNALS COMPARISON")
print("=" * 80)
print(f"{'Metric':<30} | {'Telegram (DT)':<15} | {'Discord (MS)':<15}")
print("-" * 80)

print_comparison("LONG Win Rate", telegram['long_wr'], discord['long_wr'], higher_is_better=True, is_percentage=True)
print_comparison("Filtered LONG WR", telegram['filtered_long_wr'], discord['filtered_long_wr'], higher_is_better=True, is_percentage=True)
print_comparison("Filtered LONG Signals", telegram['filtered_long_signals'], discord['filtered_long_signals'], higher_is_better=True, is_percentage=False)
print_comparison("Filtered % of Total", 
                (telegram['filtered_long_signals'] / telegram['long_signals'] * 100) if telegram['long_signals'] > 0 else 0,
                (discord['filtered_long_signals'] / discord['long_signals'] * 100) if discord['long_signals'] > 0 else 0,
                higher_is_better=False, is_percentage=True)
print()

print("LONG Best Days:")
print(f"  Telegram: {', '.join(telegram['long_best_days'][:3])}")
print(f"  Discord:  {', '.join(discord['long_best_days'][:3])}")
print()

print("LONG Best Hours (UTC):")
tg_hours = ', '.join([f"{h:02d}:00" for h in telegram['long_best_hours'][:5]])
dc_hours = ', '.join([f"{h:02d}:00" for h in discord['long_best_hours'][:5]])
print(f"  Telegram: {tg_hours}")
print(f"  Discord:  {dc_hours}")
print()

print("LONG Best Coins:")
print(f"  Telegram: {', '.join(telegram['long_best_coins'][:5])}")
print(f"  Discord:  {', '.join(discord['long_best_coins'][:5])}")
print()

print("LONG Best Months:")
print(f"  Telegram: {', '.join(telegram['long_best_months'][:5])}")
print(f"  Discord:  {', '.join(discord['long_best_months'][:5])}")
print()

print("=" * 80)
print("📉 SHORT SIGNALS COMPARISON")
print("=" * 80)
print(f"{'Metric':<30} | {'Telegram (DT)':<15} | {'Discord (MS)':<15}")
print("-" * 80)

print_comparison("SHORT Win Rate", telegram['short_wr'], discord['short_wr'], higher_is_better=True, is_percentage=True)
print_comparison("Filtered SHORT WR", telegram['filtered_short_wr'], discord['filtered_short_wr'], higher_is_better=True, is_percentage=True)
print_comparison("Filtered SHORT Signals", telegram['filtered_short_signals'], discord['filtered_short_signals'], higher_is_better=True, is_percentage=False)
print_comparison("Filtered % of Total", 
                (telegram['filtered_short_signals'] / telegram['short_signals'] * 100) if telegram['short_signals'] > 0 else 0,
                (discord['filtered_short_signals'] / discord['short_signals'] * 100) if discord['short_signals'] > 0 else 0,
                higher_is_better=False, is_percentage=True)
print()

print("SHORT Best Days:")
print(f"  Telegram: {', '.join(telegram['short_best_days'][:3])}")
print(f"  Discord:  {', '.join(discord['short_best_days'][:3])}")
print()

print("SHORT Best Hours (UTC):")
tg_hours = ', '.join([f"{h:02d}:00" for h in telegram['short_best_hours'][:5]])
dc_hours = ', '.join([f"{h:02d}:00" for h in discord['short_best_hours'][:5]])
print(f"  Telegram: {tg_hours}")
print(f"  Discord:  {dc_hours}")
print()

print("SHORT Best Coins:")
tg_short_coins = telegram.get('short_best_coins', [])
dc_short_coins = discord.get('short_best_coins', [])
print(f"  Telegram: {', '.join(tg_short_coins[:5]) if tg_short_coins else 'N/A'}")
print(f"  Discord:  {', '.join(dc_short_coins[:5]) if dc_short_coins else 'N/A'}")
print()

print("SHORT Best Months:")
print(f"  Telegram: {', '.join(telegram['short_best_months'][:5])}")
print(f"  Discord:  {', '.join(discord['short_best_months'][:5])}")
print()

print("=" * 80)
print("🎯 KEY INSIGHTS")
print("=" * 80)

# Calculate winners
long_winner = "Telegram" if telegram['long_wr'] > discord['long_wr'] else "Discord"
short_winner = "Telegram" if telegram['short_wr'] > discord['short_wr'] else "Discord"
volume_winner = "Discord" if discord['total_signals'] > telegram['total_signals'] else "Telegram"
filtered_long_winner = "Telegram" if telegram['filtered_long_wr'] > discord['filtered_long_wr'] else "Discord"
filtered_short_winner = "Telegram" if telegram['filtered_short_wr'] > discord['filtered_short_wr'] else "Discord"

print()
print(f"🏆 LONG Performance Winner: {long_winner}")
print(f"   Telegram: {telegram['long_wr']:.1f}% WR ({telegram['long_signals']} signals)")
print(f"   Discord:  {discord['long_wr']:.1f}% WR ({discord['long_signals']} signals)")
print()

print(f"🏆 SHORT Performance Winner: {short_winner}")
print(f"   Telegram: {telegram['short_wr']:.1f}% WR ({telegram['short_signals']} signals)")
print(f"   Discord:  {discord['short_wr']:.1f}% WR ({discord['short_signals']} signals)")
print()

print(f"🏆 Filtered LONG Winner: {filtered_long_winner}")
print(f"   Telegram: {telegram['filtered_long_wr']:.1f}% WR ({telegram['filtered_long_signals']} signals)")
print(f"   Discord:  {discord['filtered_long_wr']:.1f}% WR ({discord['filtered_long_signals']} signals)")
print()

print(f"🏆 Filtered SHORT Winner: {filtered_short_winner}")
print(f"   Telegram: {telegram['filtered_short_wr']:.1f}% WR ({telegram['filtered_short_signals']} signals)")
print(f"   Discord:  {discord['filtered_short_wr']:.1f}% WR ({discord['filtered_short_signals']} signals)")
print()

print(f"📊 Volume Leader: {volume_winner}")
print(f"   Telegram: {telegram['total_signals']} total signals")
print(f"   Discord:  {discord['total_signals']} total signals")
print()

# Strategy recommendations
print("=" * 80)
print("💡 STRATEGY RECOMMENDATIONS")
print("=" * 80)
print()

print("📈 FOR LONG POSITIONS:")
if telegram['long_wr'] > discord['long_wr']:
    diff = telegram['long_wr'] - discord['long_wr']
    print(f"   ⭐ PREFER TELEGRAM (DaviddTech) - {diff:.1f}% higher win rate")
    print(f"      Best: {', '.join(telegram['long_best_days'][:2])} | {telegram['long_best_coins'][0]}")
else:
    diff = discord['long_wr'] - telegram['long_wr']
    print(f"   ⭐ PREFER DISCORD (Meta Signals) - {diff:.1f}% higher win rate")
    print(f"      Best: {', '.join(discord['long_best_days'][:2])} | {discord['long_best_coins'][0]}")
print()

print("📉 FOR SHORT POSITIONS:")
if telegram['short_wr'] > discord['short_wr']:
    diff = telegram['short_wr'] - discord['short_wr']
    print(f"   ⭐ PREFER TELEGRAM (DaviddTech) - {diff:.1f}% higher win rate")
    print(f"      Best: {', '.join(telegram['short_best_days'][:2])}")
else:
    diff = discord['short_wr'] - telegram['short_wr']
    print(f"   ⭐ PREFER DISCORD (Meta Signals) - {diff:.1f}% higher win rate")
    print(f"      Best: {', '.join(discord['short_best_days'][:2])}")
print()

print("🎯 OPTIMAL STRATEGY:")
print("   1. Use BOTH sources for complementary coverage")
print("   2. Apply source-specific filters for best results")
print("   3. Consider combining signals when both sources agree")
print()

# Day pattern analysis
print("=" * 80)
print("📅 DAY PATTERN COMPARISON")
print("=" * 80)
print()

print("LONG Patterns:")
print(f"  Telegram: Best={', '.join(telegram['long_best_days'][:2])}, Worst={', '.join(telegram['long_worst_days'][:2])}")
print(f"  Discord:  Best={', '.join(discord['long_best_days'][:2])}, Worst={', '.join(discord['long_worst_days'][:2])}")
print()

print("SHORT Patterns:")
print(f"  Telegram: Best={', '.join(telegram['short_best_days'][:2])}, Worst={', '.join(telegram['short_worst_days'][:2])}")
print(f"  Discord:  Best={', '.join(discord['short_best_days'][:2])}, Worst={', '.join(discord['short_worst_days'][:2])}")
print()

# Interesting finding
tg_long_best = set(telegram['long_best_days'][:3])
dc_long_best = set(discord['long_best_days'][:3])
common_long_days = tg_long_best & dc_long_best
if common_long_days:
    print(f"🔥 BOTH AGREE - Best LONG Days: {', '.join(common_long_days)}")
else:
    print("⚠️  NO AGREEMENT - Sources have different LONG day patterns")
print()

tg_short_best = set(telegram['short_best_days'][:3])
dc_short_best = set(discord['short_best_days'][:3])
common_short_days = tg_short_best & dc_short_best
if common_short_days:
    print(f"🔥 BOTH AGREE - Best SHORT Days: {', '.join(common_short_days)}")
else:
    print("⚠️  NO AGREEMENT - Sources have different SHORT day patterns")
print()

print("=" * 80)
print("✅ COMPARISON COMPLETE")
print("=" * 80)
print()

# Save comparison results
comparison_output = {
    'comparison_date': datetime.now().isoformat(),
    'sources': {
        'telegram': {
            'file': telegram_file,
            'total_signals': telegram['total_signals'],
            'long_wr': telegram['long_wr'],
            'short_wr': telegram['short_wr'],
            'filtered_long_wr': telegram['filtered_long_wr'],
            'filtered_short_wr': telegram['filtered_short_wr']
        },
        'discord': {
            'file': discord_file,
            'total_signals': discord['total_signals'],
            'long_wr': discord['long_wr'],
            'short_wr': discord['short_wr'],
            'filtered_long_wr': discord['filtered_long_wr'],
            'filtered_short_wr': discord['filtered_short_wr']
        }
    },
    'winners': {
        'long_performance': long_winner,
        'short_performance': short_winner,
        'filtered_long': filtered_long_winner,
        'filtered_short': filtered_short_winner,
        'volume': volume_winner
    },
    'common_patterns': {
        'long_best_days': list(common_long_days) if common_long_days else [],
        'short_best_days': list(common_short_days) if common_short_days else []
    }
}

output_file = 'source_comparison_results.json'
with open(output_file, 'w') as f:
    json.dump(comparison_output, f, indent=2)

print(f"📝 Comparison saved to: {output_file}")
