"""
Test the updated Meta Signals parser
"""

import sys
import os
sys.path.append('src')

from parsers.discord_parser import DiscordMetaSignalsParser

def test_meta_signals_parser():
    """Test the parser with actual Meta Signals format"""
    
    parser = DiscordMetaSignalsParser()
    
    # Test with actual Meta Signals format
    test_message = """📈 ETH | USDT @ $3,825.25 - 2H - 1.1.1

Target 1: 3,933.10 (RR 1.09)
Target 2: 4,044.62 (RR 2.22)
Target 3: 4,268.33 (RR 4.48)
SL Close Below: 3,726.42

<@&1180197358152204360>

**[PLACE TRADE](<https://..."""
    
    print("🧪 Testing Meta Signals Parser")
    print("=" * 40)
    print(f"Message:\n{test_message}")
    print("=" * 40)
    
    signals = parser.parse_message(test_message)
    
    print(f"Found {len(signals)} signals")
    
    if signals:
        signal = signals[0]
        print(f"\n✅ Signal Details:")
        print(f"Symbol: {signal.symbol}")
        print(f"Action: {signal.action}")
        print(f"Entry Price: {signal.entry_price}")
        print(f"Stop Loss: {signal.stop_loss}")
        print(f"Take Profit (Target 1): {signal.take_profit}")
        
        if signal.additional_info:
            print(f"Target 1: {signal.additional_info.get('target1')}")
            print(f"Target 2: {signal.additional_info.get('target2')}")
            print(f"Target 3: {signal.additional_info.get('target3')}")
            print(f"Timeframe: {signal.additional_info.get('timeframe')}")
            print(f"Strategy Version: {signal.additional_info.get('strategy_version')}")
            print(f"Format Type: {signal.additional_info.get('format_type')}")
    else:
        print("❌ No signals found - parser needs adjustment")

if __name__ == "__main__":
    test_meta_signals_parser()