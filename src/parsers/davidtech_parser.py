"""
DaviddTech Telegram Signal Parser

Parses trading signals from DaviddTech Telegram channel format:
- Action: SHORT or LONG (🔴🔴 SHORT 🔴🔴 or 🟢🟢 LONG 🟢🟢)
- Pair: ADAUSDT format
- Entry price
- Take Profit (TP)
- Stop Loss (SL)
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime
from .base_parser import SignalParser


class DaviddTechParser(SignalParser):
    """Parser for DaviddTech Telegram signal format"""
    
    def __init__(self, source_name: str = "davidtech_telegram"):
        super().__init__(source_name)
        
        # DaviddTech specific patterns
        self.patterns = {
            # Action: 🔴🔴 SHORT 🔴🔴 or 🟢🟢 LONG 🟢🟢 (with optional **bold**)
            'action': r'🔴🔴\s*\*?\*?(SHORT)\*?\*?\s*🔴🔴|🟢🟢\s*\*?\*?(LONG)\*?\*?\s*🟢🟢',
            
            # Pair: ADAUSDT, BTCUSDT, etc. (with optional **bold**)
            'pair': r'👜\s*\*?\*?PAIR:\*?\*?\s*([A-Z]+USDT)',
            
            # Entry: ✔️ ENTRY: 0.5488 (with optional **bold**)
            'entry': r'✔️\s*\*?\*?ENTRY:\*?\*?\s*([\d.]+)',
            
            # Take Profit: 🟢 TP: 0.5152 (with optional **bold**)
            'tp': r'🟢\s*\*?\*?TP:\*?\*?\s*([\d.]+)',
            
            # Stop Loss: 🔴 SL: 0.5671 (with optional **bold**)
            'sl': r'🔴\s*\*?\*?SL:\*?\*?\s*([\d.]+)',
            
            # Strategy name (optional): ADA SuperF 1h - Chateau (with optional **bold**)
            'strategy': r'strategy:\s*\*?\*?([^\n\*]+)\*?\*?',
        }
    
    def parse_message(self, message: str, message_id: Optional[int] = None, timestamp: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Parse a DaviddTech signal message.
        
        Args:
            message: Message text to parse
            message_id: Message ID (optional)
            timestamp: Message timestamp
            
        Returns:
            Dictionary with signal data or None if not a valid signal
        """
        if not message:
            return None
        
        # Must contain action indicator (check for pattern, not exact match)
        if not (('🔴🔴' in message and 'SHORT' in message) or ('🟢🟢' in message and 'LONG' in message)):
            return None
        
        signal = {
            'source': self.source_name,
            'timestamp': timestamp.isoformat() if timestamp else datetime.now().isoformat(),
            'message_id': message_id,
            'raw_message': message
        }
        
        # Extract action (SHORT or LONG)
        action_match = re.search(self.patterns['action'], message)
        if action_match:
            signal['action'] = action_match.group(1) if action_match.group(1) else action_match.group(2)
        else:
            return None  # Must have action
        
        # Extract pair/symbol
        pair_match = re.search(self.patterns['pair'], message)
        if pair_match:
            signal['symbol'] = pair_match.group(1)
        else:
            return None  # Must have symbol
        
        # Extract entry price
        entry_match = re.search(self.patterns['entry'], message)
        if entry_match:
            signal['entry'] = float(entry_match.group(1))
        else:
            return None  # Must have entry
        
        # Extract take profit
        tp_match = re.search(self.patterns['tp'], message)
        if tp_match:
            signal['take_profit'] = float(tp_match.group(1))
            signal['target1'] = float(tp_match.group(1))  # Map to standard format
        
        # Extract stop loss
        sl_match = re.search(self.patterns['sl'], message)
        if sl_match:
            signal['stop_loss'] = float(sl_match.group(1))
        
        # Extract strategy name (optional)
        strategy_match = re.search(self.patterns['strategy'], message)
        if strategy_match:
            signal['strategy'] = strategy_match.group(1).strip()
        
        # Calculate risk-reward ratio if we have all prices
        if 'entry' in signal and 'take_profit' in signal and 'stop_loss' in signal:
            entry = signal['entry']
            tp = signal['take_profit']
            sl = signal['stop_loss']
            
            if signal['action'] == 'LONG':
                risk = entry - sl
                reward = tp - entry
            else:  # SHORT
                risk = sl - entry
                reward = entry - tp
            
            if risk > 0:
                signal['risk_reward'] = round(reward / risk, 2)
        
        # Add metadata
        signal['timeframe'] = self._extract_timeframe(message)
        
        # Validation - must have minimum required fields
        required_fields = ['action', 'symbol', 'entry']
        if not all(field in signal for field in required_fields):
            return None
        
        return signal
    
    def _extract_timeframe(self, message: str) -> str:
        """
        Extract timeframe from strategy name if present.
        Examples: "1h", "4h", "15m"
        """
        # Look for common timeframe patterns
        tf_patterns = [
            r'\b(\d+h)\b',  # 1h, 4h, etc.
            r'\b(\d+m)\b',  # 15m, 30m, etc.
            r'\b(\d+d)\b',  # 1d, etc.
        ]
        
        for pattern in tf_patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).upper()
        
        return 'UNKNOWN'
    
    def validate_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Validate a parsed signal.
        
        Args:
            signal: Parsed signal dictionary
            
        Returns:
            True if valid, False otherwise
        """
        if not signal:
            return False
        
        # Required fields
        required = ['action', 'symbol', 'entry']
        if not all(field in signal for field in required):
            return False
        
        # Action must be LONG or SHORT
        if signal.get('action') not in ['LONG', 'SHORT']:
            return False
        
        # Symbol must end with USDT
        if not signal.get('symbol', '').endswith('USDT'):
            return False
        
        # Entry must be positive
        if signal.get('entry', 0) <= 0:
            return False
        
        # If TP/SL present, validate direction
        entry = signal.get('entry')
        tp = signal.get('take_profit')
        sl = signal.get('stop_loss')
        
        if tp and sl and entry:
            if signal['action'] == 'LONG':
                # LONG: TP > entry > SL
                if not (tp > entry > sl):
                    return False
            else:  # SHORT
                # SHORT: SL > entry > TP
                if not (sl > entry > tp):
                    return False
        
        return True
