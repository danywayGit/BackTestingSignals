"""
Basic Backtesting Engine

This module provides a simple backtesting framework for trading signals.
"""

from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
from ..parsers.base_parser import Signal


class BacktestEngine:
    """Simple backtesting engine for trading signals"""
    
    def __init__(self, initial_capital: float = 10000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.performance_metrics = {}
        
    def execute_signal(self, signal: Signal, current_price: float) -> Dict[str, Any]:
        """
        Execute a trading signal
        
        Args:
            signal: Signal object to execute
            current_price: Current market price
            
        Returns:
            Dictionary with execution results
        """
        result = {
            'signal': signal,
            'executed': False,
            'reason': '',
            'pnl': 0
        }
        
        if signal.action in ['BUY', 'LONG', 'ENTER']:
            result = self._open_position(signal, current_price)
        elif signal.action in ['SELL', 'SHORT']:
            result = self._close_position(signal, current_price)
            
        return result
    
    def _open_position(self, signal: Signal, current_price: float) -> Dict[str, Any]:
        """Open a new position"""
        position_size = self._calculate_position_size(signal, current_price)
        
        if position_size <= 0:
            return {
                'signal': signal,
                'executed': False,
                'reason': 'Insufficient capital',
                'pnl': 0
            }
        
        # Calculate cost including commission
        cost = position_size * current_price * (1 + self.commission)
        
        if cost > self.current_capital:
            return {
                'signal': signal,
                'executed': False,
                'reason': 'Insufficient capital',
                'pnl': 0
            }
        
        # Open position
        self.positions[signal.symbol] = {
            'size': position_size,
            'entry_price': current_price,
            'signal': signal,
            'timestamp': datetime.now()
        }
        
        self.current_capital -= cost
        
        return {
            'signal': signal,
            'executed': True,
            'reason': 'Position opened',
            'cost': cost,
            'position_size': position_size
        }
    
    def _close_position(self, signal: Signal, current_price: float) -> Dict[str, Any]:
        """Close an existing position"""
        if signal.symbol not in self.positions:
            return {
                'signal': signal,
                'executed': False,
                'reason': 'No open position',
                'pnl': 0
            }
        
        position = self.positions[signal.symbol]
        position_size = position['size']
        entry_price = position['entry_price']
        
        # Calculate PnL
        gross_pnl = position_size * (current_price - entry_price)
        commission_cost = position_size * current_price * self.commission
        net_pnl = gross_pnl - commission_cost
        
        # Close position
        proceeds = position_size * current_price * (1 - self.commission)
        self.current_capital += proceeds
        
        # Record trade
        trade = {
            'symbol': signal.symbol,
            'entry_price': entry_price,
            'exit_price': current_price,
            'size': position_size,
            'pnl': net_pnl,
            'entry_time': position['timestamp'],
            'exit_time': datetime.now(),
            'signal': signal
        }
        
        self.trade_history.append(trade)
        del self.positions[signal.symbol]
        
        return {
            'signal': signal,
            'executed': True,
            'reason': 'Position closed',
            'pnl': net_pnl,
            'proceeds': proceeds
        }
    
    def _calculate_position_size(self, signal: Signal, current_price: float) -> float:
        """Calculate position size based on risk management"""
        if signal.quantity:
            return signal.quantity
        
        # Simple position sizing: use 10% of available capital
        available_capital = self.current_capital * 0.1
        position_size = available_capital / current_price
        
        return position_size
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.trade_history:
            return {'total_trades': 0, 'total_pnl': 0, 'win_rate': 0}
        
        total_pnl = sum(trade['pnl'] for trade in self.trade_history)
        winning_trades = [trade for trade in self.trade_history if trade['pnl'] > 0]
        
        metrics = {
            'total_trades': len(self.trade_history),
            'winning_trades': len(winning_trades),
            'losing_trades': len(self.trade_history) - len(winning_trades),
            'win_rate': len(winning_trades) / len(self.trade_history) * 100,
            'total_pnl': total_pnl,
            'total_return': (total_pnl / self.initial_capital) * 100,
            'current_capital': self.current_capital,
            'open_positions': len(self.positions)
        }
        
        return metrics