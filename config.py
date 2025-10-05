# Configuration file for VWAP Signal Bot

import os

# Telegram settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'default_token_if_needed')
CHAT_ID = os.getenv('CHAT_ID', 'default_chat_id')

# Trading settings
SYMBOLS = [
    # Top Tier (High Volume & Market Cap)
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 
    'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'TRXUSDT',
    'LINKUSDT', 'MATICUSDT', 'LTCUSDT', 'SHIBUSDT', 'BCHUSDT',

    # Mid Tier (Strong Altcoins)
    'NEARUSDT', 'ETCUSDT', 'UNIUSDT', 'FILUSDT', 'OPUSDT',
    'APTUSDT', 'ATOMUSDT', 'XMRUSDT', 'FTMUSDT', 'HBARUSDT',
    'AAVEUSDT', 'QNTUSDT', 'ARBUSDT', 'VETUSDT', 'GALAUSDT',
    
    # Other Popular & High-Volume Pairs
    'SUIUSDT', 'MANAUSDT', 'AXSUSDT', 'SANDUSDT', 'ALGOUSDT',
    'EOSUSDT', 'ZECUSDT', 'THETAUSDT', 'CHZUSDT', 'WAVESUSDT',
    'ICPUSDT', 'GRTUSDT', 'IMXUSDT', 'CRVUSDT', 'RUNEUSDT',
    'PEPEUSDT', 'FLOKIUSDT', 'INJUSDT', 'SEIUSDT', 'TIAUSDT'
]  # Add more USDT pairs here
INTERVAL = '1m'  # Bar interval
BAND_MULT_3 = 3.0  # 3rd band multiplier
CALC_MODE = 'Standard Deviation'  # 'Standard Deviation' or 'Percentage'
SESSION_DELAY_MIN = 25  # Minutes after 00:00 UTC to enable signals
COOLDOWN_MIN = 20  # Cooldown for same direction signals per symbol

# Binance settings (ccxt handles it)
EXCHANGE = 'binance'