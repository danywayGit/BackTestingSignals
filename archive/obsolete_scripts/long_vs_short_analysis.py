"""
Long vs Short Analysis - Detailed Position Type Performance
Analyzes if LONG and SHORT signals perform differently across:
- Days of the week (especially Thursday!)
- Hours
- Coins
- Months
"""

import pandas as pd
from pathlib import Path

def analyze_long_vs_short():
    """Analyze LONG vs SHORT performance"""
    
    # Load latest results
    results_dir = Path('data/backtest_results')
    results_files = list(results_dir.glob('intermediate_results_*.csv'))
    latest_file = max(results_files, key=lambda x: int(x.stem.split('_')[2]))
    
    print("=" * 80)
    print("🔄 LONG vs SHORT POSITION ANALYSIS")
    print("=" * 80)
    print(f"\n📂 Analyzing: {latest_file}\n")
    
    # Load data
    df = pd.read_csv(latest_file)
    df['signal_time'] = pd.to_datetime(df['signal_time'], format='mixed', utc=True)
    
    # Extract time components
    df['hour'] = df['signal_time'].dt.hour
    df['day_of_week'] = df['signal_time'].dt.dayofweek
    df['day_name'] = df['signal_time'].dt.day_name()
    df['month_name'] = df['signal_time'].dt.month_name()
    df['is_winner'] = df['final_outcome'] == 'TARGET1'
    
    print(f"📊 Total Signals: {len(df)}")
    print(f"   LONG: {len(df[df['action'] == 'LONG'])} ({len(df[df['action'] == 'LONG'])/len(df)*100:.1f}%)")
    print(f"   SHORT: {len(df[df['action'] == 'SHORT'])} ({len(df[df['action'] == 'SHORT'])/len(df)*100:.1f}%)")
    print()
    
    # Overall performance by position type
    print("=" * 80)
    print("📊 OVERALL PERFORMANCE: LONG vs SHORT")
    print("=" * 80)
    
    for action in ['LONG', 'SHORT']:
        action_data = df[df['action'] == action]
        total = len(action_data)
        wins = action_data['is_winner'].sum()
        losses = (action_data['final_outcome'] == 'STOP_LOSS').sum()
        wr = (wins / total * 100) if total > 0 else 0
        
        print(f"\n{action}:")
        print(f"  Total Signals: {total}")
        print(f"  Wins: {wins} | Losses: {losses}")
        print(f"  Win Rate: {wr:.1f}%")
    
    # Thursday analysis - THE KEY QUESTION!
    print("\n" + "=" * 80)
    print("🔍 THURSDAY ANALYSIS (The Critical Day)")
    print("=" * 80)
    
    thursday_data = df[df['day_name'] == 'Thursday']
    
    print(f"\n📅 Thursday Overall:")
    thursday_wins = thursday_data['is_winner'].sum()
    thursday_total = len(thursday_data)
    thursday_wr = (thursday_wins / thursday_total * 100) if thursday_total > 0 else 0
    print(f"  Total Signals: {thursday_total}")
    print(f"  Win Rate: {thursday_wr:.1f}%")
    
    print(f"\n🔄 Thursday Breakdown by Position Type:")
    print("-" * 80)
    
    for action in ['LONG', 'SHORT']:
        action_thursday = thursday_data[thursday_data['action'] == action]
        total = len(action_thursday)
        wins = action_thursday['is_winner'].sum()
        losses = (action_thursday['final_outcome'] == 'STOP_LOSS').sum()
        wr = (wins / total * 100) if total > 0 else 0
        
        print(f"\n  {action} on Thursday:")
        print(f"    Signals: {total}")
        print(f"    Wins: {wins} | Losses: {losses}")
        print(f"    Win Rate: {wr:.1f}%")
        
        if total > 0:
            # Show which coins on Thursday
            coins = action_thursday.groupby('symbol').size().sort_values(ascending=False).head(5)
            print(f"    Top Coins: {', '.join([f'{coin}({count})' for coin, count in coins.items()])}")
    
    # Compare Thursday to other days by position type
    print("\n" + "=" * 80)
    print("📊 DAY OF WEEK COMPARISON: LONG vs SHORT")
    print("=" * 80)
    
    for action in ['LONG', 'SHORT']:
        print(f"\n{action} Positions:")
        print("-" * 80)
        
        action_data = df[df['action'] == action]
        day_stats = []
        
        for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_data = action_data[action_data['day_name'] == day_name]
            total = len(day_data)
            if total == 0:
                continue
            wins = day_data['is_winner'].sum()
            wr = (wins / total * 100)
            day_stats.append({'day': day_name, 'total': total, 'wins': wins, 'wr': wr})
        
        if not day_stats:
            print("  No data available")
            continue
            
        day_df = pd.DataFrame(day_stats).sort_values('wr', ascending=False)
        
        for _, row in day_df.iterrows():
            marker = "🔥" if row['wr'] > 50 else "⚠️" if row['wr'] < 30 else "  "
            highlight = "<<<" if row['day'] == 'Thursday' else ""
            print(f"{marker} {row['day']:10} | WR: {row['wr']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3} {highlight}")
    
    # Hour analysis by position type
    print("\n" + "=" * 80)
    print("⏰ BEST HOURS: LONG vs SHORT")
    print("=" * 80)
    
    for action in ['LONG', 'SHORT']:
        print(f"\n{action} Positions - Top 10 Hours:")
        print("-" * 80)
        
        action_data = df[df['action'] == action]
        hour_stats = []
        
        for hour in range(24):
            hour_data = action_data[action_data['hour'] == hour]
            total = len(hour_data)
            if total < 5:
                continue
            wins = hour_data['is_winner'].sum()
            wr = (wins / total * 100)
            hour_stats.append({'hour': hour, 'total': total, 'wins': wins, 'wr': wr})
        
        if hour_stats:
            hour_df = pd.DataFrame(hour_stats).sort_values('wr', ascending=False)
            
            for _, row in hour_df.head(10).iterrows():
                print(f"  {int(row['hour']):02d}:00 UTC | WR: {row['wr']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3}")
    
    # Month analysis by position type
    print("\n" + "=" * 80)
    print("📆 BEST MONTHS: LONG vs SHORT")
    print("=" * 80)
    
    for action in ['LONG', 'SHORT']:
        print(f"\n{action} Positions:")
        print("-" * 80)
        
        action_data = df[df['action'] == action]
        month_stats = []
        
        for month in action_data['month_name'].unique():
            month_data = action_data[action_data['month_name'] == month]
            total = len(month_data)
            wins = month_data['is_winner'].sum()
            wr = (wins / total * 100)
            month_stats.append({'month': month, 'total': total, 'wins': wins, 'wr': wr})
        
        if not month_stats:
            print("  No data available")
            continue
            
        month_df = pd.DataFrame(month_stats).sort_values('wr', ascending=False)
        
        for _, row in month_df.iterrows():
            marker = "🔥" if row['wr'] > 50 else "❌" if row['wr'] < 25 else "  "
            print(f"{marker} {row['month']:10} | WR: {row['wr']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3}")
    
    # Coin analysis by position type
    print("\n" + "=" * 80)
    print("🪙 TOP COINS: LONG vs SHORT")
    print("=" * 80)
    
    for action in ['LONG', 'SHORT']:
        print(f"\n{action} Positions - Top 10 Coins:")
        print("-" * 80)
        
        action_data = df[df['action'] == action]
        coin_stats = []
        
        for symbol in action_data['symbol'].unique():
            coin_data = action_data[action_data['symbol'] == symbol]
            total = len(coin_data)
            if total < 5:
                continue
            wins = coin_data['is_winner'].sum()
            wr = (wins / total * 100)
            coin_stats.append({'symbol': symbol, 'total': total, 'wins': wins, 'wr': wr})
        
        if coin_stats:
            coin_df = pd.DataFrame(coin_stats).sort_values('wr', ascending=False)
            
            for _, row in coin_df.head(10).iterrows():
                print(f"  {row['symbol']:8} | WR: {row['wr']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3}")
    
    # Final recommendations
    print("\n" + "=" * 80)
    print("💡 KEY INSIGHTS & RECOMMENDATIONS")
    print("=" * 80)
    
    # Calculate key metrics
    long_data = df[df['action'] == 'LONG']
    short_data = df[df['action'] == 'SHORT']
    
    long_wr = (long_data['is_winner'].sum() / len(long_data) * 100) if len(long_data) > 0 else 0
    short_wr = (short_data['is_winner'].sum() / len(short_data) * 100) if len(short_data) > 0 else 0
    
    long_thursday = thursday_data[thursday_data['action'] == 'LONG']
    short_thursday = thursday_data[thursday_data['action'] == 'SHORT']
    
    long_thursday_wr = (long_thursday['is_winner'].sum() / len(long_thursday) * 100) if len(long_thursday) > 0 else 0
    short_thursday_wr = (short_thursday['is_winner'].sum() / len(short_thursday) * 100) if len(short_thursday) > 0 else 0
    
    print(f"\n1. OVERALL PERFORMANCE:")
    print(f"   LONG:  {long_wr:.1f}% win rate ({len(long_data)} signals)")
    print(f"   SHORT: {short_wr:.1f}% win rate ({len(short_data)} signals)")
    if long_wr > short_wr:
        print(f"   → LONG positions perform better overall (+{long_wr - short_wr:.1f}%)")
    else:
        print(f"   → SHORT positions perform better overall (+{short_wr - long_wr:.1f}%)")
    
    print(f"\n2. THURSDAY PERFORMANCE:")
    print(f"   LONG on Thursday:  {long_thursday_wr:.1f}% ({len(long_thursday)} signals)")
    print(f"   SHORT on Thursday: {short_thursday_wr:.1f}% ({len(short_thursday)} signals)")
    
    if long_thursday_wr < 30 and short_thursday_wr < 30:
        print(f"   → ⚠️ BOTH are terrible on Thursday! Avoid trading entirely.")
    elif long_thursday_wr < short_thursday_wr - 10:
        print(f"   → ⚠️ LONG is much worse. SHORT might be acceptable.")
    elif short_thursday_wr < long_thursday_wr - 10:
        print(f"   → ⚠️ SHORT is much worse. LONG might be acceptable.")
    else:
        print(f"   → Both perform similarly poorly on Thursday.")
    
    print(f"\n3. RECOMMENDATION:")
    if long_thursday_wr < 35 and short_thursday_wr < 35:
        print(f"   🚫 Skip ALL Thursday signals (both LONG and SHORT)")
    elif long_thursday_wr >= 40 and short_thursday_wr < 35:
        print(f"   ⚠️ Thursday: Only trade LONG (avoid SHORT)")
    elif short_thursday_wr >= 40 and long_thursday_wr < 35:
        print(f"   ⚠️ Thursday: Only trade SHORT (avoid LONG)")
    else:
        print(f"   ⚠️ Use extreme caution on Thursday regardless of position type")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_long_vs_short()
