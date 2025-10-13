"""
Optimization Analysis - Find Best Trading Setups
Analyzes backtest results to identify optimal configurations based on:
- Coin performance        day_df = pd.DataFrame(day_stats).sort_values('win_rate', ascending=False)
        for idx, row in day_df.iterrows():
            print(f"{row['day']:10} | WR: {row['win_rate']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3}") Timeframe patterns (hour, day, month)
- Risk/Reward ratios
- Entry volatility
- Market conditions
- Combined filters for maximum edge
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
from collections import defaultdict

class OptimizationAnalyzer:
    def __init__(self, results_file):
        """Initialize analyzer with backtest results"""
        self.df = pd.read_csv(results_file)
        self.df['signal_time'] = pd.to_datetime(self.df['signal_time'], format='mixed', utc=True)
        
        # Extract time components
        self.df['hour'] = self.df['signal_time'].dt.hour
        self.df['day_of_week'] = self.df['signal_time'].dt.dayofweek
        self.df['day_name'] = self.df['signal_time'].dt.day_name()
        self.df['month'] = self.df['signal_time'].dt.month
        self.df['month_name'] = self.df['signal_time'].dt.month_name()
        
        # Calculate R:R ratios
        self.df['rr_target1'] = (self.df['target1'] - self.df['entry_price']) / (self.df['entry_price'] - self.df['stop_loss'])
        self.df['rr_target2'] = (self.df['target2'] - self.df['entry_price']) / (self.df['entry_price'] - self.df['stop_loss'])
        self.df['rr_target3'] = (self.df['target3'] - self.df['entry_price']) / (self.df['entry_price'] - self.df['stop_loss'])
        
        # Calculate stop loss distance (risk)
        self.df['sl_distance_pct'] = abs((self.df['stop_loss'] - self.df['entry_price']) / self.df['entry_price'] * 100)
        
        # Categorize outcomes
        self.df['is_winner'] = self.df['final_outcome'] == 'TARGET1'
        self.df['is_big_winner'] = self.df['final_outcome'].isin(['TARGET2', 'TARGET3'])
        
        print(f"📊 Loaded {len(self.df)} signals for optimization analysis")
        print(f"✅ Winners: {self.df['is_winner'].sum()}")
        print(f"❌ Losers: {(self.df['final_outcome'] == 'STOP_LOSS').sum()}")
        print()
    
    def analyze_by_coin(self, min_signals=5):
        """Find best performing coins"""
        print("=" * 80)
        print("🪙 BEST PERFORMING COINS")
        print("=" * 80)
        
        coin_stats = []
        for symbol in self.df['symbol'].unique():
            coin_data = self.df[self.df['symbol'] == symbol]
            total = len(coin_data)
            
            if total < min_signals:
                continue
            
            wins = coin_data['is_winner'].sum()
            losses = (coin_data['final_outcome'] == 'STOP_LOSS').sum()
            win_rate = (wins / total * 100) if total > 0 else 0
            
            avg_profit = coin_data[coin_data['is_winner']]['max_profit_pct'].mean() if wins > 0 else 0
            avg_loss = coin_data[coin_data['final_outcome'] == 'STOP_LOSS']['max_drawdown_pct'].mean() if losses > 0 else 0
            
            profit_factor = abs(wins * avg_profit / (losses * avg_loss)) if losses > 0 and avg_loss != 0 else 0
            
            coin_stats.append({
                'symbol': symbol,
                'total_signals': total,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor
            })
        
        coin_df = pd.DataFrame(coin_stats).sort_values('win_rate', ascending=False)
        
        print("\n🏆 TOP 15 COINS BY WIN RATE:")
        print("-" * 80)
        for idx, row in coin_df.head(15).iterrows():
            print(f"{row['symbol']:8} | WR: {row['win_rate']:5.1f}% | Signals: {row['total_signals']:3} | "
                  f"PF: {row['profit_factor']:4.2f} | Avg Win: {row['avg_profit']:5.2f}%")
        
        print("\n💰 TOP 15 COINS BY PROFIT FACTOR:")
        print("-" * 80)
        for idx, row in coin_df.sort_values('profit_factor', ascending=False).head(15).iterrows():
            print(f"{row['symbol']:8} | PF: {row['profit_factor']:4.2f} | WR: {row['win_rate']:5.1f}% | "
                  f"Signals: {row['total_signals']:3} | Avg Win: {row['avg_profit']:5.2f}%")
        
        return coin_df
    
    def analyze_by_timeframe(self):
        """Find best hours, days, and months"""
        print("\n" + "=" * 80)
        print("⏰ BEST TIMEFRAMES")
        print("=" * 80)
        
        # Hour analysis
        print("\n🕐 BEST HOURS (UTC):")
        print("-" * 80)
        hour_stats = []
        for hour in range(24):
            hour_data = self.df[self.df['hour'] == hour]
            total = len(hour_data)
            if total < 5:
                continue
            
            wins = hour_data['is_winner'].sum()
            win_rate = (wins / total * 100) if total > 0 else 0
            
            hour_stats.append({
                'hour': hour,
                'total': total,
                'wins': wins,
                'win_rate': win_rate
            })
        
        hour_df = pd.DataFrame(hour_stats).sort_values('win_rate', ascending=False)
        for idx, row in hour_df.head(10).iterrows():
            print(f"{int(row['hour']):02d}:00 UTC | WR: {row['win_rate']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3}")
        
        # Day of week analysis
        print("\n📅 BEST DAYS OF WEEK:")
        print("-" * 80)
        day_stats = []
        for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_data = self.df[self.df['day_name'] == day_name]
            total = len(day_data)
            wins = day_data['is_winner'].sum()
            win_rate = (wins / total * 100) if total > 0 else 0
            
            day_stats.append({
                'day': day_name,
                'total': total,
                'wins': wins,
                'win_rate': win_rate
            })
        
        day_df = pd.DataFrame(day_stats).sort_values('win_rate', ascending=False)
        for idx, row in day_df.iterrows():
            print(f"{row['day']:10} | WR: {row['win_rate']:5.1f}% | Signals: {row['total']:3} | Wins: {row['wins']:3}")
        
        # Month analysis
        print("\n📆 BEST MONTHS:")
        print("-" * 80)
        month_stats = []
        for month_name in self.df['month_name'].unique():
            month_data = self.df[self.df['month_name'] == month_name]
            total = len(month_data)
            wins = month_data['is_winner'].sum()
            win_rate = (wins / total * 100) if total > 0 else 0
            
            month_stats.append({
                'month': month_name,
                'total': total,
                'wins': wins,
                'win_rate': win_rate
            })
        
        month_df = pd.DataFrame(month_stats).sort_values('win_rate', ascending=False)
        for idx, row in month_df.iterrows():
            print(f"{row['month']:10} | WR: {row['win_rate']:5.1f}% | Signals: {int(row['total']):3} | Wins: {int(row['wins']):3}")
        
        return hour_df, day_df, month_df
    
    def analyze_by_risk_reward(self):
        """Find optimal R:R ratios"""
        print("\n" + "=" * 80)
        print("🎯 OPTIMAL RISK/REWARD RATIOS")
        print("=" * 80)
        
        # Analyze by R:R buckets
        print("\n📊 WIN RATE BY R:R TARGET 1:")
        print("-" * 80)
        rr_buckets = [(0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 10.0)]
        
        for min_rr, max_rr in rr_buckets:
            bucket_data = self.df[(self.df['rr_target1'] >= min_rr) & (self.df['rr_target1'] < max_rr)]
            total = len(bucket_data)
            if total < 5:
                continue
            
            wins = bucket_data['is_winner'].sum()
            win_rate = (wins / total * 100) if total > 0 else 0
            
            print(f"R:R {min_rr:.1f}-{max_rr:.1f} | WR: {win_rate:5.1f}% | Signals: {int(total):3} | Wins: {int(wins):3}")
        
        # Analyze by stop loss distance
        print("\n📏 WIN RATE BY STOP LOSS DISTANCE:")
        print("-" * 80)
        sl_buckets = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 10), (10, 100)]
        
        for min_sl, max_sl in sl_buckets:
            bucket_data = self.df[(self.df['sl_distance_pct'] >= min_sl) & (self.df['sl_distance_pct'] < max_sl)]
            total = len(bucket_data)
            if total < 5:
                continue
            
            wins = bucket_data['is_winner'].sum()
            win_rate = (wins / total * 100) if total > 0 else 0
            
            print(f"SL {min_sl:.1f}-{max_sl:.1f}% | WR: {win_rate:5.1f}% | Signals: {int(total):3} | Wins: {int(wins):3}")
    
    def find_optimal_combinations(self, coin_df, hour_df):
        """Find best combinations of filters"""
        print("\n" + "=" * 80)
        print("🔥 OPTIMAL TRADING SETUPS (COMBINED FILTERS)")
        print("=" * 80)
        
        # Get top coins and hours
        top_coins = coin_df.head(10)['symbol'].tolist()
        top_hours = hour_df.head(8)['hour'].tolist()
        
        combinations = []
        
        # Test combinations
        for symbol in top_coins:
            for hour in top_hours:
                combo_data = self.df[(self.df['symbol'] == symbol) & (self.df['hour'] == hour)]
                total = len(combo_data)
                
                if total < 3:  # Need at least 3 signals
                    continue
                
                wins = combo_data['is_winner'].sum()
                win_rate = (wins / total * 100) if total > 0 else 0
                
                combinations.append({
                    'symbol': symbol,
                    'hour': hour,
                    'total': total,
                    'wins': wins,
                    'win_rate': win_rate
                })
        
        combo_df = pd.DataFrame(combinations).sort_values('win_rate', ascending=False)
        
        print("\n🎯 TOP 20 COIN + HOUR COMBINATIONS:")
        print("-" * 80)
        for idx, row in combo_df.head(20).iterrows():
            print(f"{row['symbol']:8} @ {int(row['hour']):02d}:00 UTC | WR: {row['win_rate']:5.1f}% | "
                  f"Signals: {int(row['total']):2} | Wins: {int(row['wins']):2}")
        
        # Test coin + day combinations
        print("\n📅 TOP 15 COIN + DAY COMBINATIONS:")
        print("-" * 80)
        day_combinations = []
        
        for symbol in top_coins:
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                combo_data = self.df[(self.df['symbol'] == symbol) & (self.df['day_name'] == day)]
                total = len(combo_data)
                
                if total < 3:
                    continue
                
                wins = combo_data['is_winner'].sum()
                win_rate = (wins / total * 100) if total > 0 else 0
                
                day_combinations.append({
                    'symbol': symbol,
                    'day': day,
                    'total': total,
                    'wins': wins,
                    'win_rate': win_rate
                })
        
        day_combo_df = pd.DataFrame(day_combinations).sort_values('win_rate', ascending=False)
        for idx, row in day_combo_df.head(15).iterrows():
            print(f"{row['symbol']:8} on {row['day']:9} | WR: {row['win_rate']:5.1f}% | "
                  f"Signals: {int(row['total']):2} | Wins: {int(row['wins']):2}")
        
        return combo_df, day_combo_df
    
    def find_edge_setups(self):
        """Find setups with significant edge"""
        print("\n" + "=" * 80)
        print("💎 HIGH-EDGE SETUPS (>65% WIN RATE)")
        print("=" * 80)
        
        high_edge = []
        
        # Multi-dimensional analysis
        for symbol in self.df['symbol'].unique():
            symbol_data = self.df[self.df['symbol'] == symbol]
            
            for hour in range(24):
                hour_data = symbol_data[symbol_data['hour'] == hour]
                
                for min_rr, max_rr in [(1.0, 1.5), (1.5, 2.0), (2.0, 3.0)]:
                    rr_data = hour_data[(hour_data['rr_target1'] >= min_rr) & (hour_data['rr_target1'] < max_rr)]
                    
                    total = len(rr_data)
                    if total < 3:
                        continue
                    
                    wins = rr_data['is_winner'].sum()
                    win_rate = (wins / total * 100) if total > 0 else 0
                    
                    if win_rate >= 65:
                        high_edge.append({
                            'symbol': symbol,
                            'hour': hour,
                            'rr_range': f"{min_rr:.1f}-{max_rr:.1f}",
                            'total': total,
                            'wins': wins,
                            'win_rate': win_rate
                        })
        
        if high_edge:
            edge_df = pd.DataFrame(high_edge).sort_values('win_rate', ascending=False)
            print("\n🎯 COIN + HOUR + R:R COMBINATIONS:")
            print("-" * 80)
            for idx, row in edge_df.head(25).iterrows():
                print(f"{row['symbol']:8} @ {int(row['hour']):02d}:00 UTC | R:R {row['rr_range']:8} | "
                      f"WR: {row['win_rate']:5.1f}% | Signals: {int(row['total']):2} | Wins: {int(row['wins']):2}")
        else:
            print("No setups found with >65% win rate (try lowering threshold)")
    
    def generate_trading_rules(self, coin_df, hour_df):
        """Generate actionable trading rules"""
        print("\n" + "=" * 80)
        print("📋 RECOMMENDED TRADING RULES")
        print("=" * 80)
        
        # Get high performers
        top_5_coins = coin_df.head(5)['symbol'].tolist()
        top_5_hours = hour_df.head(5)['hour'].tolist()
        
        print("\n✅ RULES FOR MAXIMUM WIN RATE:")
        print("-" * 80)
        print(f"1. ONLY trade these coins: {', '.join(top_5_coins)}")
        print(f"2. ONLY trade during these hours (UTC): {', '.join([f'{h:02d}:00' for h in top_5_hours])}")
        
        # Test the rules
        filtered_data = self.df[
            (self.df['symbol'].isin(top_5_coins)) & 
            (self.df['hour'].isin(top_5_hours))
        ]
        
        total_filtered = len(filtered_data)
        wins_filtered = filtered_data['is_winner'].sum()
        wr_filtered = (wins_filtered / total_filtered * 100) if total_filtered > 0 else 0
        
        print(f"\n📊 APPLYING THESE RULES:")
        print(f"   - Signals: {len(self.df)} → {total_filtered} ({total_filtered/len(self.df)*100:.1f}% kept)")
        print(f"   - Win Rate: {self.df['is_winner'].sum()/len(self.df)*100:.1f}% → {wr_filtered:.1f}%")
        print(f"   - Improvement: +{wr_filtered - (self.df['is_winner'].sum()/len(self.df)*100):.1f}%")
        
        # Additional rules
        print("\n✅ ADDITIONAL FILTERS TO CONSIDER:")
        print("-" * 80)
        
        # R:R sweet spot
        rr_data = self.df[(self.df['rr_target1'] >= 1.0) & (self.df['rr_target1'] <= 2.0)]
        rr_wr = (rr_data['is_winner'].sum() / len(rr_data) * 100) if len(rr_data) > 0 else 0
        print(f"3. Target R:R 1.0-2.0 (Win Rate: {rr_wr:.1f}%)")
        
        # Stop loss sweet spot
        sl_data = self.df[(self.df['sl_distance_pct'] >= 1.5) & (self.df['sl_distance_pct'] <= 3.0)]
        sl_wr = (sl_data['is_winner'].sum() / len(sl_data) * 100) if len(sl_data) > 0 else 0
        print(f"4. Stop Loss 1.5-3.0% (Win Rate: {sl_wr:.1f}%)")
        
        # Combined ultra-filtered
        ultra_filtered = self.df[
            (self.df['symbol'].isin(top_5_coins)) & 
            (self.df['hour'].isin(top_5_hours)) &
            (self.df['rr_target1'] >= 1.0) & 
            (self.df['rr_target1'] <= 2.0) &
            (self.df['sl_distance_pct'] >= 1.5) &
            (self.df['sl_distance_pct'] <= 3.0)
        ]
        
        if len(ultra_filtered) > 0:
            ultra_wr = (ultra_filtered['is_winner'].sum() / len(ultra_filtered) * 100)
            print(f"\n🔥 ULTRA-FILTERED SETUP (ALL RULES):")
            print(f"   - Signals: {len(ultra_filtered)} ({len(ultra_filtered)/len(self.df)*100:.1f}% of total)")
            print(f"   - Win Rate: {ultra_wr:.1f}%")
            print(f"   - Expected Value: VERY HIGH if WR > 60%")
    
    def save_results(self, coin_df, hour_df, day_df, month_df):
        """Save optimization results to file"""
        results = {
            'generated_at': datetime.now().isoformat(),
            'total_signals_analyzed': len(self.df),
            'top_coins': coin_df.head(15).to_dict('records'),
            'top_hours': hour_df.head(10).to_dict('records'),
            'top_days': day_df.to_dict('records'),
            'top_months': month_df.to_dict('records')
        }
        
        output_file = 'data/results/optimization_results.json'
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")

def main():
    """Main execution"""
    print("=" * 80)
    print("🔍 TRADING SETUP OPTIMIZATION ANALYZER")
    print("=" * 80)
    print()
    
    # Find latest results file
    results_dir = Path('data/backtest_results')
    results_files = list(results_dir.glob('intermediate_results_*.csv'))
    
    if not results_files:
        print("❌ No results files found in data/backtest_results/")
        return
    
    # Get largest file (most complete)
    latest_file = max(results_files, key=lambda x: int(x.stem.split('_')[2]))
    
    print(f"📂 Analyzing: {latest_file}")
    print()
    
    # Initialize analyzer
    analyzer = OptimizationAnalyzer(latest_file)
    
    # Run all analyses
    coin_df = analyzer.analyze_by_coin(min_signals=5)
    hour_df, day_df, month_df = analyzer.analyze_by_timeframe()
    analyzer.analyze_by_risk_reward()
    analyzer.find_optimal_combinations(coin_df, hour_df)
    analyzer.find_edge_setups()
    analyzer.generate_trading_rules(coin_df, hour_df)
    
    # Save results
    analyzer.save_results(coin_df, hour_df, day_df, month_df)
    
    print("\n" + "=" * 80)
    print("✅ OPTIMIZATION ANALYSIS COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()
