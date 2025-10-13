"""
Data Storage System for Meta Signals

This module handles storing and retrieving extracted signals from Discord.
"""

import json
import csv
import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from ..parsers.base_parser import Signal


class SignalStorage:
    """Storage system for trading signals"""
    
    def __init__(self, data_dir: str = "data/signals"):
        """
        Initialize storage system
        
        Args:
            data_dir: Directory to store signal data
        """
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "signals.db")
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for signals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                symbol TEXT NOT NULL,
                action TEXT,
                entry_price REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                target1 REAL,
                target2 REAL,
                target3 REAL,
                timeframe TEXT,
                strategy_version TEXT,
                algo_version TEXT,
                timestamp DATETIME,
                source TEXT,
                channel_name TEXT,
                author TEXT,
                guild_name TEXT,
                message_url TEXT,
                raw_message TEXT,
                has_attachments BOOLEAN,
                attachment_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attachments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                filename TEXT,
                url TEXT,
                content_type TEXT,
                size INTEGER,
                local_path TEXT,
                FOREIGN KEY (signal_id) REFERENCES signals (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_signals(self, messages_data: List[Dict[str, Any]]) -> int:
        """
        Store extracted signals in database
        
        Args:
            messages_data: List of message data with signals
            
        Returns:
            Number of signals stored
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        signals_stored = 0
        
        for msg_data in messages_data:
            for signal in msg_data['signals']:
                # Extract additional info
                additional_info = signal.additional_info or {}
                
                # Insert signal
                cursor.execute('''
                    INSERT INTO signals (
                        message_id, symbol, action, entry_price, stop_loss, take_profit,
                        target1, target2, target3, timeframe, strategy_version, algo_version,
                        timestamp, source, channel_name, author, guild_name, message_url,
                        raw_message, has_attachments, attachment_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    additional_info.get('message_id'),
                    signal.symbol,
                    signal.action,
                    signal.entry_price,
                    signal.stop_loss,
                    signal.take_profit,
                    additional_info.get('target1'),
                    additional_info.get('target2'),
                    additional_info.get('target3'),
                    additional_info.get('timeframe'),
                    additional_info.get('strategy_version'),
                    additional_info.get('algo_version'),
                    signal.timestamp,
                    signal.source,
                    msg_data.get('channel_name'),
                    msg_data.get('author'),
                    msg_data.get('guild_name'),
                    msg_data.get('message_url'),
                    additional_info.get('raw_message'),
                    additional_info.get('has_attachments', False),
                    additional_info.get('attachment_count', 0)
                ))
                
                signal_id = cursor.lastrowid
                
                # Store attachments
                if additional_info.get('attachments'):
                    for attachment in additional_info['attachments']:
                        cursor.execute('''
                            INSERT INTO attachments (
                                signal_id, filename, url, content_type, size
                            ) VALUES (?, ?, ?, ?, ?)
                        ''', (
                            signal_id,
                            attachment.get('filename'),
                            attachment.get('url'),
                            attachment.get('content_type'),
                            attachment.get('size')
                        ))
                
                signals_stored += 1
        
        conn.commit()
        conn.close()
        
        return signals_stored
    
    def export_to_csv(self, filename: str = None) -> str:
        """
        Export signals to CSV file
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meta_signals_export_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        conn = sqlite3.connect(self.db_path)
        
        # Query all signals with attachments info
        query = '''
            SELECT 
                s.*,
                GROUP_CONCAT(a.filename) as attachment_filenames,
                GROUP_CONCAT(a.url) as attachment_urls
            FROM signals s
            LEFT JOIN attachments a ON s.id = a.signal_id
            GROUP BY s.id
            ORDER BY s.timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        df.to_csv(filepath, index=False)
        
        conn.close()
        
        return filepath
    
    def export_to_json(self, filename: str = None) -> str:
        """
        Export signals to JSON file
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meta_signals_export_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all signals
        cursor.execute('''
            SELECT * FROM signals ORDER BY timestamp DESC
        ''')
        
        signals = []
        for row in cursor.fetchall():
            signal_dict = dict(zip([col[0] for col in cursor.description], row))
            
            # Get attachments for this signal
            cursor.execute('''
                SELECT filename, url, content_type, size 
                FROM attachments WHERE signal_id = ?
            ''', (signal_dict['id'],))
            
            attachments = []
            for att_row in cursor.fetchall():
                attachments.append({
                    'filename': att_row[0],
                    'url': att_row[1],
                    'content_type': att_row[2],
                    'size': att_row[3]
                })
            
            signal_dict['attachments'] = attachments
            signals.append(signal_dict)
        
        conn.close()
        
        # Write to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, default=str)
        
        return filepath
    
    def get_signals_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of stored signals
        
        Returns:
            Dictionary with summary statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total signals
        cursor.execute('SELECT COUNT(*) FROM signals')
        total_signals = cursor.fetchone()[0]
        
        # Signals by symbol
        cursor.execute('''
            SELECT symbol, COUNT(*) as count 
            FROM signals 
            GROUP BY symbol 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_symbols = cursor.fetchall()
        
        # Signals by action
        cursor.execute('''
            SELECT action, COUNT(*) as count 
            FROM signals 
            GROUP BY action
        ''')
        action_counts = cursor.fetchall()
        
        # Signals by timeframe
        cursor.execute('''
            SELECT timeframe, COUNT(*) as count 
            FROM signals 
            WHERE timeframe IS NOT NULL
            GROUP BY timeframe
        ''')
        timeframe_counts = cursor.fetchall()
        
        # Date range
        cursor.execute('''
            SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest 
            FROM signals
        ''')
        date_range = cursor.fetchone()
        
        # Signals with attachments
        cursor.execute('SELECT COUNT(*) FROM signals WHERE has_attachments = 1')
        signals_with_attachments = cursor.fetchone()[0]
        
        conn.close()
        
        summary = {
            'total_signals': total_signals,
            'top_symbols': dict(top_symbols),
            'action_counts': dict(action_counts),
            'timeframe_counts': dict(timeframe_counts),
            'date_range': {
                'earliest': date_range[0],
                'latest': date_range[1]
            },
            'signals_with_attachments': signals_with_attachments,
            'attachment_percentage': (signals_with_attachments / total_signals * 100) if total_signals > 0 else 0
        }
        
        return summary
    
    def search_signals(self, symbol: str = None, action: str = None, 
                      timeframe: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search signals with filters
        
        Args:
            symbol: Filter by symbol
            action: Filter by action
            timeframe: Filter by timeframe
            limit: Maximum results to return
            
        Returns:
            List of matching signals
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM signals WHERE 1=1'
        params = []
        
        if symbol:
            query += ' AND symbol LIKE ?'
            params.append(f'%{symbol}%')
        
        if action:
            query += ' AND action = ?'
            params.append(action.upper())
        
        if timeframe:
            query += ' AND timeframe = ?'
            params.append(timeframe)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            signal_dict = dict(zip([col[0] for col in cursor.description], row))
            results.append(signal_dict)
        
        conn.close()
        
        return results