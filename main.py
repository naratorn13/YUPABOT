from flask import Flask, request, jsonify
import os, time, hmac, hashlib, base64, requests

app = Flask(__name__)

# === OKX API Credentials ===
API_KEY = "3f9195c4-0485-4ebf-abc8-161d85857005"
SECRET_KEY = "DC9F9093F03F8791D098C5CF80A54921"
PASSPHRASE = "13112535DODo."

# === Generate OKX Signature ===
def generate_signature(timestamp, method, request_path, body):
    if body:
        body = str(body).replace("'", '"')
    else:
        body = ''
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(bytes(SECRET_KEY, encoding='utf8'), bytes(message, encoding='utf8'), digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d).decode()

# === Send Order to OKX ===
def send_order_to_okx(symbol, size):
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    url = "https://www.okx.com"  # ← แก้แล้ว ถูกต้อง
    endpoint = "/api/v5/trade/order"
    full_url = url + endpoint

    body = {
        "instId": symbol,
        "tdMode": "cash",
        "side": "buy",
        "ordType": "market",
        "sz": str(size)
    }

    signature = generate_signature(timestamp, "POST", endpoint, body)

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    response = requests.post(full_url, json=body, headers=headers)
    print("OKX API Response:", response.json())
    return response.json()

# === Routes ===
@app.route('/')
def home():
    return 'Webhook Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received:", data)

    action = data.get("action")
    symbol = data.get("symbol")
    size = data.get("size")

    print(f"Action: {action}, Symbol: {symbol}, Size: {size}")

    if action == "buy":
        order_result = send_order_to_okx(symbol, size)
    else:
        order_result = {"error": "Action not supported"}

    return jsonify({"status": "success", "data": order_result}), 200

# === Run Server ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
