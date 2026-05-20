import pandas as pd
import numpy as np
import requests
from binance.client import Client

# --- KONFIGURASI TELEGRAM ---
# Ganti dengan token dan chat_id Anda
TELEGRAM_TOKEN = "7780808936:AAGcJIentExOQ95Z2NdN8T7ON_LEzLRG1WI"
TELEGRAM_CHAT_ID = "2009096437"

# --- INISIALISASI ---
# API Key dikosongkan agar aman. Jika butuh eksekusi trade, 
# gunakan variable environment (.env)
client = Client("", "") 

MARKETS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", 
           "DOGEUSDT", "TRXUSDT", "DOTUSDT", "LTCUSDT", "SHIBUSDT", "AVAXUSDT", 
           "PEPEUSDT", "CAKEUSDT"]

TIMEFRAMES = {"1m": Client.KLINE_INTERVAL_1MINUTE, 
              "15m": Client.KLINE_INTERVAL_15MINUTE, 
              "1h": Client.KLINE_INTERVAL_1HOUR}

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': pesan}
    try:
        requests.get(url, params=params)
    except:
        pass

def get_klines(symbol, interval, limit=200):
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=["time","open","high","low","close","volume", 
                                    "close_time","qav","trades","tbb","tbq","ignore"])
    df["close"] = df["close"].astype(float)
    return df

def EMA(series, period): return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def make_signal(df):
    df["ema_fast"] = EMA(df["close"], 9)
    df["ema_slow"] = EMA(df["close"], 21)
    df["rsi"] = RSI(df["close"], 14)
    last = df.iloc[-1]
    if last["ema_fast"] > last["ema_slow"] and last["rsi"] < 70: return "BUY"
    elif last["ema_fast"] < last["ema_slow"] and last["rsi"] > 30: return "SELL"
    return "HOLD"

if __name__ == "__main__":
    print("Menganalisis sinyal...")
    for sym in MARKETS:
        for tf_name, tf in TIMEFRAMES.items():
            try:
                df = get_klines(sym, tf, 200)
                sig = make_signal(df)
                if sig != "HOLD":
                    pesan = f"🚀 Sinyal {sig} pada {sym} ({tf_name})"
                    print(pesan)
                    kirim_telegram(pesan)
            except Exception as e:
                print(f"Error {sym}: {e}")
