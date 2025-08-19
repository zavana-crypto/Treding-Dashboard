import time
from binance.client import Client
import winsound  # untuk bunyi beep (Windows)

# Masukkan API Key Binance Anda
API_KEY = "2pj9OyoSm2Lcy2BXKIxkMkRuMJuGBWuiEPPSsb0XzyxDxqODrj7AM1jEMvcNkY6o"
API_SECRET = "e0V0bEObM5oTmvgZVlp7MRYHNwT76jJcG9r2YLRpON7dTq1fvvDEshUN8nQMQwSy"

# Inisialisasi client Binance
client = Client(API_KEY, API_SECRET)

# Daftar market
markets = [
    {"id": "BTCUSDT", "title": "BTC/USDT", "fetchSymbol": "BTCUSDT"},
    {"id": "ETHUSDT", "title": "ETH/USDT", "fetchSymbol": "ETHUSDT"},
    {"id": "SOLUSDT", "title": "SOL/USDT", "fetchSymbol": "SOLUSDT"},
    {"id": "XRPUSDT", "title": "XRP/USDT", "fetchSymbol": "XRPUSDT"},
    {"id": "BNBUSDT", "title": "BNB/USDT", "fetchSymbol": "BNBUSDT"},
]

# Simpan harga terakhir untuk deteksi perubahan
last_prices = {}

# Loop untuk update harga
while True:
    print("\n📊 Harga Crypto (Binance):")
    for market in markets:
        ticker = client.get_symbol_ticker(symbol=market["fetchSymbol"])
        price = float(ticker["price"])
        print(f"{market['title']}: {price:,.2f} USDT")

        # Cek perubahan harga
        if market["id"] in last_prices:
            last_price = last_prices[market["id"]]
            change = ((price - last_price) / last_price) * 100

            if abs(change) >= 1:  # kalau naik/turun >= 1%
                print(f"⚡ ALERT: {market['title']} berubah {change:.2f}%")
                winsound.Beep(1000, 500)  # bunyi beep 0.5 detik

        last_prices[market["id"]] = price

    time.sleep(5)  # update setiap 5 detik
