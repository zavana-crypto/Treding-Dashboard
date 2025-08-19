from flask import Flask, jsonify, request
from flask_cors import CORS
from binance.client import Client
import pandas as pd
import numpy as np
import os
import time

# ====== KONFIGURASI ======
API_KEY = os.getenv("BINANCE_API_KEY", "2pj9OyoSm2Lcy2BXKIxkMkRuMJuGBWuiEPPSsb0XzyxDxqODrj7AM1jEMvcNkY6o")
API_SECRET = os.getenv("BINANCE_API_SECRET", "e0V0bEObM5oTmvgZVlp7MRYHNwT76jJcG9r2YLRpON7dTq1fvvDEshUN8nQMQwSy")
USE_TESTNET = os.getenv("BINANCE_TESTNET", "false").lower() == "true"

# daftar market persis seperti di HTML
MARKETS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT",
    "DOGEUSDT","TRXUSDT","DOTUSDT","LTCUSDT","SHIBUSDT","AVAXUSDT",
    "PEPEUSDT","CAKEUSDT"
]

TIMEFRAMES = {
    "1m": Client.KLINE_INTERVAL_1MINUTE,
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR
}

# indikator default
EMA_FAST = int(os.getenv("EMA_FAST", 9))
EMA_SLOW = int(os.getenv("EMA_SLOW", 21))
RSI_LEN  = int(os.getenv("RSI_LEN", 14))
RSI_MAX  = float(os.getenv("RSI_MAX", 70))  # filter long
RSI_MIN  = float(os.getenv("RSI_MIN", 30))  # filter short
LIMIT    = int(os.getenv("KLINES_LIMIT", 200))  # jumlah candle per request

# ====== INISIASI KLIEN & APLIKASI ======
client = Client(API_KEY, API_SECRET, testnet=USE_TESTNET)
app = Flask(__name__)
CORS(app)  # biar bisa diakses dari index.html yang jalan di file:// atau localhost

# ====== UTIL ======
def get_klines(symbol: str, interval: str, limit: int = LIMIT) -> pd.DataFrame:
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbb","tbq","ignore"
    ])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["close"] = df["close"].astype(float)
    return df

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain, index=series.index).rolling(period).mean()
    avg_loss = pd.Series(loss, index=series.index).rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def make_signal(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["ema_fast"] = ema(df["close"], EMA_FAST)
    df["ema_slow"] = ema(df["close"], EMA_SLOW)
    df["rsi"] = rsi(df["close"], RSI_LEN)

    last = df.iloc[-1]
    cond_long  = last["ema_fast"] > last["ema_slow"] and last["rsi"] < RSI_MAX
    cond_short = last["ema_fast"] < last["ema_slow"] and last["rsi"] > RSI_MIN

    if cond_long:
        sig = "BUY"
    elif cond_short:
        sig = "SELL"
    else:
        sig = "HOLD"

    return {
        "signal": sig,
        "close": float(last["close"]),
        "ema_fast": float(last["ema_fast"]),
        "ema_slow": float(last["ema_slow"]),
        "rsi": float(last["rsi"]),
        "time": df.index[-1].isoformat() if isinstance(df.index, pd.DatetimeIndex) else str(df["time"].iloc[-1])
    }

# ====== CACHE SEDERHANA (kurangi hit API) ======
_cache = {}  # key: (symbol, tf_name) -> {ts, data}
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 10))

def get_signal_cached(symbol: str, tf_name: str):
    now = time.time()
    key = (symbol, tf_name)
    if key in _cache and (now - _cache[key]["ts"] <= CACHE_TTL):
        return _cache[key]["data"]
    df = get_klines(symbol, TIMEFRAMES[tf_name], LIMIT)
    sig = make_signal(df)
    _cache[key] = {"ts": now, "data": sig}
    return sig

# ====== ENDPOINTS ======
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "testnet": USE_TESTNET,
        "markets": len(MARKETS),
        "timeframes": list(TIMEFRAMES.keys()),
        "ema_fast": EMA_FAST, "ema_slow": EMA_SLOW, "rsi_len": RSI_LEN
    })

@app.route("/signal", methods=["GET"])
def signal_one():
    """
    Contoh:
      /signal?symbol=BTCUSDT&tf=1m
    """
    symbol = request.args.get("symbol", "BTCUSDT").upper()
    tf_name = request.args.get("tf", "1m")
    if symbol not in MARKETS:
        return jsonify({"error": f"symbol {symbol} tidak didukung"}), 400
    if tf_name not in TIMEFRAMES:
        return jsonify({"error": f"tf {tf_name} tidak didukung"}), 400
    try:
        data = get_signal_cached(symbol, tf_name)
        return jsonify({symbol: {tf_name: data}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/signals", methods=["GET"])
def signals_all():
    """
    Mengembalikan semua market x semua timeframe:
    {
      "BTCUSDT": {"1m": {...}, "15m": {...}, "1h": {...}},
      "ETHUSDT": {"1m": {...}, ...},
      ...
    }
    """
    results = {}
    try:
        for sym in MARKETS:
            results[sym] = {}
            for tf_name in TIMEFRAMES.keys():
                try:
                    results[sym][tf_name] = get_signal_cached(sym, tf_name)
                except Exception as e:
                    results[sym][tf_name] = {"error": str(e)}
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Jalankan di localhost:5000
    app.run(host="0.0.0.0", port=5000)
