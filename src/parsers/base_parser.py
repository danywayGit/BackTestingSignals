"""
Signal Parser Base Class

This module contains the base class for all signal parsers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Signal:
    """Represents a trading signal"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'LONG', 'SHORT'
    entry_price: float
    stop_loss: float = None
    take_profit: float = None
    quantity: float = None
    timestamp: datetime = None
    source: str = None
    confidence: float = None
    additional_info: Dict[str, Any] = None


class SignalParser(ABC):
    """Base class for signal parsers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        
    @abstractmethod
    def parse_message(self, message: str) -> List[Signal]:
        """
        Parse a message and extract trading signals
        
        Args:
            message: Raw message text
            
        Returns:
            List of Signal objects
        """
        pass
    
    @abstractmethod
    def validate_signal(self, signal: Signal) -> bool:
        """
        Validate if a signal is properly formatted
        
        Args:
            signal: Signal object to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass