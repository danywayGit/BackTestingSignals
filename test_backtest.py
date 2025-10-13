"""
Meta Signals Backtesting - Quick Test

Test the backtesting system on a sample of signals to validate functionality.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from data.binance_data import BinanceDataFetcher

def quick_backtest():
    """Run a quick backtest on recent signals"""
    
    print("🚀 Meta Signals Backtesting - Quick Test")
    print("=" * 50)
    
    # Find the latest signals file
    signals_dir = "data/signals"
    if not os.path.exists(signals_dir):
        print("❌ No signals directory found!")
        print("Please run the signal extraction first.")
        return
    
    # Get latest signals file
    signal_files = [f for f in os.listdir(signals_dir) if f.endswith('.csv')]
    if not signal_files:
        print("❌ No signal files found!")
        return
    
    latest_file = sorted(signal_files)[-1]
    signals_path = os.path.join(signals_dir, latest_file)
    
    print(f"📊 Loading signals from: {latest_file}")
    
    # Load signals
    signals_df = pd.read_csv(signals_path)
    print(f"✅ Loaded {len(signals_df)} signals")
    
    # Initialize Binance data fetcher
    print("🔗 Connecting to Binance...")
    binance = BinanceDataFetcher()
    
    # Test with first 5 signals
    test_signals = signals_df.head(5)
    
    print(f"\\n🧪 Testing {len(test_signals)} signals...")
    print("-" * 40)
    
    results = []
    
    for idx, (_, signal) in enumerate(test_signals.iterrows(), 1):
        print(f"[{idx}/5] Testing {signal['symbol']} {signal['action']} @ ${signal['entry_price']}")
        
        try:
            # Check signal outcome
            outcome = binance.check_signal_outcome(signal.to_dict(), lookforward_hours=72)
            results.append(outcome)
            
            # Print result
            final_outcome = outcome['final_outcome']
            
            if final_outcome == 'TARGET1':
                mins = outcome.get('target1_minutes', 0)
                print(f"  ✅ Hit Target 1 in {mins:.0f} minutes")
            elif final_outcome == 'TARGET2':
                mins = outcome.get('target2_minutes', 0)
                print(f"  🎯 Hit Target 2 in {mins:.0f} minutes")
            elif final_outcome == 'TARGET3':
                mins = outcome.get('target3_minutes', 0)
                print(f"  🚀 Hit Target 3 in {mins:.0f} minutes")
            elif final_outcome == 'STOP_LOSS':
                mins = outcome.get('stop_loss_minutes', 0)
                print(f"  ❌ Hit Stop Loss in {mins:.0f} minutes")
            elif final_outcome == 'ONGOING':
                print(f"  ⏸️ Still ongoing (no targets/SL hit)")
            else:
                print(f"  ⚠️ No data available")
            
            # Show profit/drawdown
            if outcome['max_profit_pct'] > 0:
                print(f"     Max Profit: +{outcome['max_profit_pct']:.2f}%")
            if outcome['max_drawdown_pct'] < 0:
                print(f"     Max Drawdown: {outcome['max_drawdown_pct']:.2f}%")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
        
        print()
    
    # Quick summary
    print("📊 Quick Test Results:")
    print("-" * 30)
    
    valid_results = [r for r in results if r['final_outcome'] != 'NO_DATA']
    
    if valid_results:
        wins = sum(1 for r in valid_results if r['final_outcome'].startswith('TARGET'))
        losses = sum(1 for r in valid_results if r['final_outcome'] == 'STOP_LOSS')
        ongoing = sum(1 for r in valid_results if r['final_outcome'] == 'ONGOING')
        
        total = len(valid_results)
        winrate = (wins / total) * 100 if total > 0 else 0
        
        print(f"Wins: {wins}")
        print(f"Losses: {losses}")
        print(f"Ongoing: {ongoing}")
        print(f"Win Rate: {winrate:.1f}%")
        
        # Average times
        target_times = []
        sl_times = []
        
        for r in valid_results:
            if r.get('target1_minutes'):
                target_times.append(r['target1_minutes'])
            if r.get('target2_minutes'):
                target_times.append(r['target2_minutes'])
            if r.get('target3_minutes'):
                target_times.append(r['target3_minutes'])
            if r.get('stop_loss_minutes'):
                sl_times.append(r['stop_loss_minutes'])
        
        if target_times:
            print(f"Avg Target Time: {np.mean(target_times):.1f} minutes")
        if sl_times:
            print(f"Avg SL Time: {np.mean(sl_times):.1f} minutes")
    
    print("\\n✅ Quick test complete!")
    print("\\nReady for full backtesting? Run:")
    print("python full_backtest.py")

if __name__ == "__main__":
    quick_backtest()