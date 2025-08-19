from flask import Flask, request, jsonify
import MetaTrader5 as mt5

app = Flask(__name__)

# --- Mapping dashboard → MT5 ---
MARKET_MT5_MAPPING = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "XAUUSD": "XAUUSD",
    "WTI": "USOIL"
}

# --- Connect ke MT5 ---
account = 12345678
password = "password_anda"
server = "Exness-Demo"

if not mt5.initialize(login=account, password=password, server=server):
    print("Gagal connect ke MT5")
    mt5.shutdown()
    exit()
print("Berhasil connect ke MT5")

# --- Fungsi cek harga ---
def cek_harga(symbol_dashboard):
    if symbol_dashboard not in MARKET_MT5_MAPPING:
        return None
    symbol_mt5 = MARKET_MT5_MAPPING[symbol_dashboard]
    if not mt5.symbol_select(symbol_mt5, True):
        return None
    tick = mt5.symbol_info_tick(symbol_mt5)
    return tick

# --- Fungsi buka posisi ---
def open_position(symbol_dashboard, action, lot, sl, tp):
    tick = cek_harga(symbol_dashboard)
    if not tick:
        return {"status": "error", "message": "Simbol tidak tersedia"}
    symbol_mt5 = MARKET_MT5_MAPPING[symbol_dashboard]
    price = tick.ask if action == "BUY" else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol_mt5,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "ZAVANA Auto Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    return {"status": "ok", "result": str(result)}

# --- Route menerima sinyal dari dashboard ---
@app.route("/sinyal", methods=["POST"])
def sinyal():
    data = request.get_json()
    symbol = data.get("symbol")
    action = data.get("action")
    lot = data.get("lot", 0.01)
    sl = data.get("sl", 0.0)
    tp = data.get("tp", 0.0)

    response = open_position(symbol, action, lot, sl, tp)
    return jsonify(response)

# --- Jalankan server Flask ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
