import time
import requests  # Tambahkan ini
from binance.client import Client
import winsound

# --- KONFIGURASI ---
API_KEY = "..." 
API_SECRET = "..."
TELEGRAM_TOKEN = "7780808936:AAGcJIentExOQ95Z2NdN8T7ON_LEzLRG1WI"
TELEGRAM_CHAT_ID = "2009096437"

def kirim_telegram(pesan):
    """Fungsi untuk mengirim pesan ke Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': pesan}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

# Inisialisasi client Binance
client = Client(API_KEY, API_SECRET)

markets = [...] # (Daftar market Anda tetap sama)
last_prices = {}

while True:
    print("\n📊 Harga Crypto (Binance):")
    for market in markets:
        ticker = client.get_symbol_ticker(symbol=market["fetchSymbol"])
        price = float(ticker["price"])
        print(f"{market['title']}: {price:,.2f} USDT")

        if market["id"] in last_prices:
            last_price = last_prices[market["id"]]
            change = ((price - last_price) / last_price) * 100
            
            if abs(change) >= 1:
                pesan_alert = f"⚡ ALERT: {market['title']} berubah {change:.2f}% (Harga: {price:,.2f})"
                print(pesan_alert)
                
                # Tambahkan aksi:
                winsound.Beep(1000, 500)
                kirim_telegram(pesan_alert) # Panggil fungsi kirim
                
        last_prices[market["id"]] = price
    
    time.sleep(5)
