from flask import Flask, jsonify, request
from flask_cors import CORS
from binance.client import Client
import pandas as pd
import numpy as np
import os
import time

# ====== KONFIGURASI ======
# API Key dikosongkan agar aman. Tidak butuh kunci untuk data publik.
API_KEY = ""
API_SECRET = ""
USE_TESTNET = os.getenv("BINANCE_TESTNET", "false").lower() == "true"

MARKETS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", 
           "DOGEUSDT", "TRXUSDT", "DOTUSDT", "LTCUSDT", "SHIBUSDT", "AVAXUSDT", 
           "PEPEUSDT", "CAKEUSDT"]

TIMEFRAMES = {
    "1m": Client.KLINE_INTERVAL_1MINUTE, 
    "15m": Client.KLINE_INTERVAL_15MINUTE, 
    "1h": Client.KLINE_INTERVAL_1HOUR
}

# Indikator default
EMA_FAST = 9
EMA_SLOW = 21
RSI_LEN = 14
RSI_MAX = 70
RSI_MIN = 30
LIMIT = 200

# ====== INISIASI KLIEN & APLIKASI ======
client = Client(API_KEY, API_SECRET, testnet=USE_TESTNET)
app = Flask(__name__)
CORS(app)

# ====== UTIL ======
def get_klines(symbol, interval, limit=LIMIT):
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=["time","open","high","low","close","volume", 
                                    "close_time","qav","trades","tbb","tbq","ignore"])
    df["close"] = df["close"].astype(float)
    return df

def ema(series, period): return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def make_signal(df):
    df["ema_fast"] = ema(df["close"], EMA_FAST)
    df["ema_slow"] = ema(df["close"], EMA_SLOW)
    df["rsi"] = rsi(df["close"], RSI_LEN)
    last = df.iloc[-1]
    
    if last["ema_fast"] > last["ema_slow"] and last["rsi"] < RSI_MAX: sig = "BUY"
    elif last["ema_fast"] < last["ema_slow"] and last["rsi"] > RSI_MIN: sig = "SELL"
    else: sig = "HOLD"
    
    return {
        "signal": sig, "close": float(last["close"]), 
        "ema_fast": float(last["ema_fast"]), "ema_slow": float(last["ema_slow"]), 
        "rsi": float(last["rsi"])
    }

_cache = {}
CACHE_TTL = 10

def get_signal_cached(symbol, tf_name):
    now = time.time()
    key = (symbol, tf_name)
    if key in _cache and (now - _cache[key]["ts"] <= CACHE_TTL):
        return _cache[key]["data"]
    df = get_klines(symbol, TIMEFRAMES[tf_name], LIMIT)
    sig = make_signal(df)
    _cache[key] = {"ts": now, "data": sig}
    return sig

# ====== ENDPOINTS ======
@app.route("/signal", methods=["GET"])
def signal_one():
    symbol = request.args.get("symbol", "BTCUSDT").upper()
    tf_name = request.args.get("tf", "1m")
    return jsonify({symbol: {tf_name: get_signal_cached(symbol, tf_name)}})

@app.route("/signals", methods=["GET"])
def signals_all():
    results = {sym: {tf: get_signal_cached(sym, tf) for tf in TIMEFRAMES} for sym in MARKETS}
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
