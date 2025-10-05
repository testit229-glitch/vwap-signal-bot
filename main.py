import time
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID, SYMBOLS, INTERVAL, BAND_MULT_3, CALC_MODE, SESSION_DELAY_MIN, COOLDOWN_MIN, EXCHANGE
from bot import VWAPBot, SignalsCounter

# Shared counter for total signals today
signal_counter = SignalsCounter()

# Create bot instances for each symbol (cooldown per bot/symbol)
bots = {symbol: VWAPBot(symbol, TELEGRAM_TOKEN, CHAT_ID, CALC_MODE, BAND_MULT_3, SESSION_DELAY_MIN, COOLDOWN_MIN, signal_counter) for symbol in SYMBOLS}

print(f"Starting VWAP Signal Bot for symbols: {SYMBOLS}")
print("Press Ctrl+C to stop.")

try:
    while True:
        for symbol, bot in bots.items():
            bot.check_signal()
        
        # Wait 1 minute for next check (all symbols)
        time.sleep(60)
        
except KeyboardInterrupt:
    print("Bot stopped by user.")