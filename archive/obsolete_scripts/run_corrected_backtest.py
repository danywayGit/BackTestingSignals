"""
Run Full Backtest on Corrected Signals

This script runs the complete backtest on all signals with corrected LONG/SHORT labels.
"""

from full_backtest import MetaSignalsBacktester

print("=" * 80)
print("🚀 RUNNING FULL BACKTEST ON CORRECTED SIGNALS")
print("=" * 80)
print()

# Initialize backtester
bt = MetaSignalsBacktester()

# Load corrected signals
bt.load_signals('data/signals/meta_signals_corrected_20251013_195448.csv')

print()
print("🚀 Starting full backtest on ALL signals...")
print("   This will take several minutes...")
print()

# Run full backtest (no limit on signals)
bt.run_full_backtest()

# Print comprehensive summary
bt.print_final_report()

# Save results
print()
print("💾 Saving results...")
results_file = bt.save_results('corrected_full_backtest')

print()
print("=" * 80)
print("✅ BACKTEST COMPLETE!")
print("=" * 80)
print(f"Results saved to: {results_file}")
print()
print("Next step: Run optimization analysis on corrected data")
