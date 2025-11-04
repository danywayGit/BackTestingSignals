"""
Shared Backtest Analysis Functions

Provides common analysis utilities to avoid code duplication across analysis scripts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class BacktestAnalyzer:
    """
    Unified backtest analysis class with common analysis methods.
    Eliminates duplicate code across optimization and comparison scripts.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with backtest results dataframe.
        
        Args:
            df: DataFrame with backtest results containing at least:
                - signal_time, action, final_outcome, entry_price, target1
        """
        self.df = df.copy()
        self._prepare_dataframe()
    
    def _prepare_dataframe(self):
        """Prepare dataframe with common calculated columns"""
        # Parse timestamps
        if 'signal_time' in self.df.columns:
            self.df['signal_time'] = pd.to_datetime(
                self.df['signal_time'], 
                format='mixed', 
                utc=True
            )
            
            # Extract time components
            self.df['hour'] = self.df['signal_time'].dt.hour
            self.df['day_of_week'] = self.df['signal_time'].dt.dayofweek
            self.df['day_name'] = self.df['signal_time'].dt.day_name()
            self.df['month'] = self.df['signal_time'].dt.month
            self.df['month_name'] = self.df['signal_time'].dt.month_name()
            self.df['date'] = self.df['signal_time'].dt.date
        
        # Calculate win/loss
        if 'final_outcome' in self.df.columns:
            self.df['is_winner'] = self.df['final_outcome'].apply(
                lambda x: x.startswith('TARGET') if pd.notna(x) else False
            )
            self.df['is_loser'] = self.df['final_outcome'] == 'STOP_LOSS'
    
    def filter_by_action(self, action: str) -> pd.DataFrame:
        """
        Filter dataframe by position type (LONG or SHORT).
        
        Args:
            action: 'LONG' or 'SHORT'
            
        Returns:
            Filtered DataFrame
        """
        return self.df[self.df['action'] == action].copy()
    
    def calculate_win_rate(self, df: Optional[pd.DataFrame] = None) -> float:
        """
        Calculate win rate percentage.
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            
        Returns:
            Win rate as percentage (0-100)
        """
        if df is None:
            df = self.df
        
        if len(df) == 0:
            return 0.0
        
        wins = df['is_winner'].sum()
        return (wins / len(df)) * 100
    
    def get_overall_stats(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Get overall performance statistics.
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            
        Returns:
            Dict with wins, losses, total, win_rate, avg_profit, avg_loss
        """
        if df is None:
            df = self.df
        
        wins = df['is_winner'].sum()
        losses = df['is_loser'].sum()
        total = len(df)
        wr = (wins / total * 100) if total > 0 else 0
        
        # Calculate average profit and loss
        winners = df[df['is_winner']]
        losers = df[df['is_loser']]
        
        avg_profit = winners['max_profit_pct'].mean() if len(winners) > 0 else 0
        avg_loss = abs(losers['max_drawdown_pct'].mean()) if len(losers) > 0 else 0
        
        # Calculate profit factor
        total_profit = winners['max_profit_pct'].sum() if len(winners) > 0 else 0
        total_loss = abs(losers['max_drawdown_pct'].sum()) if len(losers) > 0 else 0
        pf = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return {
            'total': int(total),
            'wins': int(wins),
            'losses': int(losses),
            'win_rate': float(wr),
            'avg_profit': float(avg_profit),
            'avg_loss': float(avg_loss),
            'profit_factor': float(pf)
        }
    
    def analyze_by_day_of_week(self, df: Optional[pd.DataFrame] = None) -> List[Dict]:
        """
        Analyze performance by day of week.
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            
        Returns:
            List of dicts with day stats
        """
        if df is None:
            df = self.df
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats = []
        
        for day in day_order:
            day_data = df[df['day_name'] == day]
            if len(day_data) > 0:
                stats = self.get_overall_stats(day_data)
                stats['day'] = day
                day_stats.append(stats)
        
        return day_stats
    
    def analyze_by_hour(self, df: Optional[pd.DataFrame] = None, min_signals: int = 5) -> List[Dict]:
        """
        Analyze performance by hour of day (UTC).
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            min_signals: Minimum signals required for inclusion
            
        Returns:
            List of dicts with hour stats
        """
        if df is None:
            df = self.df
        
        hour_stats = []
        
        for hour in range(24):
            hour_data = df[df['hour'] == hour]
            if len(hour_data) >= min_signals:
                stats = self.get_overall_stats(hour_data)
                stats['hour'] = hour
                hour_stats.append(stats)
        
        return hour_stats
    
    def analyze_by_coin(self, df: Optional[pd.DataFrame] = None, min_signals: int = 3) -> List[Dict]:
        """
        Analyze performance by coin/symbol.
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            min_signals: Minimum signals required for inclusion
            
        Returns:
            List of dicts with coin stats sorted by win rate
        """
        if df is None:
            df = self.df
        
        coin_stats = []
        
        for symbol in df['symbol'].unique():
            coin_data = df[df['symbol'] == symbol]
            if len(coin_data) >= min_signals:
                stats = self.get_overall_stats(coin_data)
                stats['symbol'] = symbol
                coin_stats.append(stats)
        
        # Sort by win rate descending
        coin_stats.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return coin_stats
    
    def analyze_by_month(self, df: Optional[pd.DataFrame] = None) -> List[Dict]:
        """
        Analyze performance by month.
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            
        Returns:
            List of dicts with month stats
        """
        if df is None:
            df = self.df
        
        month_stats = []
        
        for month_name in df['month_name'].unique():
            month_data = df[df['month_name'] == month_name]
            if len(month_data) > 0:
                stats = self.get_overall_stats(month_data)
                stats['month'] = month_name
                month_stats.append(stats)
        
        return month_stats
    
    def find_perfect_combinations(
        self, 
        df: Optional[pd.DataFrame] = None,
        min_signals: int = 3
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Find 100% win rate combinations.
        
        Args:
            df: DataFrame to analyze (uses self.df if None)
            min_signals: Minimum signals for combination
            
        Returns:
            Tuple of (day_hour_combos, day_coin_combos)
        """
        if df is None:
            df = self.df
        
        # Day + Hour combinations
        day_hour_combos = []
        for day in df['day_name'].unique():
            for hour in df['hour'].unique():
                combo_data = df[(df['day_name'] == day) & (df['hour'] == hour)]
                if len(combo_data) >= min_signals:
                    wins = combo_data['is_winner'].sum()
                    if wins == len(combo_data):  # 100% WR
                        avg_profit = combo_data['max_profit_pct'].mean()
                        day_hour_combos.append({
                            'day': day,
                            'hour': hour,
                            'signals': len(combo_data),
                            'wins': int(wins),
                            'avg_profit': float(avg_profit)
                        })
        
        # Day + Coin combinations
        day_coin_combos = []
        for day in df['day_name'].unique():
            for symbol in df['symbol'].unique():
                combo_data = df[(df['day_name'] == day) & (df['symbol'] == symbol)]
                if len(combo_data) >= min_signals:
                    wins = combo_data['is_winner'].sum()
                    if wins == len(combo_data):  # 100% WR
                        avg_profit = combo_data['max_profit_pct'].mean()
                        day_coin_combos.append({
                            'day': day,
                            'symbol': symbol,
                            'signals': len(combo_data),
                            'wins': int(wins),
                            'avg_profit': float(avg_profit)
                        })
        
        return day_hour_combos, day_coin_combos
    
    def get_best_performers(
        self,
        by: str,
        df: Optional[pd.DataFrame] = None,
        top_n: int = 5,
        min_signals: int = 5
    ) -> List[Dict]:
        """
        Get top N best performers by specified dimension.
        
        Args:
            by: 'day', 'hour', 'coin', or 'month'
            df: DataFrame to analyze (uses self.df if None)
            top_n: Number of top performers to return
            min_signals: Minimum signals required
            
        Returns:
            List of top performers sorted by win rate
        """
        if by == 'day':
            stats = self.analyze_by_day_of_week(df)
        elif by == 'hour':
            stats = self.analyze_by_hour(df, min_signals)
        elif by == 'coin':
            stats = self.analyze_by_coin(df, min_signals)
        elif by == 'month':
            stats = self.analyze_by_month(df)
        else:
            raise ValueError(f"Invalid 'by' parameter: {by}")
        
        # Filter by minimum signals if needed
        if by != 'hour' and by != 'coin':  # Already filtered in those methods
            stats = [s for s in stats if s['total'] >= min_signals]
        
        # Sort by win rate and return top N
        stats.sort(key=lambda x: x['win_rate'], reverse=True)
        return stats[:top_n]
    
    def get_worst_performers(
        self,
        by: str,
        df: Optional[pd.DataFrame] = None,
        bottom_n: int = 5,
        min_signals: int = 5
    ) -> List[Dict]:
        """
        Get bottom N worst performers by specified dimension.
        
        Args:
            by: 'day', 'hour', 'coin', or 'month'
            df: DataFrame to analyze (uses self.df if None)
            bottom_n: Number of worst performers to return
            min_signals: Minimum signals required
            
        Returns:
            List of worst performers sorted by win rate (ascending)
        """
        if by == 'day':
            stats = self.analyze_by_day_of_week(df)
        elif by == 'hour':
            stats = self.analyze_by_hour(df, min_signals)
        elif by == 'coin':
            stats = self.analyze_by_coin(df, min_signals)
        elif by == 'month':
            stats = self.analyze_by_month(df)
        else:
            raise ValueError(f"Invalid 'by' parameter: {by}")
        
        # Filter by minimum signals if needed
        if by != 'hour' and by != 'coin':
            stats = [s for s in stats if s['total'] >= min_signals]
        
        # Sort by win rate ascending and return bottom N
        stats.sort(key=lambda x: x['win_rate'])
        return stats[:bottom_n]
    
    def apply_filters(
        self,
        df: Optional[pd.DataFrame] = None,
        days: Optional[List[str]] = None,
        hours: Optional[List[int]] = None,
        coins: Optional[List[str]] = None,
        months: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Apply multiple filters to dataframe.
        
        Args:
            df: DataFrame to filter (uses self.df if None)
            days: List of day names to include
            hours: List of hours to include
            coins: List of coin symbols to include
            months: List of month names to include
            
        Returns:
            Filtered DataFrame
        """
        if df is None:
            df = self.df.copy()
        else:
            df = df.copy()
        
        if days:
            df = df[df['day_name'].isin(days)]
        if hours:
            df = df[df['hour'].isin(hours)]
        if coins:
            df = df[df['symbol'].isin(coins)]
        if months:
            df = df[df['month_name'].isin(months)]
        
        return df
    
    def create_optimization_strategy(
        self,
        df: Optional[pd.DataFrame] = None,
        target_wr: float = 60.0,
        min_signals: int = 5
    ) -> Dict:
        """
        Create optimized strategy by progressively filtering.
        
        Args:
            df: DataFrame to optimize (uses self.df if None)
            target_wr: Target win rate threshold
            min_signals: Minimum signals per filter
            
        Returns:
            Dict with strategy details and performance tiers
        """
        if df is None:
            df = self.df
        
        # Get best performers above target WR
        best_days = [
            d['day'] for d in self.analyze_by_day_of_week(df)
            if d['win_rate'] > target_wr - 2 and d['total'] >= min_signals
        ]
        best_hours = [
            h['hour'] for h in self.analyze_by_hour(df, min_signals)
            if h['win_rate'] > target_wr
        ]
        best_coins = [
            c['symbol'] for c in self.analyze_by_coin(df, min_signals)
            if c['win_rate'] > target_wr + 5
        ]
        
        # Create filter tiers
        tier1 = self.apply_filters(df, days=best_days)
        tier2 = self.apply_filters(df, days=best_days, hours=best_hours)
        tier3 = self.apply_filters(df, coins=best_coins)
        tier4 = self.apply_filters(df, days=best_days, coins=best_coins)
        tier5 = self.apply_filters(df, days=best_days, hours=best_hours, coins=best_coins)
        
        return {
            'baseline': self.get_overall_stats(df),
            'tier1_best_days': {
                'filters': {'days': best_days},
                'stats': self.get_overall_stats(tier1)
            },
            'tier2_days_hours': {
                'filters': {'days': best_days, 'hours': best_hours},
                'stats': self.get_overall_stats(tier2)
            },
            'tier3_best_coins': {
                'filters': {'coins': best_coins},
                'stats': self.get_overall_stats(tier3)
            },
            'tier4_days_coins': {
                'filters': {'days': best_days, 'coins': best_coins},
                'stats': self.get_overall_stats(tier4)
            },
            'tier5_ultra_filtered': {
                'filters': {'days': best_days, 'hours': best_hours, 'coins': best_coins},
                'stats': self.get_overall_stats(tier5)
            }
        }


def load_latest_backtest(directory: str = "data/backtest_results") -> pd.DataFrame:
    """
    Load the most recent backtest results file.
    
    Args:
        directory: Path to backtest results directory
        
    Returns:
        DataFrame with backtest results
    """
    results_dir = Path(directory)
    detailed_files = sorted(results_dir.glob('meta_signals_backtest_detailed_*.csv'))
    
    if not detailed_files:
        raise FileNotFoundError(f"No backtest results found in {directory}")
    
    latest_file = detailed_files[-1]
    print(f"📂 Loading: {latest_file.name}")
    
    return pd.read_csv(latest_file)
