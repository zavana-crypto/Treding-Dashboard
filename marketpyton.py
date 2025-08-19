import MetaTrader5 as mt5

# --- 1️⃣ Mapping Dashboard ke MT5 ---
MARKET_MT5_MAPPING = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "XAUUSD": "XAUUSD",
    "WTI": "USOIL",
    "BTCUSDT": "BTCUSD",  # Crypto di MT5
    "ETHUSDT": "ETHUSD"
}

MARKETS = [
  { id:"BTCUSDT", title:"BTC/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"BTCUSDT", tvSymbol:"BINANCE:BTCUSDT" },
  { id:"ETHUSDT", title:"ETH/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"ETHUSDT", tvSymbol:"BINANCE:ETHUSDT" },
  { id:"BNBUSDT", title:"BNB/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"BNBUSDT", tvSymbol:"BINANCE:BNBUSDT" },
  { id:"SOLUSDT", title:"SOL/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"SOLUSDT", tvSymbol:"BINANCE:SOLUSDT" },
  { id:"XRPUSDT", title:"XRP/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"XRPUSDT", tvSymbol:"BINANCE:XRPUSDT" },
  { id:"ADAUSDT", title:"ADA/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"ADAUSDT", tvSymbol:"BINANCE:ADAUSDT" },
  { id:"DOGEUSDT", title:"DOGE/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"DOGEUSDT", tvSymbol:"BINANCE:DOGEUSDT" },
  { id:"TRXUSDT", title:"TRX/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"TRXUSDT", tvSymbol:"BINANCE:TRXUSDT" },
  { id:"DOTUSDT", title:"DOT/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"DOTUSDT", tvSymbol:"BINANCE:DOTUSDT" },
  { id:"LTCUSDT", title:"LTC/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"LTCUSDT", tvSymbol:"BINANCE:LTCUSDT" },
  { id:"SHIBUSDT", title:"SHIB/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"SHIBUSDT", tvSymbol:"BINANCE:SHIBUSDT" },
  { id:"AVAXUSDT", title:"AVAX/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"AVAXUSDT", tvSymbol:"BINANCE:AVAXUSDT" },
  { id:"PEPEUSDT", title:"PEPE/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"PEPEUSDT", tvSymbol:"BINANCE:PEPEUSDT" },
  { id:"CAKEUSDT", title:"CAKE/USDT", group:"CRYPTO", provider:"binance", fetchSymbol:"CAKEUSDT", tvSymbol:"BINANCE:CAKEUSDT" }
]

# --- 2️⃣ Connect ke MT5 ---
account = 272055372
password = "@Oskar2704"
server = "Exness-MT5Trial14"

if not mt5.initialize(login=account, password=password, server=server):
    print("Gagal connect ke MT5")
    mt5.shutdown()
    exit()
print("Berhasil connect ke MT5")

# --- 3️⃣ Fungsi cek simbol & harga ---
def cek_harga(symbol_dashboard):
    if symbol_dashboard not in MARKET_MT5_MAPPING:
        print(f"Simbol {symbol_dashboard} tidak tersedia di MT5")
        return None
    symbol_mt5 = MARKET_MT5_MAPPING[symbol_dashboard]
    if not mt5.symbol_select(symbol_mt5, True):
        print(f"Gagal menambahkan simbol {symbol_mt5} ke Market Watch")
        return None
    tick = mt5.symbol_info_tick(symbol_mt5)
    return tick

# --- 4️⃣ Fungsi buka posisi ---
def open_position(symbol_dashboard, action, lot, sl, tp):
    tick = cek_harga(symbol_dashboard)
    if not tick:
        return
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
    print(f"Order result: {result}")

# --- 5️⃣ Contoh eksekusi ---
open_position("EURUSD", "BUY", 0.01, 1.1000, 1.1200)
open_position("XAUUSD", "SELL", 0.01, 1950, 1900)

# Tutup koneksi MT5
mt5.shutdown()
