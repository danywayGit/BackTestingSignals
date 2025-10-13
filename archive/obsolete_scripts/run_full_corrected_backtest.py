"""
Full Backtest on All Corrected Signals

Runs complete backtest on all 989 signals with corrected LONG/SHORT labels.
This will take several minutes as it processes all signals against historical data.
"""

from full_backtest import MetaSignalsBacktester
import sys

print("=" * 80)
print("🚀 FULL BACKTEST - ALL CORRECTED SIGNALS")
print("=" * 80)
print()

# Initialize
backtester = MetaSignalsBacktester()

# Load corrected signals
print("📂 Loading corrected signals...")
backtester.load_signals('data/signals/meta_signals_corrected_20251013_195448.csv')

print()
print("🚀 Starting FULL backtest on ALL 989 signals...")
print("   This will process:")
print("   - 773 LONG signals (78.2%)")
print("   - 216 SHORT signals (21.8%)")
print()
print("   ⏱️  Estimated time: 5-10 minutes")
print("   📊 Processing...")
print()

# Run full backtest (no signal limit)
try:
    backtester.run_full_backtest(max_signals=None)
    
    # Save results
    print()
    print("💾 Saving results...")
    backtester.save_full_results()
    
    # Print final report
    print()
    backtester.print_final_report()
    
    print()
    print("=" * 80)
    print("✅ BACKTEST COMPLETE!")
    print("=" * 80)
    print()
    print("Results saved in data/backtest_results/")
    print("Next: Run SHORT analysis script")
    
except KeyboardInterrupt:
    print()
    print("⚠️  Backtest interrupted by user")
    print("Partial results may be saved")
    sys.exit(1)
except Exception as e:
    print()
    print(f"❌ Error during backtest: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
