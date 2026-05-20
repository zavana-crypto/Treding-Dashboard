import time
import requests
from binance.client import Client
import winsound

# --- KONFIGURASI ---
API_KEY = "..." 
API_SECRET = "..."
TELEGRAM_TOKEN = "7780808936:AAGcJIentExOQ95Z2NdN8T7ON_LEzLRG1WI"
TELEGRAM_CHAT_ID = "2009096437"

# --- FUNGSI TELEGRAM ---
def kirim_telegram(pesan):
    """Fungsi untuk mengirim pesan ke Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': pesan}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

# --- INISIALISASI ---
client = Client(API_KEY, API_SECRET)

# Isi daftar market Anda di sini
# Contoh format: {"id": "btcusdt", "fetchSymbol": "BTCUSDT", "title": "Bitcoin"}
markets = [
    {"id": "btcusdt", "fetchSymbol": "BTCUSDT", "title": "Bitcoin"},
    {"id": "ethusdt", "fetchSymbol": "ETHUSDT", "title": "Ethereum"}
]
last_prices = {}

# --- MAIN LOOP ---
print("Sistem Bot Siap Berjalan...")

while True:
    try:
        print("\n📊 Memantau Harga (Binance):")
        for market in markets:
            ticker = client.get_symbol_ticker(symbol=market["fetchSymbol"])
            price = float(ticker["price"])
            print(f"{market['title']}: {price:,.2f} USDT")

            if market["id"] in last_prices:
                last_price = last_prices[market["id"]]
                change = ((price - last_price) / last_price) * 100
                
                # Jika perubahan >= 1%, kirim notifikasi
                if abs(change) >= 1:
                    pesan_alert = f"⚡ ALERT: {market['title']} berubah {change:.2f}% (Harga: {price:,.2f} USDT)"
                    print(pesan_alert)
                    
                    winsound.Beep(1000, 500)
                    kirim_telegram(pesan_alert)
                    
            last_prices[market["id"]] = price
            
    except Exception as e:
        print(f"Terjadi kesalahan saat memantau harga: {e}")
    
    # Tunggu 5 detik sebelum cek lagi
    time.sleep(5)
