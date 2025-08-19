# file: bot.py
from binance.client import Client
import pandas as pd
import numpy as np

# === API Key Binance (isi dengan punyamu) ===
API_KEY = "2pj9OyoSm2Lcy2BXKIxkMkRuMJuGBWuiEPPSsb0XzyxDxqODrj7AM1jEMvcNkY6o"
API_SECRET = "e0V0bEObM5oTmvgZVlp7MRYHNwT76jJcG9r2YLRpON7dTq1fvvDEshUN8nQMQwSy"
client = Client(API_KEY, API_SECRET, testnet=False)  # testnet=True kalau mau coba aman

# === Daftar Market (dari HTML kamu) ===
MARKETS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT",
    "DOGEUSDT","TRXUSDT","DOTUSDT","LTCUSDT","SHIBUSDT","AVAXUSDT",
    "PEPEUSDT","CAKEUSDT"
]

# === Timeframes ===
TIMEFRAMES = {
    "1m": Client.KLINE_INTERVAL_1MINUTE,
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR
}

# === Fungsi ambil candlestick ===
def get_klines(symbol, interval, limit=200):
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbb","tbq","ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

# === Indikator EMA & RSI ===
def EMA(series, period=14):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# === Sinyal trading ===
def make_signal(df):
    df["ema_fast"] = EMA(df["close"], 9)
    df["ema_slow"] = EMA(df["close"], 21)
    df["rsi"] = RSI(df["close"], 14)
    last = df.iloc[-1]

    if last["ema_fast"] > last["ema_slow"] and last["rsi"] < 70:
        return "BUY"
    elif last["ema_fast"] < last["ema_slow"] and last["rsi"] > 30:
        return "SELL"
    else:
        return "HOLD"

# === Loop semua market & timeframe ===
def check_all():
    signals = {}
    for sym in MARKETS:
        signals[sym] = {}
        for tf_name, tf in TIMEFRAMES.items():
            try:
                df = get_klines(sym, tf, 200)
                sig = make_signal(df)
                signals[sym][tf_name] = sig
            except Exception as e:
                signals[sym][tf_name] = f"ERR: {str(e)}"
    return signals

if __name__ == "__main__":
    results = check_all()
    for sym, tf_signals in results.items():
        print(f"\n=== {sym} ===")
        for tf, sig in tf_signals.items():
            print(f" {tf} : {sig}")
