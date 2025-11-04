"""
Compare October 13 Baseline with November 4 Results
Analyzes improvements and changes between two backtest runs
"""

import pandas as pd
import json
from pathlib import Path

def compare_backtests():
    """Compare October and November backtest results"""
    
    results_dir = Path('data/backtest_results')
    
    # October 13 baseline (989 signals, LONG only)
    october_file = results_dir / 'meta_signals_backtest_detailed_20251013_195515.csv'
    october_metrics = results_dir / 'meta_signals_backtest_metrics_20251013_195515.json'
    
    # November 4 results (1139 signals, LONG + SHORT)
    november_file = results_dir / 'meta_signals_backtest_detailed_20251104_031305.csv'
    november_metrics = results_dir / 'meta_signals_backtest_metrics_20251104_031305.json'
    
    print("=" * 80)
    print("📊 OCTOBER 13 vs NOVEMBER 4 COMPARISON")
    print("=" * 80)
    print()
    
    # Load metrics
    with open(october_metrics, 'r') as f:
        oct_metrics = json.load(f)
    
    with open(november_metrics, 'r') as f:
        nov_metrics = json.load(f)
    
    # Load detailed data
    oct_df = pd.read_csv(october_file)
    nov_df = pd.read_csv(november_file)
    
    # Parse timestamps
    oct_df['signal_time'] = pd.to_datetime(oct_df['signal_time'], format='mixed', utc=True)
    nov_df['signal_time'] = pd.to_datetime(nov_df['signal_time'], format='mixed', utc=True)
    
    # Basic dataset comparison
    print("📅 DATASET OVERVIEW")
    print("-" * 80)
    print(f"October 13 Baseline:")
    print(f"  Date Range: {oct_df['signal_time'].min().date()} to {oct_df['signal_time'].max().date()}")
    print(f"  Total Signals: {len(oct_df):,}")
    print(f"  LONG: {len(oct_df[oct_df['action'] == 'LONG']):,}")
    print(f"  SHORT: {len(oct_df[oct_df['action'] == 'SHORT']):,}")
    print()
    print(f"November 4 Results:")
    print(f"  Date Range: {nov_df['signal_time'].min().date()} to {nov_df['signal_time'].max().date()}")
    print(f"  Total Signals: {len(nov_df):,}")
    print(f"  LONG: {len(nov_df[nov_df['action'] == 'LONG']):,}")
    print(f"  SHORT: {len(nov_df[nov_df['action'] == 'SHORT']):,}")
    print()
    print(f"💡 Change: +{len(nov_df) - len(oct_df)} signals (+{(len(nov_df) - len(oct_df))/len(oct_df)*100:.1f}%)")
    print(f"   NEW SHORT signals: {len(nov_df[nov_df['action'] == 'SHORT'])}")
    print()
    
    # Overall performance comparison
    print("=" * 80)
    print("📊 OVERALL PERFORMANCE COMPARISON")
    print("=" * 80)
    
    oct_wins = (oct_df['final_outcome'] == 'TARGET1').sum()
    oct_losses = (oct_df['final_outcome'] == 'STOP_LOSS').sum()
    oct_wr = oct_wins / len(oct_df) * 100
    
    nov_wins = (nov_df['final_outcome'] == 'TARGET1').sum()
    nov_losses = (nov_df['final_outcome'] == 'STOP_LOSS').sum()
    nov_wr = nov_wins / len(nov_df) * 100
    
    print(f"\n{'Metric':<25} {'October 13':<20} {'November 4':<20} {'Change'}")
    print("-" * 80)
    print(f"{'Win Rate':<25} {oct_wr:>6.1f}% ({oct_wins}/{len(oct_df)})  {nov_wr:>6.1f}% ({nov_wins}/{len(nov_df)})  {nov_wr - oct_wr:>+6.1f}%")
    print(f"{'Total Wins':<25} {oct_wins:>18,}  {nov_wins:>18,}  {nov_wins - oct_wins:>+6,}")
    print(f"{'Total Losses':<25} {oct_losses:>18,}  {nov_losses:>18,}  {nov_losses - oct_losses:>+6,}")
    
    # LONG-only comparison (apples to apples)
    print("\n" + "=" * 80)
    print("🔵 LONG SIGNALS COMPARISON (Apples-to-Apples)")
    print("=" * 80)
    
    oct_long = oct_df[oct_df['action'] == 'LONG']
    nov_long = nov_df[nov_df['action'] == 'LONG']
    
    oct_long_wins = (oct_long['final_outcome'] == 'TARGET1').sum()
    oct_long_wr = oct_long_wins / len(oct_long) * 100
    
    nov_long_wins = (nov_long['final_outcome'] == 'TARGET1').sum()
    nov_long_wr = nov_long_wins / len(nov_long) * 100
    
    print(f"\n{'Metric':<25} {'October 13':<20} {'November 4':<20} {'Change'}")
    print("-" * 80)
    print(f"{'LONG Signals':<25} {len(oct_long):>18,}  {len(nov_long):>18,}  {len(nov_long) - len(oct_long):>+6,}")
    print(f"{'LONG Win Rate':<25} {oct_long_wr:>17.1f}%  {nov_long_wr:>17.1f}%  {nov_long_wr - oct_long_wr:>+6.1f}%")
    print(f"{'LONG Wins':<25} {oct_long_wins:>18,}  {nov_long_wins:>18,}  {nov_long_wins - oct_long_wins:>+6,}")
    
    # Top coins comparison
    print("\n" + "=" * 80)
    print("🪙 TOP PERFORMING COINS COMPARISON")
    print("=" * 80)
    
    # Calculate win rates by coin for both
    oct_by_coin = oct_df.groupby('symbol').agg({
        'final_outcome': lambda x: ((x == 'TARGET1').sum(), len(x), (x == 'TARGET1').sum() / len(x) * 100)
    }).reset_index()
    oct_by_coin.columns = ['symbol', 'stats']
    oct_by_coin[['wins', 'total', 'wr']] = pd.DataFrame(oct_by_coin['stats'].tolist(), index=oct_by_coin.index)
    oct_by_coin = oct_by_coin[oct_by_coin['total'] >= 10].sort_values('wr', ascending=False).head(10)
    
    nov_by_coin = nov_df.groupby('symbol').agg({
        'final_outcome': lambda x: ((x == 'TARGET1').sum(), len(x), (x == 'TARGET1').sum() / len(x) * 100)
    }).reset_index()
    nov_by_coin.columns = ['symbol', 'stats']
    nov_by_coin[['wins', 'total', 'wr']] = pd.DataFrame(nov_by_coin['stats'].tolist(), index=nov_by_coin.index)
    nov_by_coin = nov_by_coin[nov_by_coin['total'] >= 10].sort_values('wr', ascending=False).head(10)
    
    print("\n📈 OCTOBER 13 TOP 10 COINS (10+ signals):")
    for idx, row in oct_by_coin.iterrows():
        print(f"  {row['symbol']:<10} {row['wr']:>5.1f}% ({int(row['wins'])}/{int(row['total'])})")
    
    print("\n📈 NOVEMBER 4 TOP 10 COINS (10+ signals):")
    for idx, row in nov_by_coin.iterrows():
        print(f"  {row['symbol']:<10} {row['wr']:>5.1f}% ({int(row['wins'])}/{int(row['total'])})")
    
    # Find coins that improved significantly
    print("\n" + "=" * 80)
    print("📊 COINS WITH SIGNIFICANT CHANGES (10+ signals in both)")
    print("=" * 80)
    
    oct_coins_dict = {}
    for idx, row in oct_by_coin.iterrows():
        oct_coins_dict[row['symbol']] = row['wr']
    
    nov_coins_dict = {}
    for idx, row in nov_by_coin.iterrows():
        nov_coins_dict[row['symbol']] = row['wr']
    
    # Get coins in both datasets
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
    
    # Sort by absolute change
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
    
    oct_df['hour'] = oct_df['signal_time'].dt.hour
    nov_df['hour'] = nov_df['signal_time'].dt.hour
    
    oct_by_hour = oct_df.groupby('hour').agg({
        'final_outcome': lambda x: (x == 'TARGET1').sum() / len(x) * 100
    }).reset_index()
    oct_by_hour.columns = ['hour', 'wr']
    oct_top_hours = oct_by_hour.nlargest(5, 'wr')
    
    nov_by_hour = nov_df.groupby('hour').agg({
        'final_outcome': lambda x: (x == 'TARGET1').sum() / len(x) * 100
    }).reset_index()
    nov_by_hour.columns = ['hour', 'wr']
    nov_top_hours = nov_by_hour.nlargest(5, 'wr')
    
    print("\n📈 OCTOBER 13 TOP 5 HOURS:")
    for idx, row in oct_top_hours.iterrows():
        print(f"  {int(row['hour']):02d}:00 UTC: {row['wr']:>5.1f}%")
    
    print("\n📈 NOVEMBER 4 TOP 5 HOURS:")
    for idx, row in nov_top_hours.iterrows():
        print(f"  {int(row['hour']):02d}:00 UTC: {row['wr']:>5.1f}%")
    
    # Key findings
    print("\n" + "=" * 80)
    print("🎯 KEY FINDINGS & RECOMMENDATIONS")
    print("=" * 80)
    
    wr_change = nov_wr - oct_wr
    long_wr_change = nov_long_wr - oct_long_wr
    
    print(f"\n1. OVERALL QUALITY:")
    if wr_change > 0:
        print(f"   ✅ Signal quality IMPROVED by {wr_change:.1f}%")
    elif wr_change < 0:
        print(f"   ⚠️  Signal quality DECLINED by {abs(wr_change):.1f}%")
    else:
        print(f"   ⚪ Signal quality UNCHANGED")
    
    print(f"\n2. LONG SIGNALS:")
    if long_wr_change > 0:
        print(f"   ✅ LONG performance IMPROVED by {long_wr_change:.1f}%")
    elif long_wr_change < 0:
        print(f"   ⚠️  LONG performance DECLINED by {abs(long_wr_change):.1f}%")
    else:
        print(f"   ⚪ LONG performance UNCHANGED")
    
    print(f"\n3. SHORT SIGNALS:")
    nov_short = nov_df[nov_df['action'] == 'SHORT']
    if len(nov_short) > 0:
        short_wins = (nov_short['final_outcome'] == 'TARGET1').sum()
        short_wr = short_wins / len(nov_short) * 100
        print(f"   📊 {len(nov_short)} SHORT signals added with {short_wr:.1f}% WR")
        if short_wr > 50:
            print(f"   ✅ SHORT signals are PROFITABLE")
        else:
            print(f"   ⚠️  SHORT signals need optimization")
    
    print(f"\n4. DATA VOLUME:")
    print(f"   📈 +{len(nov_df) - len(oct_df)} signals ({(len(nov_df) - len(oct_df))/len(oct_df)*100:.1f}% increase)")
    print(f"   💡 More data = better statistical confidence")
    
    print("\n" + "=" * 80)
    print("✅ Comparison Complete!")
    print("=" * 80)

if __name__ == "__main__":
    compare_backtests()
