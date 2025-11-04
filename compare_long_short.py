"""
Compare LONG vs SHORT Performance Patterns
Analyzes differences between LONG and SHORT signals across multiple dimensions
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

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
    
    # Load data
    df = pd.read_csv(latest_file)
    df['signal_time'] = pd.to_datetime(df['signal_time'], format='mixed', utc=True)
    
    # Extract time components
    df['hour'] = df['signal_time'].dt.hour
    df['day_of_week'] = df['signal_time'].dt.dayofweek
    df['day_name'] = df['signal_time'].dt.day_name()
    df['month'] = df['signal_time'].dt.month
    df['month_name'] = df['signal_time'].dt.month_name()
    df['is_winner'] = df['final_outcome'] == 'TARGET1'
    
    # Overall stats
    total = len(df)
    long_data = df[df['action'] == 'LONG']
    short_data = df[df['action'] == 'SHORT']
    
    print(f"📊 DATASET OVERVIEW")
    print(f"   Total Signals: {total:,}")
    print(f"   LONG Signals: {len(long_data):,} ({len(long_data)/total*100:.1f}%)")
    print(f"   SHORT Signals: {len(short_data):,} ({len(short_data)/total*100:.1f}%)")
    print()
    
    # Overall performance comparison
    print("=" * 80)
    print("📊 OVERALL PERFORMANCE COMPARISON")
    print("=" * 80)
    
    comparison = []
    
    for action, data in [('LONG', long_data), ('SHORT', short_data)]:
        wins = data['is_winner'].sum()
        losses = (data['final_outcome'] == 'STOP_LOSS').sum()
        total_action = len(data)
        wr = wins / total_action * 100 if total_action > 0 else 0
        
        avg_profit = data[data['is_winner']]['max_profit_pct'].mean() if wins > 0 else 0
        avg_loss = abs(data[data['final_outcome'] == 'STOP_LOSS']['max_drawdown_pct'].mean()) if losses > 0 else 0
        
        print(f"\n{action}:")
        print(f"  Win Rate: {wr:.1f}% ({wins}/{total_action})")
        print(f"  Wins: {wins} | Losses: {losses}")
        print(f"  Avg Profit: {avg_profit:.2f}%")
        print(f"  Avg Loss: {avg_loss:.2f}%")
        
        comparison.append({
            'action': action,
            'win_rate': wr,
            'wins': wins,
            'losses': losses,
            'total': total_action,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss
        })
    
    print(f"\n💡 Difference: LONG performs {comparison[0]['win_rate'] - comparison[1]['win_rate']:.1f}% better")
    
    # Day of week comparison
    print("\n" + "=" * 80)
    print("📅 PERFORMANCE BY DAY OF WEEK")
    print("=" * 80)
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    print(f"\n{'Day':<12} {'LONG WR':<15} {'SHORT WR':<15} {'Best For':<12} {'Difference'}")
    print("-" * 80)
    
    day_comparison = []
    
    for day in day_order:
        long_day = long_data[long_data['day_name'] == day]
        short_day = short_data[short_data['day_name'] == day]
        
        long_wr = long_day['is_winner'].sum() / len(long_day) * 100 if len(long_day) > 0 else 0
        short_wr = short_day['is_winner'].sum() / len(short_day) * 100 if len(short_day) > 0 else 0
        
        long_count = len(long_day)
        short_count = len(short_day)
        
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
    
    print(f"\n{'Hour':<8} {'LONG WR':<18} {'SHORT WR':<18} {'Best For':<12} {'Difference'}")
    print("-" * 80)
    
    hour_comparison = []
    
    for hour in range(24):
        long_hour = long_data[long_data['hour'] == hour]
        short_hour = short_data[short_data['hour'] == hour]
        
        if len(long_hour) == 0 and len(short_hour) == 0:
            continue
        
        long_wr = long_hour['is_winner'].sum() / len(long_hour) * 100 if len(long_hour) > 0 else 0
        short_wr = short_hour['is_winner'].sum() / len(short_hour) * 100 if len(short_hour) > 0 else 0
        
        long_count = len(long_hour)
        short_count = len(short_hour)
        
        best = "LONG" if long_wr > short_wr else "SHORT" if short_wr > long_wr else "TIE"
        diff = abs(long_wr - short_wr)
        
        if long_count >= 5 or short_count >= 5:  # Only show hours with decent volume
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
    
    print(f"\n{'Coin':<10} {'LONG WR':<18} {'SHORT WR':<18} {'Best For':<12} {'Difference'}")
    print("-" * 80)
    
    coin_comparison = []
    
    for coin in top_coins:
        long_coin = long_data[long_data['symbol'] == coin]
        short_coin = short_data[short_data['symbol'] == coin]
        
        long_wr = long_coin['is_winner'].sum() / len(long_coin) * 100 if len(long_coin) > 0 else 0
        short_wr = short_coin['is_winner'].sum() / len(short_coin) * 100 if len(short_coin) > 0 else 0
        
        long_count = len(long_coin)
        short_count = len(short_coin)
        
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
    long_days_str = ', '.join([f"{d['day']} ({d['long_wr']:.1f}%)" for d in long_best_days])
    short_days_str = ', '.join([f"{d['day']} ({d['short_wr']:.1f}%)" for d in short_best_days])
    print(f"   LONG: {long_days_str}")
    print(f"   SHORT: {short_days_str}")
    
    # Best hours for each
    long_best_hours = sorted([h for h in hour_comparison if h['long_count'] >= 10], 
                            key=lambda x: x['long_wr'], reverse=True)[:3]
    short_best_hours = sorted([h for h in hour_comparison if h['short_count'] >= 5], 
                             key=lambda x: x['short_wr'], reverse=True)[:3]
    
    print("\n⏰ BEST HOURS:")
    long_hours_str = ', '.join([f"{h['hour']:02d}:00 ({h['long_wr']:.1f}%)" for h in long_best_hours])
    short_hours_str = ', '.join([f"{h['hour']:02d}:00 ({h['short_wr']:.1f}%)" for h in short_best_hours])
    print(f"   LONG: {long_hours_str}")
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
    
    output_file = 'long_vs_short_comparison.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Comparison complete! Results saved to {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    compare_long_short()
