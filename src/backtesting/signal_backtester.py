"""
Signal Backtesting Engine

Comprehensive backtesting system for Meta Signals using Binance historical data.
Analyzes target hits, stop losses, timing, and performance metrics.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import csv
import time

# Import our data fetcher
import sys
sys.path.append('..')
from data.binance_data import BinanceDataFetcher

class SignalBacktester:
    """Comprehensive signal backtesting engine"""
    
    def __init__(self, signals_file: str):
        """
        Initialize backtester with signals
        
        Args:
            signals_file: Path to CSV file with signals
        """
        self.signals_file = signals_file
        self.binance = BinanceDataFetcher()
        self.results = []
        self.load_signals()
        
        # Create results directory
        self.results_dir = "data/backtest_results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_signals(self):
        """Load signals from CSV file"""
        print(f"📊 Loading signals from: {self.signals_file}")
        
        try:
            self.signals_df = pd.read_csv(self.signals_file)
            print(f"✅ Loaded {len(self.signals_df)} signals")
            
            # Show signal distribution
            symbol_counts = self.signals_df['symbol'].value_counts()
            print(f"🎯 Top symbols: {dict(symbol_counts.head())}")
            
        except Exception as e:
            print(f"❌ Error loading signals: {e}")
            self.signals_df = pd.DataFrame()
    
    def backtest_signal(self, signal: Dict, lookforward_hours: int = 72) -> Dict:
        """
        Backtest a single signal
        
        Args:
            signal: Signal dictionary
            lookforward_hours: Hours to look forward for targets/SL
            
        Returns:
            Detailed backtest result
        """
        print(f"🔍 Testing {signal['symbol']} {signal['action']} @ ${signal['entry_price']}")
        
        # Use our Binance data fetcher
        outcome = self.binance.check_signal_outcome(signal, lookforward_hours)
        
        # Add additional analysis
        outcome.update({
            'timeframe': signal.get('timeframe', 'Unknown'),
            'strategy_version': signal.get('strategy_version', 'Unknown'),
            'signal_timestamp': signal['timestamp']
        })
        
        # Calculate risk/reward ratios
        entry = float(signal['entry_price'])
        sl = float(signal['stop_loss']) if signal['stop_loss'] else None
        t1 = float(signal['target1']) if signal['target1'] else None
        t2 = float(signal['target2']) if signal['target2'] else None
        t3 = float(signal['target3']) if signal['target3'] else None
        
        if sl and entry:
            if signal['action'] == 'LONG':
                risk_amount = abs(entry - sl)
                if t1: outcome['rr_target1'] = abs(t1 - entry) / risk_amount
                if t2: outcome['rr_target2'] = abs(t2 - entry) / risk_amount
                if t3: outcome['rr_target3'] = abs(t3 - entry) / risk_amount
            else:  # SHORT
                risk_amount = abs(sl - entry)
                if t1: outcome['rr_target1'] = abs(entry - t1) / risk_amount
                if t2: outcome['rr_target2'] = abs(entry - t2) / risk_amount
                if t3: outcome['rr_target3'] = abs(entry - t3) / risk_amount
        
        return outcome
    
    def run_backtest(self, max_signals: Optional[int] = None, 
                    lookforward_hours: int = 72) -> List[Dict]:
        """
        Run backtest on all signals
        
        Args:
            max_signals: Limit number of signals to test (for quick testing)
            lookforward_hours: Hours to look forward for each signal
            
        Returns:
            List of backtest results
        """
        print("🚀 Starting comprehensive backtest...")
        print("=" * 50)
        
        signals_to_test = self.signals_df.head(max_signals) if max_signals else self.signals_df
        total_signals = len(signals_to_test)
        
        print(f"📊 Testing {total_signals} signals")
        print(f"⏰ Lookforward period: {lookforward_hours} hours")
        print()
        
        results = []
        
        for idx, (_, signal) in enumerate(signals_to_test.iterrows(), 1):
            print(f"[{idx}/{total_signals}] ", end="")
            
            try:
                result = self.backtest_signal(signal.to_dict(), lookforward_hours)
                results.append(result)
                
                # Show quick result
                outcome = result['final_outcome']
                symbol = result['symbol']
                
                if outcome == 'TARGET1':
                    print(f"✅ {symbol} hit T1 in {result.get('target1_minutes', 0):.0f}min")
                elif outcome == 'TARGET2':
                    print(f"🎯 {symbol} hit T2 in {result.get('target2_minutes', 0):.0f}min")
                elif outcome == 'TARGET3':
                    print(f"🚀 {symbol} hit T3 in {result.get('target3_minutes', 0):.0f}min")
                elif outcome == 'STOP_LOSS':
                    print(f"❌ {symbol} hit SL in {result.get('stop_loss_minutes', 0):.0f}min")
                else:
                    print(f"⏸️ {symbol} ongoing/no data")
                
                # Progress update every 20 signals
                if idx % 20 == 0:
                    wins = sum(1 for r in results if r['final_outcome'].startswith('TARGET'))
                    losses = sum(1 for r in results if r['final_outcome'] == 'STOP_LOSS')
                    winrate = (wins / len(results)) * 100 if results else 0
                    print(f"\\n📈 Progress: {idx}/{total_signals} | Winrate: {winrate:.1f}% | Wins: {wins} | Losses: {losses}\\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
            
            # Small delay to avoid rate limits
            time.sleep(0.1)
        
        self.results = results
        return results
    
    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.results:
            return {}
        
        print("📊 Calculating performance metrics...")
        
        # Basic counts
        total_signals = len(self.results)
        valid_results = [r for r in self.results if r['final_outcome'] != 'NO_DATA']
        
        target1_hits = sum(1 for r in valid_results if r['hit_target1'])
        target2_hits = sum(1 for r in valid_results if r['hit_target2']) 
        target3_hits = sum(1 for r in valid_results if r['hit_target3'])
        stop_loss_hits = sum(1 for r in valid_results if r['hit_stop_loss'])
        
        # Win rates
        total_valid = len(valid_results)
        if total_valid > 0:
            target1_rate = (target1_hits / total_valid) * 100
            target2_rate = (target2_hits / total_valid) * 100
            target3_rate = (target3_hits / total_valid) * 100
            stop_loss_rate = (stop_loss_hits / total_valid) * 100
            
            # Overall win rate (any target hit)
            wins = sum(1 for r in valid_results if r['final_outcome'].startswith('TARGET'))
            overall_winrate = (wins / total_valid) * 100
        else:
            target1_rate = target2_rate = target3_rate = stop_loss_rate = overall_winrate = 0
        
        # Timing analysis
        target_times = []
        sl_times = []
        
        for r in valid_results:
            if r['target1_minutes']:
                target_times.append(r['target1_minutes'])
            if r['target2_minutes']:
                target_times.append(r['target2_minutes'])
            if r['target3_minutes']:
                target_times.append(r['target3_minutes'])
            if r['stop_loss_minutes']:
                sl_times.append(r['stop_loss_minutes'])
        
        # Profit/Loss analysis
        profits = [r['max_profit_pct'] for r in valid_results if r['max_profit_pct'] > 0]
        drawdowns = [abs(r['max_drawdown_pct']) for r in valid_results if r['max_drawdown_pct'] < 0]
        
        # Risk/Reward analysis
        rr_ratios = []
        for r in valid_results:
            for target in ['rr_target1', 'rr_target2', 'rr_target3']:
                if target in r and r[target]:
                    rr_ratios.append(r[target])
        
        metrics = {
            'total_signals': total_signals,
            'valid_signals': total_valid,
            'data_coverage': (total_valid / total_signals) * 100 if total_signals > 0 else 0,
            
            # Win rates
            'overall_winrate': overall_winrate,
            'target1_rate': target1_rate,
            'target2_rate': target2_rate,
            'target3_rate': target3_rate,
            'stop_loss_rate': stop_loss_rate,
            
            # Counts
            'target1_hits': target1_hits,
            'target2_hits': target2_hits,
            'target3_hits': target3_hits,
            'stop_loss_hits': stop_loss_hits,
            'wins': wins,
            'losses': stop_loss_hits,
            
            # Timing (in minutes)
            'avg_target_time': np.mean(target_times) if target_times else 0,
            'median_target_time': np.median(target_times) if target_times else 0,
            'avg_sl_time': np.mean(sl_times) if sl_times else 0,
            'median_sl_time': np.median(sl_times) if sl_times else 0,
            'fastest_target': min(target_times) if target_times else 0,
            'slowest_target': max(target_times) if target_times else 0,
            
            # Profit/Loss
            'avg_max_profit': np.mean(profits) if profits else 0,
            'max_profit_achieved': max(profits) if profits else 0,
            'avg_max_drawdown': np.mean(drawdowns) if drawdowns else 0,
            'worst_drawdown': max(drawdowns) if drawdowns else 0,
            
            # Risk/Reward
            'avg_risk_reward': np.mean(rr_ratios) if rr_ratios else 0,
            'best_risk_reward': max(rr_ratios) if rr_ratios else 0,
            
            # Symbol performance
            'symbol_performance': self._analyze_by_symbol(),
            'timeframe_performance': self._analyze_by_timeframe(),
            'strategy_performance': self._analyze_by_strategy()
        }
        
        return metrics
    
    def _analyze_by_symbol(self) -> Dict:
        """Analyze performance by symbol"""
        symbol_stats = {}
        
        for r in self.results:
            symbol = r['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {
                    'total': 0, 'wins': 0, 'losses': 0,
                    'target_times': [], 'sl_times': []
                }
            
            symbol_stats[symbol]['total'] += 1
            
            if r['final_outcome'].startswith('TARGET'):
                symbol_stats[symbol]['wins'] += 1
                if r.get('target1_minutes'):
                    symbol_stats[symbol]['target_times'].append(r['target1_minutes'])
            elif r['final_outcome'] == 'STOP_LOSS':
                symbol_stats[symbol]['losses'] += 1
                if r.get('stop_loss_minutes'):
                    symbol_stats[symbol]['sl_times'].append(r['stop_loss_minutes'])
        
        # Calculate win rates and averages
        for symbol, stats in symbol_stats.items():
            if stats['total'] > 0:
                stats['winrate'] = (stats['wins'] / stats['total']) * 100
                stats['avg_target_time'] = np.mean(stats['target_times']) if stats['target_times'] else 0
                stats['avg_sl_time'] = np.mean(stats['sl_times']) if stats['sl_times'] else 0
        
        return symbol_stats
    
    def _analyze_by_timeframe(self) -> Dict:
        """Analyze performance by timeframe"""
        tf_stats = {}
        
        for r in self.results:
            tf = r.get('timeframe', 'Unknown')
            if tf not in tf_stats:
                tf_stats[tf] = {'total': 0, 'wins': 0, 'losses': 0}
            
            tf_stats[tf]['total'] += 1
            if r['final_outcome'].startswith('TARGET'):
                tf_stats[tf]['wins'] += 1
            elif r['final_outcome'] == 'STOP_LOSS':
                tf_stats[tf]['losses'] += 1
        
        # Calculate win rates
        for tf, stats in tf_stats.items():
            if stats['total'] > 0:
                stats['winrate'] = (stats['wins'] / stats['total']) * 100
        
        return tf_stats
    
    def _analyze_by_strategy(self) -> Dict:
        """Analyze performance by strategy version"""
        strategy_stats = {}
        
        for r in self.results:
            strategy = r.get('strategy_version', 'Unknown')
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'total': 0, 'wins': 0, 'losses': 0}
            
            strategy_stats[strategy]['total'] += 1
            if r['final_outcome'].startswith('TARGET'):
                strategy_stats[strategy]['wins'] += 1
            elif r['final_outcome'] == 'STOP_LOSS':
                strategy_stats[strategy]['losses'] += 1
        
        # Calculate win rates
        for strategy, stats in strategy_stats.items():
            if stats['total'] > 0:
                stats['winrate'] = (stats['wins'] / stats['total']) * 100
        
        return strategy_stats
    
    def save_results(self, filename_prefix: str = "backtest") -> str:
        """Save detailed results to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(self.results_dir, filename)
        
        if not self.results:
            print("❌ No results to save")
            return ""
        
        # Convert results to DataFrame and save
        df = pd.DataFrame(self.results)
        df.to_csv(filepath, index=False)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print comprehensive performance summary"""
        if not self.results:
            print("❌ No results to summarize")
            return
        
        metrics = self.calculate_metrics()
        
        print("\\n🎯 SIGNAL BACKTEST RESULTS")
        print("=" * 60)
        
        print(f"📊 Dataset Overview:")
        print(f"  Total Signals: {metrics['total_signals']}")
        print(f"  Valid Data: {metrics['valid_signals']} ({metrics['data_coverage']:.1f}%)")
        print()
        
        print(f"🏆 Performance Metrics:")
        print(f"  Overall Win Rate: {metrics['overall_winrate']:.1f}%")
        print(f"  Target 1 Hit Rate: {metrics['target1_rate']:.1f}%")
        print(f"  Target 2 Hit Rate: {metrics['target2_rate']:.1f}%")
        print(f"  Target 3 Hit Rate: {metrics['target3_rate']:.1f}%")
        print(f"  Stop Loss Hit Rate: {metrics['stop_loss_rate']:.1f}%")
        print()
        
        print(f"⏰ Timing Analysis:")
        print(f"  Average Target Time: {metrics['avg_target_time']:.1f} minutes")
        print(f"  Median Target Time: {metrics['median_target_time']:.1f} minutes")
        print(f"  Fastest Target: {metrics['fastest_target']:.1f} minutes")
        print(f"  Average SL Time: {metrics['avg_sl_time']:.1f} minutes")
        print()
        
        print(f"💰 Profit/Loss Analysis:")
        print(f"  Average Max Profit: {metrics['avg_max_profit']:.2f}%")
        print(f"  Best Profit: {metrics['max_profit_achieved']:.2f}%")
        print(f"  Average Max Drawdown: {metrics['avg_max_drawdown']:.2f}%")
        print(f"  Worst Drawdown: {metrics['worst_drawdown']:.2f}%")
        print()
        
        print(f"⚖️ Risk/Reward:")
        print(f"  Average R/R Ratio: {metrics['avg_risk_reward']:.2f}")
        print(f"  Best R/R Ratio: {metrics['best_risk_reward']:.2f}")
        print()
        
        # Top performing symbols
        symbol_perf = metrics['symbol_performance']
        top_symbols = sorted(symbol_perf.items(), 
                           key=lambda x: (x[1]['winrate'], x[1]['total']), 
                           reverse=True)[:10]
        
        print(f"🎯 Top Performing Symbols:")
        for symbol, stats in top_symbols:
            if stats['total'] >= 5:  # Only show symbols with 5+ signals
                print(f"  {symbol}: {stats['winrate']:.1f}% ({stats['wins']}/{stats['total']})")
        print()
        
        # Timeframe analysis
        tf_perf = metrics['timeframe_performance']
        print(f"📅 Performance by Timeframe:")
        for tf, stats in sorted(tf_perf.items(), key=lambda x: x[1]['winrate'], reverse=True):
            print(f"  {tf}: {stats['winrate']:.1f}% ({stats['wins']}/{stats['total']})")
        print()
        
        print("✅ Backtest Complete!")


if __name__ == "__main__":
    # Quick test run
    signals_file = "../../data/signals/meta_signals_quick_20251013_025440.csv"
    
    if os.path.exists(signals_file):
        backtester = SignalBacktester(signals_file)
        
        # Run backtest on first 10 signals for testing
        print("🧪 Running test backtest on first 10 signals...")
        results = backtester.run_backtest(max_signals=10)
        
        # Show summary
        backtester.print_summary()
        
        # Save results
        backtester.save_results("test_backtest")
    else:
        print(f"❌ Signals file not found: {signals_file}")
        print("Please run the signal extraction first!")