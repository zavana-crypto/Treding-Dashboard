from flask import Flask, jsonify
import requests

app = Flask(__name__)

markets = [
    {"id": "BTCUSDT", "title": "BTC/USDT"},
    {"id": "ETHUSDT", "title": "ETH/USDT"},
    {"id": "SOLUSDT", "title": "SOL/USDT"},
    {"id": "XRPUSDT", "title": "XRP/USDT"},
    {"id": "BNBUSDT", "title": "BNB/USDT"},
]

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    data = requests.get(url).json()
    return float(data["price"])

@app.route("/prices")
def prices():
    result = {}
    for market in markets:
        result[market["id"]] = get_price(market["id"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
