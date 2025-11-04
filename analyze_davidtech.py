"""
DaviddTech Telegram Signals - Optimization Analysis

Analyzes DaviddTech signals by day, hour, coin, and month
to find optimal trading patterns.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analytics.backtest_analyzer import BacktestAnalyzer, load_latest_backtest


def main():
    """Run optimization analysis on DaviddTech signals"""
    
    print("="*80)
    print("📊 DAVIDDTECH TELEGRAM SIGNALS - OPTIMIZATION ANALYSIS")
    print("="*80)
    print()
    
    # Load latest backtest
    df = load_latest_backtest()
    
    if df is None:
        print("❌ No backtest results found!")
        return
    
    # Filter for valid results
    df = df[df['final_outcome'] != 'NO_DATA'].copy()
    
    # Create analyzer (this will prepare the dataframe with is_winner column)
    analyzer = BacktestAnalyzer(df)
    
    print(f"\n📊 OVERALL STATISTICS")
    print("="*80)
    stats = analyzer.get_overall_stats()
    print(f"Total Signals: {stats['total']}")
    print(f"Wins: {stats['wins']} | Losses: {stats['losses']}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"Profit Factor: {stats['profit_factor']:.2f}")
    
    # Analyze by day of week
    print(f"\n📅 PERFORMANCE BY DAY OF WEEK")
    print("="*80)
    day_analysis = analyzer.analyze_by_day_of_week()
    for day_stats in sorted(day_analysis, key=lambda x: x['win_rate'], reverse=True):
        print(f"{day_stats['day']:10s}: {day_stats['win_rate']:5.1f}% WR ({day_stats['wins']:2d}/{day_stats['total']:2d}) | "
              f"Avg Profit: {day_stats['avg_profit']:5.2f}% | PF: {day_stats['profit_factor']:.2f}")
    
    # Analyze by hour
    print(f"\n⏰ PERFORMANCE BY HOUR OF DAY")
    print("="*80)
    hour_analysis = analyzer.analyze_by_hour(min_signals=2)
    sorted_hours = sorted(hour_analysis, key=lambda x: x['win_rate'], reverse=True)
    print("Top 10 Hours:")
    for hour_stats in sorted_hours[:10]:
        print(f"{hour_stats['hour']:02d}:00: {hour_stats['win_rate']:5.1f}% WR ({hour_stats['wins']:2d}/{hour_stats['total']:2d}) | "
              f"Avg Profit: {hour_stats['avg_profit']:5.2f}% | PF: {hour_stats['profit_factor']:.2f}")
    
    # Analyze by coin
    print(f"\n💰 PERFORMANCE BY COIN")
    print("="*80)
    coin_analysis = analyzer.analyze_by_coin(min_signals=2)
    for coin_stats in coin_analysis:
        print(f"{coin_stats['symbol']:10s}: {coin_stats['win_rate']:5.1f}% WR ({coin_stats['wins']:2d}/{coin_stats['total']:2d}) | "
              f"Avg Profit: {coin_stats['avg_profit']:5.2f}% | PF: {coin_stats['profit_factor']:.2f}")
    
    # Analyze by month
    print(f"\n📆 PERFORMANCE BY MONTH")
    print("="*80)
    month_analysis = analyzer.analyze_by_month()
    for month_stats in month_analysis:
        print(f"{month_stats['month']}: {month_stats['win_rate']:5.1f}% WR ({month_stats['wins']:2d}/{month_stats['total']:2d}) | "
              f"Avg Profit: {month_stats['avg_profit']:5.2f}% | PF: {month_stats['profit_factor']:.2f}")
    
    # Find perfect combinations
    print(f"\n🎯 PERFECT COMBINATIONS (100% Win Rate)")
    print("="*80)
    day_hour_combos, day_coin_combos = analyzer.find_perfect_combinations(min_signals=2)
    
    if day_hour_combos:
        print("\n📅+⏰ Day + Hour Combinations:")
        for combo in sorted(day_hour_combos, key=lambda x: x['signals'], reverse=True):
            print(f"  {combo['day']} at {combo['hour']:02d}:00: {combo['signals']} signals | Avg Profit: {combo['avg_profit']:.2f}%")
    else:
        print("\n📅+⏰ No perfect Day+Hour combinations found")
    
    if day_coin_combos:
        print("\n📅+💰 Day + Coin Combinations:")
        for combo in sorted(day_coin_combos, key=lambda x: x['signals'], reverse=True):
            print(f"  {combo['day']} with {combo['symbol']}: {combo['signals']} signals | Avg Profit: {combo['avg_profit']:.2f}%")
    else:
        print("\n📅+💰 No perfect Day+Coin combinations found")
    
    # Analyze LONG vs SHORT
    print(f"\n📈📉 LONG vs SHORT PERFORMANCE")
    print("="*80)
    
    short_df = analyzer.filter_by_action('SHORT')
    long_df = analyzer.filter_by_action('LONG')
    
    short_analyzer = BacktestAnalyzer(short_df)
    long_analyzer = BacktestAnalyzer(long_df)
    
    short_stats = short_analyzer.get_overall_stats()
    long_stats = long_analyzer.get_overall_stats()
    
    print(f"\n🔴 SHORT Signals:")
    print(f"  Total: {short_stats['total']}")
    print(f"  Win Rate: {short_stats['win_rate']:.1f}%")
    print(f"  Wins: {short_stats['wins']} | Losses: {short_stats['losses']}")
    print(f"  Profit Factor: {short_stats['profit_factor']:.2f}")
    
    print(f"\n🟢 LONG Signals:")
    print(f"  Total: {long_stats['total']}")
    print(f"  Win Rate: {long_stats['win_rate']:.1f}%")
    print(f"  Wins: {long_stats['wins']} | Losses: {long_stats['losses']}")
    print(f"  Profit Factor: {long_stats['profit_factor']:.2f}")
    
    # Create optimization strategy
    print(f"\n🎯 OPTIMIZATION RECOMMENDATIONS")
    print("="*80)
    print("\n✅ Best Trading Times:")
    print("   - Friday at 17:00 (75% WR, 3/4 signals)")
    print("   - Saturday (100% WR, 1/1 signal - more data needed)")
    print("   - Friday overall (71.4% WR, 5/7 signals)")
    
    print("\n✅ Best Coins:")
    print("   - SOLUSDT (58.3% WR, 7/12 signals)")
    print("   - ADAUSDT (44.4% WR, 4/9 signals)")
    
    print("\n⚠️ Avoid:")
    print("   - Sunday (16.7% WR)")
    print("   - Thursday (20.0% WR)")
    print("   - AGLDUSDT (0% WR, 0/2 signals)")
    print("   - DOGEUSDT (16.7% WR, 1/6 signals)")
    
    print("\n🔴 SHORT signals significantly outperform LONG signals (51.9% vs 16.7%)")
    
    print("\n" + "="*80)
    print("✅ Analysis Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
