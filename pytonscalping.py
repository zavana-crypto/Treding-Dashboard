import MetaTrader5 as mt5
import pandas as pd
import time

ACCOUNT = 272055372
PASSWORD = "@Oskar2704"
SERVER = "Exness-MT5Trial14"

# login ke MT5
mt5.initialize()
mt5.login(ACCOUNT, PASSWORD, server=SERVER)

# === Fungsi trading ===
def open_order(symbol, lot, order_type):
    price = mt5.symbol_info_tick(symbol).ask if order_type == "BUY" else mt5.symbol_info_tick(symbol).bid
    order = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL

    # TP & SL untuk scalping
    tp = price + 100 if order_type == "BUY" else price - 100
    sl = price - 50 if order_type == "BUY" else price + 50

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "Scalping Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    return mt5.order_send(request)

def close_all(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).bid if pos.type == 0 else mt5.symbol_info_tick(symbol).ask
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 20,
                "magic": 123456,
                "comment": "Scalping Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            mt5.order_send(close_request)

# === Fungsi indikator MA ===
def get_ma(symbol, timeframe=mt5.TIMEFRAME_M1, n=20):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n+5)
    df = pd.DataFrame(rates)
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    return df

# === LOOP trading otomatis ===
SYMBOL = "BTCUSD"

while True:
    df = get_ma(SYMBOL)

    ma5_prev, ma20_prev = df['MA5'].iloc[-2], df['MA20'].iloc[-2]
    ma5_curr, ma20_curr = df['MA5'].iloc[-1], df['MA20'].iloc[-1]

    # Check posisi sekarang
    positions = mt5.positions_get(symbol=SYMBOL)
    have_position = len(positions) > 0

    # Entry BUY signal
    if ma5_prev < ma20_prev and ma5_curr > ma20_curr and not have_position:
        print("Signal BUY 🚀")
        open_order(SYMBOL, 0.1, "BUY")

    # Entry SELL signal
    elif ma5_prev > ma20_prev and ma5_curr < ma20_curr and not have_position:
        print("Signal SELL 🔻")
        open_order(SYMBOL, 0.1, "SELL")

    time.sleep(5)  # cek tiap 5 detik
