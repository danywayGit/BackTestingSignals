"""
Discord Signal Parser for Meta Signals

This module handles parsing signals from Discord channels, specifically 
designed for Meta Signals format with symbol, timeframe, strategy version,
entry, targets, and stop loss information.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_parser import SignalParser, Signal


class DiscordMetaSignalsParser(SignalParser):
    """Parser specifically designed for Meta Signals Discord format"""
    
    def __init__(self, source_name: str = "meta_signals_discord"):
        super().__init__(source_name)
        
        # Meta Signals specific patterns
        self.patterns = {
            # Meta Signals format: 📈 ETH | USDT @ $3,825.25 - 2H - 1.1.1
            'meta_signal_header': r'📈\s*([A-Z]{2,10})\s*\|\s*USDT\s*@\s*\$?([\d,]+\.?\d*)\s*-\s*([^\-]+)\s*-\s*([\d\.]+)',
            
            # Traditional symbol patterns (fallback)
            'symbol': r'(?:^|\s|📈|📉|🚀)([A-Z]{2,10})[/\s]?(?:USDT|USD|BTC|ETH|PERP)?(?:\s|$)',
            
            # Timeframe patterns (e.g., 2H, 45M, 1D)
            'timeframe': r'\b(\d+[HMS]|\d+[DWM]|Daily|Hourly)\b',
            
            # Strategy version (Meta Signals format like 1.1.1)
            'strategy_version': r'(\d+\.\d+\.\d+)',
            
            # Meta Signals target patterns
            'target1': r'Target\s*1:\s*\$?([\d,]+\.?\d*)',
            'target2': r'Target\s*2:\s*\$?([\d,]+\.?\d*)',
            'target3': r'Target\s*3:\s*\$?([\d,]+\.?\d*)',
            
            # Meta Signals stop loss patterns
            'stop_loss': r'SL\s*Close\s*(?:Below|Above):\s*\$?([\d,]+\.?\d*)',
            
            # Entry price patterns (fallback)
            'entry': r'(?:Entry|ENTRY|Enter|@)\s*\$?([\d,]+\.?\d*)',
            
            # Signal direction indicators
            'direction': r'📈|📉|🟢|🔴',
            
            # Risk-reward patterns
            'risk_reward': r'\(RR\s*([\d\.]+)\)',
            
            # Additional patterns for other formats
            'action': r'\b(LONG|SHORT|BUY|SELL)\b',
            'algo_mention': r'(?:Algo|Algorithm|AI)[:\s]*([^\n\r]+?)(?:\n|$)',
        }
    
    def parse_message(self, message: str, message_id: str = None, 
                     timestamp: datetime = None, attachments: List[Dict] = None) -> List[Signal]:
        """
        Parse a Discord message for Meta Signals trading signals
        
        Args:
            message: Raw Discord message text
            message_id: Discord message ID
            timestamp: Message timestamp
            attachments: List of message attachments (for Algo version images)
            
        Returns:
            List of Signal objects found in the message
        """
        original_message = message
        message_upper = message.upper().strip()
        signals = []
        
        # Try Meta Signals specific format first
        meta_match = re.search(self.patterns['meta_signal_header'], original_message)
        
        if meta_match:
            # Parse Meta Signals format
            symbol = meta_match.group(1)
            entry_price = float(meta_match.group(2).replace(',', ''))
            timeframe = meta_match.group(3).strip()
            strategy_version = meta_match.group(4)
            
            # Extract targets
            target1_match = re.search(self.patterns['target1'], message)
            target2_match = re.search(self.patterns['target2'], message)
            target3_match = re.search(self.patterns['target3'], message)
            
            # Extract stop loss
            sl_match = re.search(self.patterns['stop_loss'], message)
            
            # Determine direction (📈 = LONG, 📉 = SHORT)
            direction_match = re.search(self.patterns['direction'], original_message)
            action = 'LONG' if '📈' in original_message else ('SHORT' if '📉' in original_message else 'UNKNOWN')
            
            # Build additional info dictionary
            additional_info = {
                'raw_message': original_message,
                'message_id': message_id,
                'timeframe': timeframe,
                'strategy_version': strategy_version,
                'target1': float(target1_match.group(1).replace(',', '')) if target1_match else None,
                'target2': float(target2_match.group(1).replace(',', '')) if target2_match else None,
                'target3': float(target3_match.group(1).replace(',', '')) if target3_match else None,
                'signal_direction': direction_match.group(0) if direction_match else None,
                'has_attachments': bool(attachments),
                'attachment_count': len(attachments) if attachments else 0,
                'format_type': 'meta_signals'
            }
            
            # Process attachments for Algo version images
            if attachments:
                additional_info['attachments'] = []
                for attachment in attachments:
                    att_info = {
                        'filename': attachment.get('filename', ''),
                        'url': attachment.get('url', ''),
                        'content_type': attachment.get('content_type', ''),
                        'size': attachment.get('size', 0)
                    }
                    additional_info['attachments'].append(att_info)
            
            signal = Signal(
                symbol=self._clean_symbol(symbol),
                action=action,
                entry_price=entry_price,
                stop_loss=float(sl_match.group(1).replace(',', '')) if sl_match else None,
                take_profit=float(target1_match.group(1).replace(',', '')) if target1_match else None,
                timestamp=timestamp or datetime.now(),
                source=self.source_name,
                additional_info=additional_info
            )
            
            if self.validate_signal(signal):
                signals.append(signal)
        
        else:
            # Fallback to generic parsing for other formats
            # Extract basic signal components
            symbol_match = re.search(self.patterns['symbol'], message_upper)
            timeframe_match = re.search(self.patterns['timeframe'], message_upper)
            strategy_match = re.search(self.patterns['strategy_version'], original_message, re.IGNORECASE)
            action_match = re.search(self.patterns['action'], message_upper)
            entry_match = re.search(self.patterns['entry'], message_upper)
            
            # Extract targets (fallback patterns)
            target1_match = re.search(self.patterns['target1'], message_upper)
            target2_match = re.search(self.patterns['target2'], message_upper)
            target3_match = re.search(self.patterns['target3'], message_upper)
            
            # Extract stop loss (fallback patterns)
            sl_match = re.search(self.patterns['stop_loss'], message_upper)
            
            # Extract additional info
            direction_match = re.search(self.patterns['direction'], original_message)
            algo_match = re.search(self.patterns['algo_mention'], original_message, re.IGNORECASE)
            
            if symbol_match and entry_match:
                # Build additional info dictionary
                additional_info = {
                    'raw_message': original_message,
                    'message_id': message_id,
                    'timeframe': timeframe_match.group(1) if timeframe_match else None,
                    'strategy_version': strategy_match.group(1).strip() if strategy_match else None,
                    'target1': float(target1_match.group(1).replace(',', '')) if target1_match else None,
                    'target2': float(target2_match.group(1).replace(',', '')) if target2_match else None,
                    'target3': float(target3_match.group(1).replace(',', '')) if target3_match else None,
                    'signal_direction': direction_match.group(0) if direction_match else None,
                    'algo_version': algo_match.group(1).strip() if algo_match else None,
                    'has_attachments': bool(attachments),
                    'attachment_count': len(attachments) if attachments else 0,
                    'format_type': 'generic'
                }
                
                # Process attachments for Algo version images
                if attachments:
                    additional_info['attachments'] = []
                    for attachment in attachments:
                        att_info = {
                            'filename': attachment.get('filename', ''),
                            'url': attachment.get('url', ''),
                            'content_type': attachment.get('content_type', ''),
                            'size': attachment.get('size', 0)
                        }
                        additional_info['attachments'].append(att_info)
                
                signal = Signal(
                    symbol=self._clean_symbol(symbol_match.group(1)),
                    action=action_match.group(1) if action_match else 'UNKNOWN',
                    entry_price=float(entry_match.group(1).replace(',', '')),
                    stop_loss=float(sl_match.group(1).replace(',', '')) if sl_match else None,
                    take_profit=float(target1_match.group(1).replace(',', '')) if target1_match else None,
                    timestamp=timestamp or datetime.now(),
                    source=self.source_name,
                    additional_info=additional_info
                )
                
                if self.validate_signal(signal):
                    signals.append(signal)
        
        return signals
    
    def _clean_symbol(self, symbol: str) -> str:
        """Clean and standardize symbol format"""
        # Remove common suffixes and standardize
        symbol = symbol.upper().replace('/', '').replace('-', '')
        
        # Add USDT if no quote currency specified
        if not any(quote in symbol for quote in ['USDT', 'USD', 'BTC', 'ETH']):
            if len(symbol) <= 5:  # Likely base currency only
                symbol += 'USDT'
        
        return symbol
    
    def validate_signal(self, signal: Signal) -> bool:
        """
        Validate if a signal has required fields for Meta Signals format
        
        Args:
            signal: Signal object to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (
            signal.symbol and
            signal.entry_price and
            signal.entry_price > 0 and
            len(signal.symbol) >= 3  # Minimum symbol length
        )
    
    def extract_all_targets(self, signal: Signal) -> List[float]:
        """
        Extract all target prices from a signal
        
        Args:
            signal: Signal object with additional_info containing targets
            
        Returns:
            List of target prices
        """
        targets = []
        if signal.additional_info:
            for i in range(1, 4):  # target1, target2, target3
                target_key = f'target{i}'
                if target_key in signal.additional_info and signal.additional_info[target_key]:
                    targets.append(signal.additional_info[target_key])
        
        return targets
    
    def get_signal_summary(self, signal: Signal) -> Dict[str, Any]:
        """
        Get a comprehensive summary of a parsed signal
        
        Args:
            signal: Signal object
            
        Returns:
            Dictionary with signal summary
        """
        targets = self.extract_all_targets(signal)
        
        summary = {
            'symbol': signal.symbol,
            'action': signal.action,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'targets': targets,
            'timeframe': signal.additional_info.get('timeframe') if signal.additional_info else None,
            'strategy_version': signal.additional_info.get('strategy_version') if signal.additional_info else None,
            'algo_version': signal.additional_info.get('algo_version') if signal.additional_info else None,
            'timestamp': signal.timestamp,
            'has_image_algo': signal.additional_info.get('has_attachments', False) if signal.additional_info else False
        }
        
        return summary