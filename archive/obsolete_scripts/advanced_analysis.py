"""
Advanced Signal Analysis Scripts

Comprehensive analysis tools for Meta Signals performance evaluation.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import sys

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from data.binance_data import BinanceDataFetcher

class AdvancedSignalAnalyzer:
    """Advanced analysis tools for signal performance"""
    
    def __init__(self, results_file: str = None):
        """Initialize with backtest results"""
        if results_file is None:
            # Find latest results file
            results_dir = "data/backtest_results"
            files = [f for f in os.listdir(results_dir) if f.startswith("meta_signals_backtest_detailed_")]
            if files:
                results_file = os.path.join(results_dir, sorted(files)[-1])
        
        if results_file and os.path.exists(results_file):
            self.results_df = pd.read_csv(results_file)
            print(f"📊 Loaded {len(self.results_df)} backtest results from {os.path.basename(results_file)}")
        else:
            self.results_df = pd.DataFrame()
            print("❌ No results file found. Run backtest first.")
        
        self.binance = BinanceDataFetcher()
    
    def analyze_market_conditions(self):
        """Analyze market conditions when signals were generated"""
        print("\\n🌊 MARKET CONDITIONS ANALYSIS")
        print("=" * 50)
        
        if self.results_df.empty:
            return
        
        # Group by date
        self.results_df['signal_date'] = pd.to_datetime(self.results_df['signal_time']).dt.date
        daily_performance = self.results_df.groupby('signal_date').agg({
            'final_outcome': lambda x: (x.str.startswith('TARGET')).sum(),
            'signal_id': 'count',
            'max_profit_pct': 'mean',
            'max_drawdown_pct': 'mean'
        }).rename(columns={
            'final_outcome': 'wins',
            'signal_id': 'total_signals',
            'max_profit_pct': 'avg_profit',
            'max_drawdown_pct': 'avg_drawdown'
        })
        
        daily_performance['win_rate'] = (daily_performance['wins'] / daily_performance['total_signals']) * 100
        
        print("📅 Daily Performance Summary:")
        print(f"Best Day: {daily_performance['win_rate'].max():.1f}% win rate ({daily_performance.loc[daily_performance['win_rate'].idxmax()].name})")
        print(f"Worst Day: {daily_performance['win_rate'].min():.1f}% win rate ({daily_performance.loc[daily_performance['win_rate'].idxmin()].name})")
        print(f"Average Daily Win Rate: {daily_performance['win_rate'].mean():.1f}%")
        
        # Top performing days
        print("\\n🏆 Top 5 Performing Days:")
        top_days = daily_performance.nlargest(5, 'win_rate')
        for date, row in top_days.iterrows():
            print(f"  {date}: {row['win_rate']:.1f}% ({row['wins']}/{row['total_signals']}) signals")
        
        return daily_performance
    
    def analyze_timeframe_performance(self):
        """Analyze performance by timeframe"""
        print("\\n⏰ TIMEFRAME ANALYSIS")
        print("=" * 50)
        
        if self.results_df.empty:
            return
        
        # Extract timeframe from signal data (you'll need to add this to backtest results)
        # For now, analyze by time of day
        self.results_df['signal_hour'] = pd.to_datetime(self.results_df['signal_time']).dt.hour
        
        hourly_performance = self.results_df.groupby('signal_hour').agg({
            'final_outcome': lambda x: (x.str.startswith('TARGET')).sum(),
            'signal_id': 'count',
            'target1_minutes': 'mean',
            'max_profit_pct': 'mean'
        }).rename(columns={
            'final_outcome': 'wins',
            'signal_id': 'total_signals',
            'target1_minutes': 'avg_target_time',
            'max_profit_pct': 'avg_profit'
        })
        
        hourly_performance['win_rate'] = (hourly_performance['wins'] / hourly_performance['total_signals']) * 100
        
        print("🕐 Performance by Hour of Day:")
        best_hours = hourly_performance.nlargest(5, 'win_rate')
        for hour, row in best_hours.iterrows():
            if row['total_signals'] >= 3:  # Only show hours with meaningful data
                print(f"  {hour:02d}:00 - {row['win_rate']:.1f}% win rate ({row['wins']}/{row['total_signals']}) - Avg time to target: {row['avg_target_time']:.0f}min")
        
        return hourly_performance
    
    def analyze_symbol_correlations(self):
        """Analyze correlations between different symbols"""
        print("\\n🔗 SYMBOL CORRELATION ANALYSIS")
        print("=" * 50)
        
        if self.results_df.empty:
            return
        
        # Performance by symbol
        symbol_performance = self.results_df.groupby('symbol').agg({
            'final_outcome': lambda x: (x.str.startswith('TARGET')).sum(),
            'signal_id': 'count',
            'max_profit_pct': 'mean',
            'max_drawdown_pct': 'mean',
            'target1_minutes': 'mean'
        }).rename(columns={
            'final_outcome': 'wins',
            'signal_id': 'total_signals',
            'max_profit_pct': 'avg_profit',
            'max_drawdown_pct': 'avg_drawdown',
            'target1_minutes': 'avg_target_time'
        })
        
        symbol_performance['win_rate'] = (symbol_performance['wins'] / symbol_performance['total_signals']) * 100
        
        # Filter symbols with at least 5 signals
        significant_symbols = symbol_performance[symbol_performance['total_signals'] >= 5]
        
        print("🎯 Symbol Performance (5+ signals):")
        top_symbols = significant_symbols.nlargest(10, 'win_rate')
        for symbol, row in top_symbols.iterrows():
            print(f"  {symbol:6}: {row['win_rate']:5.1f}% ({row['wins']:2}/{row['total_signals']:2}) - " +
                  f"Avg Profit: {row['avg_profit']:5.2f}% - Avg Time: {row['avg_target_time']:4.0f}min")
        
        return symbol_performance
    
    def analyze_profit_distribution(self):
        """Analyze profit/loss distribution"""
        print("\\n💰 PROFIT/LOSS DISTRIBUTION")
        print("=" * 50)
        
        if self.results_df.empty:
            return
        
        # Winning trades analysis
        winners = self.results_df[self.results_df['final_outcome'].str.startswith('TARGET')]
        losers = self.results_df[self.results_df['final_outcome'] == 'STOP_LOSS']
        
        print(f"📈 Winning Trades Analysis ({len(winners)} trades):")
        if not winners.empty:
            print(f"  Average Profit: {winners['max_profit_pct'].mean():.2f}%")
            print(f"  Median Profit: {winners['max_profit_pct'].median():.2f}%")
            print(f"  Best Profit: {winners['max_profit_pct'].max():.2f}%")
            print(f"  Worst Profit: {winners['max_profit_pct'].min():.2f}%")
            
            # Profit distribution
            profit_ranges = [0, 1, 2, 3, 5, 10]
            for i in range(len(profit_ranges)-1):
                count = ((winners['max_profit_pct'] >= profit_ranges[i]) & 
                        (winners['max_profit_pct'] < profit_ranges[i+1])).sum()
                pct = (count / len(winners)) * 100
                print(f"  {profit_ranges[i]:.0f}-{profit_ranges[i+1]:.0f}%: {count} trades ({pct:.1f}%)")
        
        print(f"\\n📉 Losing Trades Analysis ({len(losers)} trades):")
        if not losers.empty:
            print(f"  Average Loss: {losers['max_drawdown_pct'].mean():.2f}%")
            print(f"  Median Loss: {losers['max_drawdown_pct'].median():.2f}%")
            print(f"  Worst Loss: {losers['max_drawdown_pct'].min():.2f}%")
            print(f"  Best Loss: {losers['max_drawdown_pct'].max():.2f}%")
    
    def analyze_timing_patterns(self):
        """Analyze timing patterns for successful trades"""
        print("\\n⏱️ TIMING PATTERN ANALYSIS")
        print("=" * 50)
        
        if self.results_df.empty:
            return
        
        # Filter successful trades
        winners = self.results_df[self.results_df['final_outcome'].str.startswith('TARGET')]
        
        if winners.empty:
            print("No winning trades to analyze")
            return
        
        # Time to target analysis
        target_times = winners['target1_minutes'].dropna()
        
        print("🎯 Time to Target Analysis:")
        print(f"  Average: {target_times.mean():.1f} minutes ({target_times.mean()/60:.1f} hours)")
        print(f"  Median: {target_times.median():.1f} minutes")
        print(f"  Fastest: {target_times.min():.1f} minutes")
        print(f"  Slowest: {target_times.max():.1f} minutes")
        
        # Time distribution
        time_ranges = [0, 30, 60, 120, 360, 720, float('inf')]
        time_labels = ["0-30min", "30min-1h", "1-2h", "2-6h", "6-12h", "12h+"]
        
        print("\\n⏰ Time Distribution:")
        for i, label in enumerate(time_labels):
            if i < len(time_ranges) - 1:
                count = ((target_times >= time_ranges[i]) & 
                        (target_times < time_ranges[i+1])).sum()
            else:
                count = (target_times >= time_ranges[i]).sum()
            
            pct = (count / len(target_times)) * 100
            print(f"  {label:8}: {count:3} trades ({pct:4.1f}%)")
    
    def generate_trading_insights(self):
        """Generate actionable trading insights"""
        print("\\n🧠 TRADING INSIGHTS & RECOMMENDATIONS")
        print("=" * 60)
        
        if self.results_df.empty:
            return
        
        insights = []
        
        # Overall performance insight
        total_signals = len(self.results_df)
        wins = (self.results_df['final_outcome'].str.startswith('TARGET')).sum()
        win_rate = (wins / total_signals) * 100
        
        if win_rate > 50:
            insights.append(f"✅ Strong Strategy: {win_rate:.1f}% win rate indicates profitable signals")
        elif win_rate > 40:
            insights.append(f"⚖️ Moderate Strategy: {win_rate:.1f}% win rate with proper risk management")
        else:
            insights.append(f"⚠️ Challenging Strategy: {win_rate:.1f}% win rate requires careful position sizing")
        
        # Profit factor insight
        winners = self.results_df[self.results_df['final_outcome'].str.startswith('TARGET')]
        losers = self.results_df[self.results_df['final_outcome'] == 'STOP_LOSS']
        
        if not winners.empty and not losers.empty:
            total_profit = winners['max_profit_pct'].sum()
            total_loss = abs(losers['max_drawdown_pct'].sum())
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            
            if profit_factor > 1.5:
                insights.append(f"💰 Excellent Profit Factor: {profit_factor:.2f} - Strong edge in markets")
            elif profit_factor > 1.0:
                insights.append(f"💵 Positive Profit Factor: {profit_factor:.2f} - Strategy is profitable")
            else:
                insights.append(f"📉 Negative Profit Factor: {profit_factor:.2f} - Review strategy")
        
        # Best symbols insight
        symbol_performance = self.results_df.groupby('symbol').agg({
            'final_outcome': lambda x: (x.str.startswith('TARGET')).sum(),
            'signal_id': 'count'
        })
        symbol_performance['win_rate'] = (symbol_performance['final_outcome'] / symbol_performance['signal_id']) * 100
        significant_symbols = symbol_performance[symbol_performance['signal_id'] >= 5]
        
        if not significant_symbols.empty:
            best_symbol = significant_symbols['win_rate'].idxmax()
            best_rate = significant_symbols.loc[best_symbol, 'win_rate']
            insights.append(f"🎯 Best Performing Symbol: {best_symbol} ({best_rate:.1f}% win rate)")
        
        # Timing insight
        if not winners.empty:
            avg_time = winners['target1_minutes'].mean()
            if avg_time < 120:  # Less than 2 hours
                insights.append(f"⚡ Fast Signals: Average {avg_time:.0f}min to target - Good for scalping")
            elif avg_time < 480:  # Less than 8 hours
                insights.append(f"📈 Medium-term Signals: Average {avg_time/60:.1f}h to target - Suitable for day trading")
            else:
                insights.append(f"📊 Long-term Signals: Average {avg_time/60:.1f}h to target - Swing trading approach")
        
        # Print insights
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        print("\\n📋 RECOMMENDED ACTIONS:")
        print("1. Focus position sizing on symbols with >50% win rate")
        print("2. Set realistic profit targets based on historical timing")
        print("3. Use proper risk management (1-2% risk per trade)")
        print("4. Monitor market conditions during best performing hours")
        
        return insights
    
    def export_analysis_report(self):
        """Export comprehensive analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"data/analysis/comprehensive_analysis_{timestamp}.txt"
        
        os.makedirs("data/analysis", exist_ok=True)
        
        # Capture all analysis output
        import io
        import contextlib
        
        output = io.StringIO()
        
        with contextlib.redirect_stdout(output):
            self.analyze_market_conditions()
            self.analyze_timeframe_performance()
            self.analyze_symbol_correlations()
            self.analyze_profit_distribution()
            self.analyze_timing_patterns()
            self.generate_trading_insights()
        
        # Save to file
        with open(report_file, 'w') as f:
            f.write(output.getvalue())
        
        print(f"\\n📄 Analysis report saved to: {report_file}")
        return report_file

def run_comprehensive_analysis():
    """Run all analysis modules"""
    print("🔍 COMPREHENSIVE SIGNAL ANALYSIS")
    print("=" * 60)
    
    analyzer = AdvancedSignalAnalyzer()
    
    if analyzer.results_df.empty:
        print("❌ No backtest results found. Run backtest first.")
        return
    
    # Run all analysis modules
    analyzer.analyze_market_conditions()
    analyzer.analyze_timeframe_performance() 
    analyzer.analyze_symbol_correlations()
    analyzer.analyze_profit_distribution()
    analyzer.analyze_timing_patterns()
    analyzer.generate_trading_insights()
    
    # Export report
    analyzer.export_analysis_report()
    
    print("\\n✅ Comprehensive analysis complete!")

if __name__ == "__main__":
    run_comprehensive_analysis()