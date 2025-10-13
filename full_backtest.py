"""
Full Meta Signals Backtesting

Comprehensive backtesting of all Meta Signals with detailed analytics.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import csv

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from data.binance_data import BinanceDataFetcher

class MetaSignalsBacktester:
    """Comprehensive Meta Signals backtesting system"""
    
    def __init__(self):
        self.binance = BinanceDataFetcher()
        self.results = []
        self.signals_df = None
        
        # Create results directory
        self.results_dir = "data/backtest_results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_signals(self, filename: str = None):
        """Load signals from CSV file"""
        if filename is None:
            # Find latest signals file
            signals_dir = "data/signals"
            signal_files = [f for f in os.listdir(signals_dir) if f.endswith('.csv')]
            if not signal_files:
                raise FileNotFoundError("No signal files found!")
            filename = sorted(signal_files)[-1]
            filepath = os.path.join(signals_dir, filename)
        else:
            filepath = filename
        
        print(f"📊 Loading signals from: {os.path.basename(filepath)}")
        self.signals_df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(self.signals_df)} signals")
        
        # Show distribution
        print(f"🎯 Signal distribution:")
        print(f"  Actions: {dict(self.signals_df['action'].value_counts())}")
        print(f"  Top symbols: {dict(self.signals_df['symbol'].value_counts().head())}")
        print(f"  Timeframes: {dict(self.signals_df['timeframe'].value_counts())}")
        print()
    
    def run_full_backtest(self, max_signals: int = None, 
                         lookforward_hours: int = 72,
                         batch_size: int = 50):
        """
        Run comprehensive backtest on all signals
        
        Args:
            max_signals: Limit number of signals (None for all)
            lookforward_hours: Hours to look forward for targets/SL
            batch_size: Process signals in batches for progress updates
        """
        if self.signals_df is None:
            self.load_signals()
        
        signals_to_test = self.signals_df.head(max_signals) if max_signals else self.signals_df
        total_signals = len(signals_to_test)
        
        print("🚀 Starting FULL Meta Signals Backtesting")
        print("=" * 60)
        print(f"📊 Testing {total_signals} signals")
        print(f"⏰ Lookforward period: {lookforward_hours} hours")
        print(f"📦 Batch size: {batch_size}")
        print()
        
        results = []
        batch_count = 0
        start_time = datetime.now()
        
        for idx, (_, signal) in enumerate(signals_to_test.iterrows(), 1):
            try:
                # Test signal
                result = self.binance.check_signal_outcome(signal.to_dict(), lookforward_hours)
                results.append(result)
                
                # Progress indicator
                if idx % 10 == 0:
                    print(f"⏳ Progress: {idx}/{total_signals} ({(idx/total_signals)*100:.1f}%)")
                
                # Batch summary
                if idx % batch_size == 0:
                    batch_count += 1
                    self._print_batch_summary(results[-batch_size:], batch_count, batch_size)
                
                # Save intermediate results every 100 signals
                if idx % 100 == 0:
                    self._save_intermediate_results(results, idx)
                
            except Exception as e:
                print(f"❌ Error on signal {idx}: {e}")
                continue
        
        # Final batch summary if needed
        remaining = len(results) % batch_size
        if remaining > 0:
            batch_count += 1
            self._print_batch_summary(results[-remaining:], batch_count, remaining)
        
        self.results = results
        
        elapsed = datetime.now() - start_time
        print(f"\\n⏱️ Backtesting completed in {elapsed}")
        print(f"✅ Successfully tested {len(results)} signals")
        
        return results
    
    def _print_batch_summary(self, batch_results: list, batch_num: int, batch_size: int):
        """Print summary for a batch of results"""
        valid_results = [r for r in batch_results if r['final_outcome'] != 'NO_DATA']
        
        if not valid_results:
            print(f"📦 Batch {batch_num}: No valid data")
            return
        
        wins = sum(1 for r in valid_results if r['final_outcome'].startswith('TARGET'))
        losses = sum(1 for r in valid_results if r['final_outcome'] == 'STOP_LOSS')
        ongoing = len(valid_results) - wins - losses
        
        winrate = (wins / len(valid_results)) * 100 if valid_results else 0
        
        print(f"📦 Batch {batch_num} ({batch_size} signals): " + 
              f"Win Rate: {winrate:.1f}% | " +
              f"Wins: {wins} | Losses: {losses} | Ongoing: {ongoing}")
    
    def _save_intermediate_results(self, results: list, count: int):
        """Save intermediate results"""
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"intermediate_results_{count}_{timestamp}.csv"
        filepath = os.path.join(self.results_dir, filename)
        
        df = pd.DataFrame(results)
        df.to_csv(filepath, index=False)
        print(f"💾 Saved intermediate results: {filename}")
    
    def calculate_comprehensive_metrics(self) -> dict:
        """Calculate detailed performance metrics"""
        if not self.results:
            return {}
        
        print("📊 Calculating comprehensive metrics...")
        
        # Filter valid results
        valid_results = [r for r in self.results if r['final_outcome'] != 'NO_DATA']
        total_signals = len(self.results)
        total_valid = len(valid_results)
        
        if total_valid == 0:
            return {'error': 'No valid results to analyze'}
        
        # Basic outcome counts
        target1_hits = sum(1 for r in valid_results if r['hit_target1'])
        target2_hits = sum(1 for r in valid_results if r['hit_target2'])
        target3_hits = sum(1 for r in valid_results if r['hit_target3'])
        stop_loss_hits = sum(1 for r in valid_results if r['hit_stop_loss'])
        
        # Win categories
        any_target_wins = sum(1 for r in valid_results if r['final_outcome'].startswith('TARGET'))
        target1_only = sum(1 for r in valid_results if r['final_outcome'] == 'TARGET1')
        target2_wins = sum(1 for r in valid_results if r['final_outcome'] == 'TARGET2')
        target3_wins = sum(1 for r in valid_results if r['final_outcome'] == 'TARGET3')
        
        # Win rates
        overall_winrate = (any_target_wins / total_valid) * 100
        target1_rate = (target1_hits / total_valid) * 100
        target2_rate = (target2_hits / total_valid) * 100
        target3_rate = (target3_hits / total_valid) * 100
        stop_loss_rate = (stop_loss_hits / total_valid) * 100
        
        # Timing analysis
        target_times = []
        sl_times = []
        target1_times = []
        target2_times = []
        target3_times = []
        
        for r in valid_results:
            if r.get('target1_minutes'):
                target_times.append(r['target1_minutes'])
                target1_times.append(r['target1_minutes'])
            if r.get('target2_minutes'):
                target_times.append(r['target2_minutes'])
                target2_times.append(r['target2_minutes'])
            if r.get('target3_minutes'):
                target_times.append(r['target3_minutes'])
                target3_times.append(r['target3_minutes'])
            if r.get('stop_loss_minutes'):
                sl_times.append(r['stop_loss_minutes'])
        
        # Profit/Loss analysis
        profits = [r['max_profit_pct'] for r in valid_results if r['max_profit_pct'] > 0]
        drawdowns = [abs(r['max_drawdown_pct']) for r in valid_results if r['max_drawdown_pct'] < 0]
        
        # Risk metrics
        all_profits = [r['max_profit_pct'] for r in valid_results]
        all_drawdowns = [r['max_drawdown_pct'] for r in valid_results]
        
        metrics = {
            # Dataset info
            'total_signals': total_signals,
            'valid_signals': total_valid,
            'data_coverage_pct': (total_valid / total_signals) * 100,
            
            # Win rates
            'overall_winrate_pct': overall_winrate,
            'target1_hit_rate_pct': target1_rate,
            'target2_hit_rate_pct': target2_rate,
            'target3_hit_rate_pct': target3_rate,
            'stop_loss_rate_pct': stop_loss_rate,
            
            # Outcome counts
            'total_wins': any_target_wins,
            'total_losses': stop_loss_hits,
            'target1_only_wins': target1_only,
            'target2_wins': target2_wins,
            'target3_wins': target3_wins,
            'target1_hits': target1_hits,
            'target2_hits': target2_hits,
            'target3_hits': target3_hits,
            
            # Timing metrics (minutes)
            'avg_target_time_min': np.mean(target_times) if target_times else 0,
            'median_target_time_min': np.median(target_times) if target_times else 0,
            'avg_target1_time_min': np.mean(target1_times) if target1_times else 0,
            'avg_target2_time_min': np.mean(target2_times) if target2_times else 0,
            'avg_target3_time_min': np.mean(target3_times) if target3_times else 0,
            'avg_sl_time_min': np.mean(sl_times) if sl_times else 0,
            'median_sl_time_min': np.median(sl_times) if sl_times else 0,
            'fastest_target_min': min(target_times) if target_times else 0,
            'slowest_target_min': max(target_times) if target_times else 0,
            
            # Profit/Loss metrics
            'avg_max_profit_pct': np.mean(profits) if profits else 0,
            'median_max_profit_pct': np.median(profits) if profits else 0,
            'best_profit_pct': max(profits) if profits else 0,
            'avg_max_drawdown_pct': np.mean(drawdowns) if drawdowns else 0,
            'median_max_drawdown_pct': np.median(drawdowns) if drawdowns else 0,
            'worst_drawdown_pct': max(drawdowns) if drawdowns else 0,
            
            # Risk metrics
            'profit_factor': (sum(p for p in all_profits if p > 0) / 
                            abs(sum(d for d in all_drawdowns if d < 0))) if any(d < 0 for d in all_drawdowns) else float('inf'),
            'sharpe_estimate': np.mean(all_profits) / np.std(all_profits) if len(all_profits) > 1 and np.std(all_profits) > 0 else 0,
            
            # Performance by categories
            'symbol_performance': self._analyze_by_symbol(),
            'timeframe_performance': self._analyze_by_timeframe(),
            'strategy_performance': self._analyze_by_strategy(),
            'action_performance': self._analyze_by_action()
        }
        
        return metrics
    
    def _analyze_by_symbol(self) -> dict:
        """Analyze performance by symbol"""
        symbol_stats = {}
        
        for r in self.results:
            if r['final_outcome'] == 'NO_DATA':
                continue
                
            symbol = r['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {
                    'total': 0, 'wins': 0, 'losses': 0,
                    'profits': [], 'drawdowns': [], 'target_times': []
                }
            
            stats = symbol_stats[symbol]
            stats['total'] += 1
            
            if r['final_outcome'].startswith('TARGET'):
                stats['wins'] += 1
                if r.get('target1_minutes'):
                    stats['target_times'].append(r['target1_minutes'])
            elif r['final_outcome'] == 'STOP_LOSS':
                stats['losses'] += 1
            
            if r['max_profit_pct'] > 0:
                stats['profits'].append(r['max_profit_pct'])
            if r['max_drawdown_pct'] < 0:
                stats['drawdowns'].append(abs(r['max_drawdown_pct']))
        
        # Calculate summary stats
        for symbol, stats in symbol_stats.items():
            if stats['total'] > 0:
                stats['winrate_pct'] = (stats['wins'] / stats['total']) * 100
                stats['avg_profit_pct'] = np.mean(stats['profits']) if stats['profits'] else 0
                stats['avg_drawdown_pct'] = np.mean(stats['drawdowns']) if stats['drawdowns'] else 0
                stats['avg_target_time_min'] = np.mean(stats['target_times']) if stats['target_times'] else 0
        
        return symbol_stats
    
    def _analyze_by_timeframe(self) -> dict:
        """Analyze performance by timeframe"""
        return self._analyze_by_category('timeframe')
    
    def _analyze_by_strategy(self) -> dict:
        """Analyze performance by strategy version"""
        return self._analyze_by_category('strategy_version')
    
    def _analyze_by_action(self) -> dict:
        """Analyze performance by action (LONG/SHORT)"""
        return self._analyze_by_category('action')
    
    def _analyze_by_category(self, category: str) -> dict:
        """Generic analysis by category"""
        category_stats = {}
        
        for r in self.results:
            if r['final_outcome'] == 'NO_DATA':
                continue
                
            cat_value = r.get(category, 'Unknown')
            if cat_value not in category_stats:
                category_stats[cat_value] = {'total': 0, 'wins': 0, 'losses': 0}
            
            category_stats[cat_value]['total'] += 1
            if r['final_outcome'].startswith('TARGET'):
                category_stats[cat_value]['wins'] += 1
            elif r['final_outcome'] == 'STOP_LOSS':
                category_stats[cat_value]['losses'] += 1
        
        # Calculate win rates
        for cat_value, stats in category_stats.items():
            if stats['total'] > 0:
                stats['winrate_pct'] = (stats['wins'] / stats['total']) * 100
        
        return category_stats
    
    def save_full_results(self, filename_prefix: str = "meta_signals_backtest"):
        """Save comprehensive results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = f"{filename_prefix}_detailed_{timestamp}.csv"
        results_path = os.path.join(self.results_dir, results_file)
        
        df = pd.DataFrame(self.results)
        df.to_csv(results_path, index=False)
        print(f"💾 Detailed results saved: {results_file}")
        
        # Save metrics summary
        metrics = self.calculate_comprehensive_metrics()
        metrics_file = f"{filename_prefix}_metrics_{timestamp}.json"
        metrics_path = os.path.join(self.results_dir, metrics_file)
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        print(f"📊 Metrics saved: {metrics_file}")
        
        return results_path, metrics_path
    
    def print_final_report(self):
        """Print comprehensive final report"""
        if not self.results:
            print("❌ No results to report")
            return
        
        metrics = self.calculate_comprehensive_metrics()
        
        print("\\n" + "="*80)
        print("🎯 META SIGNALS BACKTESTING - FINAL REPORT")
        print("="*80)
        
        print(f"\\n📊 DATASET OVERVIEW:")
        print(f"  Total Signals Tested: {metrics['total_signals']:,}")
        print(f"  Valid Data Coverage: {metrics['valid_signals']:,} ({metrics['data_coverage_pct']:.1f}%)")
        
        print(f"\\n🏆 OVERALL PERFORMANCE:")
        print(f"  Win Rate: {metrics['overall_winrate_pct']:.1f}%")
        print(f"  Total Wins: {metrics['total_wins']:,}")
        print(f"  Total Losses: {metrics['total_losses']:,}")
        print(f"  W/L Ratio: {metrics['total_wins']/max(metrics['total_losses'], 1):.2f}")
        
        print(f"\\n🎯 TARGET ANALYSIS:")
        print(f"  Target 1 Hit Rate: {metrics['target1_hit_rate_pct']:.1f}% ({metrics['target1_hits']:,} hits)")
        print(f"  Target 2 Hit Rate: {metrics['target2_hit_rate_pct']:.1f}% ({metrics['target2_hits']:,} hits)")
        print(f"  Target 3 Hit Rate: {metrics['target3_hit_rate_pct']:.1f}% ({metrics['target3_hits']:,} hits)")
        print(f"  Stop Loss Rate: {metrics['stop_loss_rate_pct']:.1f}% ({metrics['total_losses']:,} hits)")
        
        print(f"\\n⏰ TIMING ANALYSIS:")
        print(f"  Average Target Time: {metrics['avg_target_time_min']:.1f} minutes ({metrics['avg_target_time_min']/60:.1f} hours)")
        print(f"  Median Target Time: {metrics['median_target_time_min']:.1f} minutes")
        print(f"  Fastest Target: {metrics['fastest_target_min']:.1f} minutes")
        print(f"  Average Stop Loss Time: {metrics['avg_sl_time_min']:.1f} minutes ({metrics['avg_sl_time_min']/60:.1f} hours)")
        
        print(f"\\n💰 PROFIT/LOSS ANALYSIS:")
        print(f"  Average Max Profit: {metrics['avg_max_profit_pct']:.2f}%")
        print(f"  Best Profit: {metrics['best_profit_pct']:.2f}%")
        print(f"  Average Max Drawdown: {metrics['avg_max_drawdown_pct']:.2f}%")
        print(f"  Worst Drawdown: {metrics['worst_drawdown_pct']:.2f}%")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        
        # Top performing symbols
        symbol_perf = metrics['symbol_performance']
        top_symbols = sorted(symbol_perf.items(), 
                           key=lambda x: (x[1]['winrate_pct'], x[1]['total']), 
                           reverse=True)[:15]
        
        print(f"\\n🎯 TOP PERFORMING SYMBOLS:")
        for symbol, stats in top_symbols:
            if stats['total'] >= 10:  # Only show symbols with 10+ signals
                print(f"  {symbol:6}: {stats['winrate_pct']:5.1f}% ({stats['wins']:3}/{stats['total']:3}) " +
                      f"Avg Profit: {stats['avg_profit_pct']:5.2f}%")
        
        # Timeframe analysis
        tf_perf = metrics['timeframe_performance']
        print(f"\\n📅 PERFORMANCE BY TIMEFRAME:")
        for tf, stats in sorted(tf_perf.items(), key=lambda x: x[1]['winrate_pct'], reverse=True):
            print(f"  {tf:4}: {stats['winrate_pct']:5.1f}% ({stats['wins']:3}/{stats['total']:3})")
        
        # Action analysis
        action_perf = metrics['action_performance']
        print(f"\\n📈 PERFORMANCE BY ACTION:")
        for action, stats in sorted(action_perf.items(), key=lambda x: x[1]['winrate_pct'], reverse=True):
            print(f"  {action:5}: {stats['winrate_pct']:5.1f}% ({stats['wins']:3}/{stats['total']:3})")
        
        print("\\n" + "="*80)
        print("✅ BACKTESTING COMPLETE - Analysis ready for trading decisions!")
        print("="*80)


def main():
    """Main backtesting execution"""
    backtester = MetaSignalsBacktester()
    
    print("🔥 Meta Signals Comprehensive Backtesting")
    print("This will test ALL signals against historical Binance data")
    print()
    
    # Ask user for test size
    response = input("Test all 989 signals? (y/n) or enter number: ").strip().lower()
    
    if response == 'y' or response == 'yes':
        max_signals = None
        print("🚀 Testing ALL signals!")
    elif response == 'n' or response == 'no':
        max_signals = 100
        print("🧪 Testing first 100 signals")
    else:
        try:
            max_signals = int(response)
            print(f"🧪 Testing first {max_signals} signals")
        except:
            max_signals = 100
            print("🧪 Invalid input, testing first 100 signals")
    
    print()
    
    # Run backtesting
    backtester.run_full_backtest(max_signals=max_signals)
    
    # Calculate and save results
    backtester.save_full_results()
    
    # Print final report
    backtester.print_final_report()

if __name__ == "__main__":
    main()