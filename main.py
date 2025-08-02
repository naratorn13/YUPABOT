from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Webhook Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received:", data)

    # Example: Extract TradingView data
    action = data.get("action")
    symbol = data.get("symbol")
    size = data.get("size")

    print(f"Action: {action}, Symbol: {symbol}, Size: {size}")
    # TODO: Connect to OKX API here

    return jsonify({"status": "success", "data": data}), 200

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=5000)

