"""
Compare LONG vs SHORT Performance Patterns - Refactored
Analyzes differences between LONG and SHORT signals across multiple dimensions
Uses BacktestAnalyzer class to eliminate code duplication
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from src.analytics.backtest_analyzer import BacktestAnalyzer

def compare_long_short():
    """Compare LONG vs SHORT performance patterns"""
    
    # Find latest backtest results
    results_dir = Path('data/backtest_results')
    detailed_files = sorted(results_dir.glob('meta_signals_backtest_detailed_*.csv'))
    
    if not detailed_files:
        print("❌ No backtest results found!")
        return
    
    latest_file = detailed_files[-1]
    
    print("=" * 80)
    print("🔄 LONG vs SHORT COMPREHENSIVE COMPARISON")
    print("=" * 80)
    print(f"📂 Analyzing: {latest_file.name}\n")
    
    # Load data and create main analyzer
    df = pd.read_csv(latest_file)
    analyzer = BacktestAnalyzer(df)
    
    # Get overall stats
    overall = analyzer.get_overall_stats()
    
    # Separate LONG and SHORT
    long_df = analyzer.filter_by_action('LONG')
    short_df = analyzer.filter_by_action('SHORT')
    
    long_analyzer = BacktestAnalyzer(long_df) if len(long_df) > 0 else None
    short_analyzer = BacktestAnalyzer(short_df) if len(short_df) > 0 else None
    
    print(f"📊 DATASET OVERVIEW")
    print(f"   Total Signals: {overall['total']:,}")
    print(f"   LONG Signals: {len(long_df):,} ({len(long_df)/overall['total']*100:.1f}%)")
    print(f"   SHORT Signals: {len(short_df):,} ({len(short_df)/overall['total']*100:.1f}%)")
    print()
    
    # Overall performance comparison
    print("=" * 80)
    print("📊 OVERALL PERFORMANCE COMPARISON")
    print("=" * 80)
    
    comparison = []
    
    for action, action_analyzer in [('LONG', long_analyzer), ('SHORT', short_analyzer)]:
        if action_analyzer:
            stats = action_analyzer.get_overall_stats()
            
            print(f"\n{action}:")
            print(f"  Win Rate: {stats['win_rate']:.1f}% ({stats['wins']}/{stats['total']})")
            print(f"  Wins: {stats['wins']} | Losses: {stats['losses']}")
            print(f"  Profit Factor: {stats['profit_factor']:.2f}")
            
            comparison.append({
                'action': action,
                'win_rate': stats['win_rate'],
                'wins': stats['wins'],
                'losses': stats['losses'],
                'total': stats['total'],
                'profit_factor': stats['profit_factor']
            })
    
    if len(comparison) == 2:
        print(f"\n💡 Difference: {comparison[0]['action']} performs {comparison[0]['win_rate'] - comparison[1]['win_rate']:.1f}% better")
    
    # Day of week comparison
    print("\n" + "=" * 80)
    print("📅 PERFORMANCE BY DAY OF WEEK")
    print("=" * 80)
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    long_day_stats = {s['day']: s for s in long_analyzer.analyze_by_day_of_week()} if long_analyzer else {}
    short_day_stats = {s['day']: s for s in short_analyzer.analyze_by_day_of_week()} if short_analyzer else {}
    
    print(f"\n{'Day':<12} {'LONG WR':<15} {'SHORT WR':<15} {'Best For':<12} {'Difference'}")
    print("-" * 80)
    
    day_comparison = []
    
    for day in day_order:
        long_stat = long_day_stats.get(day, {'win_rate': 0, 'total': 0})
        short_stat = short_day_stats.get(day, {'win_rate': 0, 'total': 0})
        
        long_wr = long_stat['win_rate']
        short_wr = short_stat['win_rate']
        long_count = long_stat['total']
        short_count = short_stat['total']
        
        best = "LONG" if long_wr > short_wr else "SHORT" if short_wr > long_wr else "TIE"
        diff = abs(long_wr - short_wr)
        
        indicator = "🔵" if best == "LONG" else "🔴" if best == "SHORT" else "⚪"
        
        print(f"{indicator} {day:<10} {long_wr:>5.1f}% ({long_count:>3}) {short_wr:>5.1f}% ({short_count:>3}) {best:<12} {diff:>5.1f}%")
        
        day_comparison.append({
            'day': day,
            'long_wr': long_wr,
            'long_count': long_count,
            'short_wr': short_wr,
            'short_count': short_count,
            'best': best,
            'difference': diff
        })
    
    # Hour comparison
    print("\n" + "=" * 80)
    print("⏰ PERFORMANCE BY HOUR (UTC)")
    print("=" * 80)
    
    long_hour_stats = {s['hour']: s for s in long_analyzer.analyze_by_hour(min_signals=5)} if long_analyzer else {}
    short_hour_stats = {s['hour']: s for s in short_analyzer.analyze_by_hour(min_signals=3)} if short_analyzer else {}
    
    all_hours = sorted(set(long_hour_stats.keys()) | set(short_hour_stats.keys()))
    
    print(f"\n{'Hour':<8} {'LONG WR':<18} {'SHORT WR':<18} {'Best For':<12} {'Difference'}")
    print("-" * 80)
    
    hour_comparison = []
    
    for hour in all_hours:
        long_stat = long_hour_stats.get(hour, {'win_rate': 0, 'total': 0})
        short_stat = short_hour_stats.get(hour, {'win_rate': 0, 'total': 0})
        
        long_wr = long_stat['win_rate']
        short_wr = short_stat['win_rate']
        long_count = long_stat['total']
        short_count = short_stat['total']
        
        best = "LONG" if long_wr > short_wr else "SHORT" if short_wr > long_wr else "TIE"
        diff = abs(long_wr - short_wr)
        
        indicator = "🔵" if best == "LONG" and diff > 10 else "🔴" if best == "SHORT" and diff > 10 else "⚪"
        print(f"{indicator} {hour:02d}:00  {long_wr:>5.1f}% ({long_count:>3}) {short_wr:>6.1f}% ({short_count:>3}) {best:<12} {diff:>5.1f}%")
        
        hour_comparison.append({
            'hour': hour,
            'long_wr': long_wr,
            'long_count': long_count,
            'short_wr': short_wr,
            'short_count': short_count,
            'best': best,
            'difference': diff
        })
    
    # Coin comparison - top 20 by signal count
    print("\n" + "=" * 80)
    print("🪙 PERFORMANCE BY COIN (Top 20 by signal volume)")
    print("=" * 80)
    
    # Get top 20 coins by total signals
    top_coins = df['symbol'].value_counts().head(20).index
    
    long_coin_stats = {s['symbol']: s for s in long_analyzer.analyze_by_coin()} if long_analyzer else {}
    short_coin_stats = {s['symbol']: s for s in short_analyzer.analyze_by_coin()} if short_analyzer else {}
    
    print(f"\n{'Coin':<10} {'LONG WR':<18} {'SHORT WR':<18} {'Best For':<12} {'Difference'}")
    print("-" * 80)
    
    coin_comparison = []
    
    for coin in top_coins:
        long_stat = long_coin_stats.get(coin, {'win_rate': 0, 'total': 0})
        short_stat = short_coin_stats.get(coin, {'win_rate': 0, 'total': 0})
        
        long_wr = long_stat['win_rate']
        short_wr = short_stat['win_rate']
        long_count = long_stat['total']
        short_count = short_stat['total']
        
        if long_count == 0 and short_count == 0:
            continue
        
        best = "LONG" if long_wr > short_wr else "SHORT" if short_wr > long_wr else "TIE"
        diff = abs(long_wr - short_wr)
        
        indicator = "🔵" if best == "LONG" and diff > 15 else "🔴" if best == "SHORT" and diff > 15 else "⚪"
        
        print(f"{indicator} {coin:<8} {long_wr:>5.1f}% ({long_count:>3}) {short_wr:>6.1f}% ({short_count:>3}) {best:<12} {diff:>5.1f}%")
        
        coin_comparison.append({
            'coin': coin,
            'long_wr': long_wr,
            'long_count': long_count,
            'short_wr': short_wr,
            'short_count': short_count,
            'best': best,
            'difference': diff
        })
    
    # Key findings summary
    print("\n" + "=" * 80)
    print("🎯 KEY FINDINGS & RECOMMENDATIONS")
    print("=" * 80)
    
    # Best days for each
    long_best_days = sorted([d for d in day_comparison if d['long_count'] >= 10], 
                           key=lambda x: x['long_wr'], reverse=True)[:3]
    short_best_days = sorted([d for d in day_comparison if d['short_count'] >= 5], 
                            key=lambda x: x['short_wr'], reverse=True)[:3]
    
    print("\n📅 BEST DAYS:")
    if long_best_days:
        long_days_str = ', '.join([f"{d['day']} ({d['long_wr']:.1f}%)" for d in long_best_days])
        print(f"   LONG: {long_days_str}")
    if short_best_days:
        short_days_str = ', '.join([f"{d['day']} ({d['short_wr']:.1f}%)" for d in short_best_days])
        print(f"   SHORT: {short_days_str}")
    
    # Best hours for each
    long_best_hours = sorted([h for h in hour_comparison if h['long_count'] >= 10], 
                            key=lambda x: x['long_wr'], reverse=True)[:3]
    short_best_hours = sorted([h for h in hour_comparison if h['short_count'] >= 5], 
                             key=lambda x: x['short_wr'], reverse=True)[:3]
    
    print("\n⏰ BEST HOURS:")
    if long_best_hours:
        long_hours_str = ', '.join([f"{h['hour']:02d}:00 ({h['long_wr']:.1f}%)" for h in long_best_hours])
        print(f"   LONG: {long_hours_str}")
    if short_best_hours:
        short_hours_str = ', '.join([f"{h['hour']:02d}:00 ({h['short_wr']:.1f}%)" for h in short_best_hours])
        print(f"   SHORT: {short_hours_str}")
    
    # Coins that are significantly better for one type
    long_preferred = [c for c in coin_comparison if c['best'] == 'LONG' and c['difference'] > 15 
                     and c['long_count'] >= 5]
    short_preferred = [c for c in coin_comparison if c['best'] == 'SHORT' and c['difference'] > 15 
                      and c['short_count'] >= 3]
    
    if long_preferred:
        print("\n🔵 LONG-PREFERRED COINS (>15% better):")
        for c in sorted(long_preferred, key=lambda x: x['difference'], reverse=True)[:5]:
            print(f"   {c['coin']}: LONG {c['long_wr']:.1f}% vs SHORT {c['short_wr']:.1f}% (+{c['difference']:.1f}%)")
    
    if short_preferred:
        print("\n🔴 SHORT-PREFERRED COINS (>15% better):")
        for c in sorted(short_preferred, key=lambda x: x['difference'], reverse=True)[:5]:
            print(f"   {c['coin']}: SHORT {c['short_wr']:.1f}% vs LONG {c['long_wr']:.1f}% (+{c['difference']:.1f}%)")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'file': latest_file.name,
        'overall': comparison,
        'by_day': day_comparison,
        'by_hour': hour_comparison,
        'by_coin': coin_comparison,
        'best_days_long': [d['day'] for d in long_best_days],
        'best_days_short': [d['day'] for d in short_best_days],
        'best_hours_long': [h['hour'] for h in long_best_hours],
        'best_hours_short': [h['hour'] for h in short_best_hours],
        'long_preferred_coins': [c['coin'] for c in long_preferred],
        'short_preferred_coins': [c['coin'] for c in short_preferred]
    }
    
    output_file = 'long_vs_short_comparison_refactored.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Comparison complete! Results saved to {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    compare_long_short()
