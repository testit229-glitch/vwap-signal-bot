import ccxt
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone
import time

class SignalsCounter:
    def __init__(self):
        self.count = 0
        self.last_reset_date = None

    def get_count(self):
        current_date = datetime.now(timezone.utc).date()
        if self.last_reset_date != current_date:
            self.count = 0
            self.last_reset_date = current_date
        return self.count

    def increment(self):
        self.count += 1
        return self.count

class VWAPBot:
    def __init__(self, symbol, telegram_token, chat_id, calc_mode, band_mult_3, session_delay_min, cooldown_min, counter):
        self.symbol = symbol
        self.INTERVAL = '1m'  # Fixed for now
        self.exchange = ccxt.binance()  # Public access, no API key needed for spot data
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.calc_mode = calc_mode
        self.band_mult_3 = band_mult_3
        self.session_delay_min = session_delay_min
        self.cooldown_min = cooldown_min
        self.counter = counter  # Shared counter for total signals today
        self.last_buy_time = None
        self.last_sell_time = None

    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        params = {'chat_id': self.chat_id, 'text': message}
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Failed to send message for {self.symbol}: {response.text}")
        except Exception as e:
            print(f"Error sending message for {self.symbol}: {e}")

    def fetch_data(self, limit=1440):  # 1 day of 1m bars
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.INTERVAL, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            return None

    def calculate_vwap_and_bands(self, df):
        if len(df) < 20:
            return None, None, None, None
        
        # Source: hlc3
        df['tp'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['pv'] = df['tp'] * df['Volume']
        df['cum_pv'] = df['pv'].cumsum()
        df['cum_vol'] = df['Volume'].cumsum()
        df['vwap'] = df['cum_pv'] / df['cum_vol']
        
        # Volume-weighted standard deviation
        df['dev'] = df['tp'] - df['vwap']
        df['var_contrib'] = df['Volume'] * (df['dev'] ** 2)
        df['cum_var'] = df['var_contrib'].cumsum()
        df['vwap_variance'] = df['cum_var'] / df['cum_vol']
        df['stdev'] = np.sqrt(df['vwap_variance'])
        
        # Latest values
        latest = df.iloc[-1]
        vwap_val = latest['vwap']
        stdev_val = latest['stdev']
        low_val = latest['Low']
        high_val = latest['High']
        current_time = df.index[-1].to_pydatetime()
        
        # Band basis
        if self.calc_mode == 'Standard Deviation':
            band_basis = stdev_val
        else:  # Percentage
            band_basis = vwap_val * 0.01
        
        upper_band_3 = vwap_val + band_basis * self.band_mult_3
        lower_band_3 = vwap_val - band_basis * self.band_mult_3
        
        return vwap_val, upper_band_3, lower_band_3, low_val, high_val, current_time

    def check_signal(self):
        df = self.fetch_data()
        if df is None:
            return
        
        vwap_val, upper_band_3, lower_band_3, low_val, high_val, current_time = self.calculate_vwap_and_bands(df)
        if any(v is None for v in [vwap_val, upper_band_3, lower_band_3, low_val, high_val]):
            return
        
        # Session start (00:00 UTC)
        session_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        time_since_session_start = (current_time - session_start).total_seconds() / 60
        
        suppress_signals = time_since_session_start < self.session_delay_min
        
        # Conditions
        buy_condition = low_val <= lower_band_3
        sell_condition = high_val >= upper_band_3
        
        # Cooldown checks
        cooldown_passed_buy = self.last_buy_time is None or (current_time - self.last_buy_time).total_seconds() >= (self.cooldown_min * 60)
        cooldown_passed_sell = self.last_sell_time is None or (current_time - self.last_sell_time).total_seconds() >= (self.cooldown_min * 60)
        
        # Generate signals
        if buy_condition and not suppress_signals and cooldown_passed_buy:
            total_signals = self.counter.increment()
            entry_price = lower_band_3
            message = f"🟢 BUY\nPair: #{self.symbol}\nEntry Price: {entry_price:.4f}\nStoploss : 2.5%\nTotal Signals Today: {total_signals}"
            self.send_telegram_message(message)
            self.last_buy_time = current_time
            print(f"BUY signal for {self.symbol} at {current_time}")
        
        if sell_condition and not suppress_signals and cooldown_passed_sell:
            total_signals = self.counter.increment()
            entry_price = upper_band_3
            message = f"🔴 SELL\nPair: #{self.symbol}\nEntry Price: {entry_price:.4f}\nStoploss : 2.5%\nTotal Signals Today: {total_signals}"
            self.send_telegram_message(message)
            self.last_sell_time = current_time
            print(f"SELL signal for {self.symbol} at {current_time}")