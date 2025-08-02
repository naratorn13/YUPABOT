from flask import Flask, request, jsonify
import requests
import time
import base64
import hmac
import hashlib
import json

app = Flask(__name__)

# === กำหนดค่าคีย์ของคุณที่ได้จาก OKX ===
API_KEY = "3f9195c4-0485-4ebf-abc8-161d85857005"
API_SECRET = "DC9F9093F03F8791D098C5CF80A54921"
API_PASSPHRASE = "13112535DODo."

# === สร้างลายเซ็น ===
def generate_signature(timestamp, method, request_path, body):
    body_str = json.dumps(body, separators=(',', ':')) if body else ''  # ต้องไม่มีเว้นวรรคเกิน
    message = f"{timestamp}{method.upper()}{request_path}{body_str}"
    hmac_key = base64.b64decode(API_SECRET)
    signature = hmac.new(hmac_key, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

# === ส่งคำสั่งซื้อไปที่ OKX ===
def send_order_to_okx(symbol, size):
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    url = "https://www.okx.com"
    endpoint = "/api/v5/trade/order"
    full_url = url + endpoint

    body = {
        "instId": symbol,
        "tdMode": "cross",
        "side": "buy",
        "posSide": "long",
        "ordType": "market",
        "sz": str(size)
    }

    signature = generate_signature(timestamp, "POST", endpoint, body)

    headers = {
        "Content-Type": "application/json",
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": API_PASSPHRASE
    }

    response = requests.post(full_url, headers=headers, json=body)
    return response.json()

# === Webhook Receiver ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get('action', 'buy')
    symbol = data.get('symbol')
    size = data.get('size')

    print(f"Action: {action}, Symbol: {symbol}, Size: {size}")

    if action == "buy":
        order_result = send_order_to_okx(symbol, size)
    else:
        order_result = {"error": "Action not supported"}

    return jsonify({"status": "success", "data": order_result}), 200

# === Run Server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
