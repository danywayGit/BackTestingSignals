"""
Compare October 13 Baseline with November 4 Results - Refactored
Analyzes improvements and changes between two backtest runs
Uses BacktestAnalyzer class to eliminate code duplication
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from analytics.backtest_analyzer import BacktestAnalyzer

def compare_backtests():
    """Compare October and November backtest results"""
    
    results_dir = Path('data/backtest_results')
    
    # October 13 baseline (989 signals, LONG only)
    october_file = results_dir / 'meta_signals_backtest_detailed_20251013_195515.csv'
    
    # November 4 results (1139 signals, LONG + SHORT)
    november_file = results_dir / 'meta_signals_backtest_detailed_20251104_031305.csv'
    
    print("=" * 80)
    print("📊 OCTOBER 13 vs NOVEMBER 4 COMPARISON")
    print("=" * 80)
    print()
    
    # Load data and create analyzers
    oct_df = pd.read_csv(october_file)
    nov_df = pd.read_csv(november_file)
    
    oct_analyzer = BacktestAnalyzer(oct_df)
    nov_analyzer = BacktestAnalyzer(nov_df)
    
    # Get overall stats
    oct_stats = oct_analyzer.get_overall_stats()
    nov_stats = nov_analyzer.get_overall_stats()
    
    # Get date ranges
    oct_df_parsed = oct_analyzer.df
    nov_df_parsed = nov_analyzer.df
    
    # Basic dataset comparison
    print("📅 DATASET OVERVIEW")
    print("-" * 80)
    print(f"October 13 Baseline:")
    print(f"  Date Range: {oct_df_parsed['signal_time'].min().date()} to {oct_df_parsed['signal_time'].max().date()}")
    print(f"  Total Signals: {oct_stats['total']:,}")
    
    oct_long = oct_analyzer.filter_by_action('LONG')
    oct_short = oct_analyzer.filter_by_action('SHORT')
    print(f"  LONG: {len(oct_long):,}")
    print(f"  SHORT: {len(oct_short):,}")
    print()
    
    print(f"November 4 Results:")
    print(f"  Date Range: {nov_df_parsed['signal_time'].min().date()} to {nov_df_parsed['signal_time'].max().date()}")
    print(f"  Total Signals: {nov_stats['total']:,}")
    
    nov_long = nov_analyzer.filter_by_action('LONG')
    nov_short = nov_analyzer.filter_by_action('SHORT')
    print(f"  LONG: {len(nov_long):,}")
    print(f"  SHORT: {len(nov_short):,}")
    print()
    
    print(f"💡 Change: +{nov_stats['total'] - oct_stats['total']} signals (+{(nov_stats['total'] - oct_stats['total'])/oct_stats['total']*100:.1f}%)")
    print(f"   NEW SHORT signals: {len(nov_short)}")
    print()
    
    # Overall performance comparison
    print("=" * 80)
    print("📊 OVERALL PERFORMANCE COMPARISON")
    print("=" * 80)
    
    print(f"\n{'Metric':<25} {'October 13':<20} {'November 4':<20} {'Change'}")
    print("-" * 80)
    print(f"{'Win Rate':<25} {oct_stats['win_rate']:>6.1f}% ({oct_stats['wins']}/{oct_stats['total']})  {nov_stats['win_rate']:>6.1f}% ({nov_stats['wins']}/{nov_stats['total']})  {nov_stats['win_rate'] - oct_stats['win_rate']:>+6.1f}%")
    print(f"{'Total Wins':<25} {oct_stats['wins']:>18,}  {nov_stats['wins']:>18,}  {nov_stats['wins'] - oct_stats['wins']:>+6,}")
    print(f"{'Total Losses':<25} {oct_stats['losses']:>18,}  {nov_stats['losses']:>18,}  {nov_stats['losses'] - oct_stats['losses']:>+6,}")
    
    # LONG-only comparison (apples to apples)
    print("\n" + "=" * 80)
    print("🔵 LONG SIGNALS COMPARISON (Apples-to-Apples)")
    print("=" * 80)
    
    oct_long_analyzer = BacktestAnalyzer(oct_long) if len(oct_long) > 0 else None
    nov_long_analyzer = BacktestAnalyzer(nov_long) if len(nov_long) > 0 else None
    
    if oct_long_analyzer and nov_long_analyzer:
        oct_long_stats = oct_long_analyzer.get_overall_stats()
        nov_long_stats = nov_long_analyzer.get_overall_stats()
        
        print(f"\n{'Metric':<25} {'October 13':<20} {'November 4':<20} {'Change'}")
        print("-" * 80)
        print(f"{'LONG Signals':<25} {oct_long_stats['total']:>18,}  {nov_long_stats['total']:>18,}  {nov_long_stats['total'] - oct_long_stats['total']:>+6,}")
        print(f"{'LONG Win Rate':<25} {oct_long_stats['win_rate']:>17.1f}%  {nov_long_stats['win_rate']:>17.1f}%  {nov_long_stats['win_rate'] - oct_long_stats['win_rate']:>+6.1f}%")
        print(f"{'LONG Wins':<25} {oct_long_stats['wins']:>18,}  {nov_long_stats['wins']:>18,}  {nov_long_stats['wins'] - oct_long_stats['wins']:>+6,}")
    
    # Top coins comparison
    print("\n" + "=" * 80)
    print("🪙 TOP PERFORMING COINS COMPARISON")
    print("=" * 80)
    
    oct_coins = oct_analyzer.analyze_by_coin(min_signals=10)
    nov_coins = nov_analyzer.analyze_by_coin(min_signals=10)
    
    oct_coins_top = sorted(oct_coins, key=lambda x: x['win_rate'], reverse=True)[:10]
    nov_coins_top = sorted(nov_coins, key=lambda x: x['win_rate'], reverse=True)[:10]
    
    print("\n📈 OCTOBER 13 TOP 10 COINS (10+ signals):")
    for coin in oct_coins_top:
        print(f"  {coin['symbol']:<10} {coin['win_rate']:>5.1f}% ({coin['wins']}/{coin['total']})")
    
    print("\n📈 NOVEMBER 4 TOP 10 COINS (10+ signals):")
    for coin in nov_coins_top:
        print(f"  {coin['symbol']:<10} {coin['win_rate']:>5.1f}% ({coin['wins']}/{coin['total']})")
    
    # Find coins with significant changes
    print("\n" + "=" * 80)
    print("📊 COINS WITH SIGNIFICANT CHANGES (10+ signals in both)")
    print("=" * 80)
    
    oct_coins_dict = {c['symbol']: c['win_rate'] for c in oct_coins}
    nov_coins_dict = {c['symbol']: c['win_rate'] for c in nov_coins}
    
    common_coins = set(oct_coins_dict.keys()) & set(nov_coins_dict.keys())
    
    changes = []
    for coin in common_coins:
        change = nov_coins_dict[coin] - oct_coins_dict[coin]
        changes.append({
            'coin': coin,
            'oct_wr': oct_coins_dict[coin],
            'nov_wr': nov_coins_dict[coin],
            'change': change
        })
    
    changes.sort(key=lambda x: abs(x['change']), reverse=True)
    
    if changes:
        print("\n🔼 BIGGEST IMPROVEMENTS:")
        improvements = [c for c in changes if c['change'] > 5][:5]
        if improvements:
            for c in improvements:
                print(f"  {c['coin']:<10} {c['oct_wr']:>5.1f}% → {c['nov_wr']:>5.1f}% (+{c['change']:>5.1f}%)")
        else:
            print("  No significant improvements >5%")
        
        print("\n🔽 BIGGEST DECLINES:")
        declines = [c for c in changes if c['change'] < -5][:5]
        if declines:
            for c in declines:
                print(f"  {c['coin']:<10} {c['oct_wr']:>5.1f}% → {c['nov_wr']:>5.1f}% ({c['change']:>5.1f}%)")
        else:
            print("  No significant declines >5%")
    
    # Time-based comparison
    print("\n" + "=" * 80)
    print("⏰ BEST HOURS COMPARISON")
    print("=" * 80)
    
    oct_hours = oct_analyzer.analyze_by_hour()
    nov_hours = nov_analyzer.analyze_by_hour()
    
    oct_hours_top = sorted(oct_hours, key=lambda x: x['win_rate'], reverse=True)[:5]
    nov_hours_top = sorted(nov_hours, key=lambda x: x['win_rate'], reverse=True)[:5]
    
    print("\n📈 OCTOBER 13 TOP 5 HOURS:")
    for hour in oct_hours_top:
        print(f"  {hour['hour']:02d}:00 UTC: {hour['win_rate']:>5.1f}%")
    
    print("\n📈 NOVEMBER 4 TOP 5 HOURS:")
    for hour in nov_hours_top:
        print(f"  {hour['hour']:02d}:00 UTC: {hour['win_rate']:>5.1f}%")
    
    # Key findings
    print("\n" + "=" * 80)
    print("🎯 KEY FINDINGS & RECOMMENDATIONS")
    print("=" * 80)
    
    wr_change = nov_stats['win_rate'] - oct_stats['win_rate']
    
    print(f"\n1. OVERALL QUALITY:")
    if wr_change > 0:
        print(f"   ✅ Signal quality IMPROVED by {wr_change:.1f}%")
    elif wr_change < 0:
        print(f"   ⚠️  Signal quality DECLINED by {abs(wr_change):.1f}%")
    else:
        print(f"   ⚪ Signal quality UNCHANGED")
    
    if oct_long_analyzer and nov_long_analyzer:
        long_wr_change = nov_long_stats['win_rate'] - oct_long_stats['win_rate']
        print(f"\n2. LONG SIGNALS:")
        if long_wr_change > 0:
            print(f"   ✅ LONG performance IMPROVED by {long_wr_change:.1f}%")
        elif long_wr_change < 0:
            print(f"   ⚠️  LONG performance DECLINED by {abs(long_wr_change):.1f}%")
        else:
            print(f"   ⚪ LONG performance UNCHANGED")
    
    print(f"\n3. SHORT SIGNALS:")
    if len(nov_short) > 0:
        nov_short_analyzer = BacktestAnalyzer(nov_short)
        short_stats = nov_short_analyzer.get_overall_stats()
        print(f"   📊 {short_stats['total']} SHORT signals added with {short_stats['win_rate']:.1f}% WR")
        if short_stats['win_rate'] > 50:
            print(f"   ✅ SHORT signals are PROFITABLE")
        else:
            print(f"   ⚠️  SHORT signals need optimization")
    
    print(f"\n4. DATA VOLUME:")
    print(f"   📈 +{nov_stats['total'] - oct_stats['total']} signals ({(nov_stats['total'] - oct_stats['total'])/oct_stats['total']*100:.1f}% increase)")
    print(f"   💡 More data = better statistical confidence")
    
    print("\n" + "=" * 80)
    print("✅ Comparison Complete!")
    print("=" * 80)

if __name__ == "__main__":
    compare_backtests()
