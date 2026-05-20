import time
import requests
import winsound

# --- KONFIGURASI ---
TELEGRAM_TOKEN = "7780808936:AAGcJIentExOQ95Z2NdN8T7ON_LEzLRG1WI"
TELEGRAM_CHAT_ID = "2009096437"

# --- FUNGSI ---
def kirim_telegram(pesan):
    """Mengirim pesan ke Telegram via API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': pesan}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

def get_price(symbol):
    """Mengambil harga publik dari Binance tanpa API Key"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url).json()
    return float(response['price'])

# --- DATA MARKET ---
markets = [
    {"id": "btcusdt", "fetchSymbol": "BTCUSDT", "title": "Bitcoin"},
    {"id": "ethusdt", "fetchSymbol": "ETHUSDT", "title": "Ethereum"}
]
last_prices = {}

# --- MAIN LOOP ---
print("Sistem Bot Siap Berjalan (Mode Monitor)...")

while True:
    try:
        for market in markets:
            price = get_price(market["fetchSymbol"])
            print(f"📊 {market['title']}: {price:,.2f} USDT")

            if market["id"] in last_prices:
                last_price = last_prices[market["id"]]
                change = ((price - last_price) / last_price) * 100
                
                # Cek perubahan >= 1%
                if abs(change) >= 1:
                    pesan_alert = f"⚡ ALERT: {market['title']} berubah {change:.2f}% (Harga: {price:,.2f} USDT)"
                    print(pesan_alert)
                    winsound.Beep(1000, 500)
                    kirim_telegram(pesan_alert)
                    
            last_prices[market["id"]] = price
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(5)
