"""
Telegram Signal Parser

This module handles parsing signals from Telegram channels.
"""

import re
from typing import List
from datetime import datetime
from .base_parser import SignalParser, Signal


class TelegramSignalParser(SignalParser):
    """Parser for Telegram trading signals"""
    
    def __init__(self, source_name: str = "telegram"):
        super().__init__(source_name)
        
        # Common patterns for signal parsing
        self.patterns = {
            'symbol': r'[#$]?([A-Z]{3,10})[/\s]?(?:USDT|USD|BTC|ETH)?',
            'action': r'\b(BUY|SELL|LONG|SHORT|ENTER)\b',
            'price': r'(?:ENTRY|PRICE|@|AT)[:\s]*(\d+\.?\d*)',
            'stop_loss': r'(?:SL|STOP.?LOSS|STOP)[:\s]*(\d+\.?\d*)',
            'take_profit': r'(?:TP|TAKE.?PROFIT|TARGET)[:\s]*(\d+\.?\d*)'
        }
    
    def parse_message(self, message: str) -> List[Signal]:
        """
        Parse a Telegram message for trading signals
        
        Args:
            message: Raw Telegram message text
            
        Returns:
            List of Signal objects found in the message
        """
        message = message.upper().strip()
        signals = []
        
        # Extract basic signal components
        symbol_match = re.search(self.patterns['symbol'], message)
        action_match = re.search(self.patterns['action'], message)
        price_match = re.search(self.patterns['price'], message)
        sl_match = re.search(self.patterns['stop_loss'], message)
        tp_match = re.search(self.patterns['take_profit'], message)
        
        if symbol_match and action_match and price_match:
            signal = Signal(
                symbol=symbol_match.group(1),
                action=action_match.group(1),
                entry_price=float(price_match.group(1)),
                stop_loss=float(sl_match.group(1)) if sl_match else None,
                take_profit=float(tp_match.group(1)) if tp_match else None,
                timestamp=datetime.now(),
                source=self.source_name,
                additional_info={'raw_message': message}
            )
            
            if self.validate_signal(signal):
                signals.append(signal)
        
        return signals
    
    def validate_signal(self, signal: Signal) -> bool:
        """
        Validate if a signal has required fields
        
        Args:
            signal: Signal object to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (
            signal.symbol and
            signal.action in ['BUY', 'SELL', 'LONG', 'SHORT', 'ENTER'] and
            signal.entry_price and
            signal.entry_price > 0
        )