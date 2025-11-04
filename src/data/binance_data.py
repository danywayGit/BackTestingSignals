"""
Binance Historical Data Fetcher

Fetches historical OHLCV data from Binance for backtesting signals.
Uses public API endpoints - no API keys required.
"""

import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Optional, Tuple

class BinanceDataFetcher:
    """Fetch historical data from Binance for backtesting"""
    
    def __init__(self):
        """Initialize Binance client (public API only)"""
        self.client = Client()  # No API key needed for historical data
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_kline_data(self, symbol: str, start_time: datetime, end_time: datetime, 
                      interval: str = "1m") -> pd.DataFrame:
        """
        Fetch kline/candlestick data from Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            start_time: Start datetime
            end_time: End datetime  
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            
        Returns:
            DataFrame with OHLCV data
        """
        print(f"📊 Fetching {symbol} data from {start_time} to {end_time}")
        
        # Check cache first
        cache_key = f"{symbol}_{interval}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.csv")
        
        if os.path.exists(cache_file):
            print(f"💾 Loading from cache: {cache_file}")
            return pd.read_csv(cache_file, parse_dates=['timestamp'])
        
        try:
            # Convert to millisecond timestamps
            start_ts = int(start_time.timestamp() * 1000)
            end_ts = int(end_time.timestamp() * 1000)
            
            # Fetch klines
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_ts,
                end_str=end_ts
            )
            
            if not klines:
                print(f"⚠️ No data found for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # Clean up data types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            # Cache the data
            df.to_csv(cache_file, index=False)
            print(f"✅ Cached data to: {cache_file}")
            
            # Rate limiting
            time.sleep(0.1)
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return pd.DataFrame()
    
    def check_signal_outcome(self, signal: Dict, lookforward_hours: int = 72) -> Dict:
        """
        Check if a signal hit its targets or stop loss
        
        Args:
            signal: Signal dictionary with entry, targets, stop loss
            lookforward_hours: How many hours to look forward from signal time
            
        Returns:
            Dictionary with outcome analysis
        """
        # Only add USDT if not already present
        symbol = signal['symbol'] if signal['symbol'].endswith('USDT') else signal['symbol'] + 'USDT'
        entry_price = float(signal['entry_price'])
        stop_loss = float(signal['stop_loss']) if signal['stop_loss'] else None
        target1 = float(signal['target1']) if signal['target1'] else None
        target2 = float(signal['target2']) if signal['target2'] else None
        target3 = float(signal['target3']) if signal['target3'] else None
        action = signal['action']
        
        # Parse signal timestamp (ensure timezone-aware)
        signal_time = pd.to_datetime(signal['timestamp'])
        if signal_time.tz is None:
            signal_time = signal_time.tz_localize('UTC')
        end_time = signal_time + timedelta(hours=lookforward_hours)
        
        # Fetch data
        df = self.get_kline_data(symbol, signal_time, end_time, interval="1m")
        
        if df.empty:
            return {
                'signal_id': signal['message_id'],
                'symbol': signal['symbol'],
                'status': 'NO_DATA',
                'entry_price': entry_price,
                'outcome': 'NO_DATA'
            }
        
        # Filter data after signal time (ensure timezone-aware comparison)
        if hasattr(signal_time, 'tz_localize') and signal_time.tz is None:
            signal_time = signal_time.tz_localize('UTC')
        elif isinstance(signal_time, str):
            signal_time = pd.to_datetime(signal_time, utc=True)
        
        # Ensure DataFrame timestamp is timezone-aware
        if df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        
        df = df[df['timestamp'] >= signal_time].copy()
        if df.empty:
            return {
                'signal_id': signal['message_id'],
                'symbol': signal['symbol'],
                'status': 'NO_DATA_AFTER_SIGNAL',
                'entry_price': entry_price,
                'outcome': 'NO_DATA'
            }
        
        outcome = {
            'signal_id': signal['message_id'],
            'symbol': signal['symbol'],
            'action': action,
            'signal_time': signal_time,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target1': target1,
            'target2': target2,
            'target3': target3,
            'status': 'ACTIVE',
            'outcome': 'ONGOING',
            'hit_target1': False,
            'hit_target2': False,
            'hit_target3': False,
            'hit_stop_loss': False,
            'target1_time': None,
            'target2_time': None,
            'target3_time': None,
            'stop_loss_time': None,
            'target1_minutes': None,
            'target2_minutes': None,
            'target3_minutes': None,
            'stop_loss_minutes': None,
            'max_profit_pct': 0,
            'max_drawdown_pct': 0,
            'final_outcome': 'ONGOING'
        }
        
        # Check each candle
        for idx, row in df.iterrows():
            timestamp = row['timestamp']
            high = row['high']
            low = row['low']
            
            minutes_elapsed = (timestamp - signal_time).total_seconds() / 60
            
            if action == 'LONG':
                # Calculate profit/loss percentages
                profit_pct = ((high - entry_price) / entry_price) * 100
                drawdown_pct = ((low - entry_price) / entry_price) * 100
                
                # Update max profit and drawdown
                outcome['max_profit_pct'] = max(outcome['max_profit_pct'], profit_pct)
                outcome['max_drawdown_pct'] = min(outcome['max_drawdown_pct'], drawdown_pct)
                
                # Check stop loss first (if hit, position closes)
                if stop_loss and low <= stop_loss and not outcome['hit_stop_loss']:
                    outcome['hit_stop_loss'] = True
                    outcome['stop_loss_time'] = timestamp
                    outcome['stop_loss_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'STOP_LOSS'
                    outcome['status'] = 'CLOSED'
                    break
                
                # Check targets (in order) - CLOSE POSITION when target is hit
                if target1 and high >= target1 and not outcome['hit_target1']:
                    outcome['hit_target1'] = True
                    outcome['target1_time'] = timestamp
                    outcome['target1_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'TARGET1'
                    # Continue to check for higher targets in same candle
                
                if target2 and high >= target2 and not outcome['hit_target2']:
                    outcome['hit_target2'] = True
                    outcome['target2_time'] = timestamp
                    outcome['target2_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'TARGET2'
                    # Continue to check for Target 3 in same candle
                
                if target3 and high >= target3 and not outcome['hit_target3']:
                    outcome['hit_target3'] = True
                    outcome['target3_time'] = timestamp
                    outcome['target3_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'TARGET3'
                    outcome['status'] = 'CLOSED'
                    break  # Exit on Target 3 (highest target)
                
                # If any target was hit in this candle, position should close
                if outcome['hit_target1'] or outcome['hit_target2'] or outcome['hit_target3']:
                    outcome['status'] = 'CLOSED'
                    break
            
            else:  # SHORT
                # Calculate profit/loss percentages (inverted for shorts)
                profit_pct = ((entry_price - low) / entry_price) * 100
                drawdown_pct = ((entry_price - high) / entry_price) * 100
                
                # Update max profit and drawdown
                outcome['max_profit_pct'] = max(outcome['max_profit_pct'], profit_pct)
                outcome['max_drawdown_pct'] = min(outcome['max_drawdown_pct'], drawdown_pct)
                
                # Check stop loss first
                if stop_loss and high >= stop_loss and not outcome['hit_stop_loss']:
                    outcome['hit_stop_loss'] = True
                    outcome['stop_loss_time'] = timestamp
                    outcome['stop_loss_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'STOP_LOSS'
                    outcome['status'] = 'CLOSED'
                    break
                
                # Check targets (in order) - CLOSE POSITION when target is hit
                if target1 and low <= target1 and not outcome['hit_target1']:
                    outcome['hit_target1'] = True
                    outcome['target1_time'] = timestamp
                    outcome['target1_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'TARGET1'
                    # Continue to check for higher targets in same candle
                
                if target2 and low <= target2 and not outcome['hit_target2']:
                    outcome['hit_target2'] = True
                    outcome['target2_time'] = timestamp
                    outcome['target2_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'TARGET2'
                    # Continue to check for Target 3 in same candle
                
                if target3 and low <= target3 and not outcome['hit_target3']:
                    outcome['hit_target3'] = True
                    outcome['target3_time'] = timestamp
                    outcome['target3_minutes'] = minutes_elapsed
                    outcome['final_outcome'] = 'TARGET3'
                    outcome['status'] = 'CLOSED'
                    break  # Exit on Target 3 (highest target)
                
                # If any target was hit in this candle, position should close
                if outcome['hit_target1'] or outcome['hit_target2'] or outcome['hit_target3']:
                    outcome['status'] = 'CLOSED'
                    break
        
        return outcome
    
    def get_symbol_list(self) -> List[str]:
        """Get list of available trading symbols"""
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] 
                      if s['status'] == 'TRADING' and s['symbol'].endswith('USDT')]
            return symbols
        except Exception as e:
            print(f"❌ Error getting symbols: {e}")
            return []
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol exists on Binance"""
        symbol_usdt = symbol + 'USDT'
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol_usdt)
            return True
        except:
            return False