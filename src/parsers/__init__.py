"""Signal parsers package"""

from .base_parser import SignalParser, Signal
from .telegram_parser import TelegramSignalParser
from .discord_parser import DiscordMetaSignalsParser

__all__ = ['SignalParser', 'Signal', 'TelegramSignalParser', 'DiscordMetaSignalsParser']