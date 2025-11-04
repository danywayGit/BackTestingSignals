"""Fix symbol names in the signals CSV by adding USDT suffix where needed"""
import pandas as pd

# Load the CSV
df = pd.read_csv('data/signals/meta_signals_export_20251104_024600.csv')

print(f"Total signals: {len(df)}")
print(f"LONG signals: {(df['action'] == 'LONG').sum()}")
print(f"SHORT signals: {(df['action'] == 'SHORT').sum()}")

# Find symbols that don't end with USDT
problematic = df[~df['symbol'].str.endswith('USDT')]
print(f"\nSymbols needing USDT suffix: {len(problematic)}")
print(f"Unique symbols: {list(problematic['symbol'].unique())}")

# Fix symbols by adding USDT suffix
df['symbol'] = df['symbol'].apply(lambda x: x if x.endswith('USDT') else f"{x}USDT")

# Verify the fix
still_problematic = df[~df['symbol'].str.endswith('USDT')]
print(f"\nAfter fix - symbols still problematic: {len(still_problematic)}")

# Save the fixed CSV
output_file = 'data/signals/meta_signals_export_20251104_024600_fixed.csv'
df.to_csv(output_file, index=False)
print(f"\n✅ Fixed CSV saved to: {output_file}")
print(f"Total signals: {len(df)}")
print(f"Sample symbols: {list(df['symbol'].unique()[:10])}")
