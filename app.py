from flask import Flask, jsonify, request
import numpy as np

app = Flask(__name__)

# เก็บข้อมูลพอร์ต
stats = {
    "balance": 0,
    "equity": 0,
    "trades": [],
    "win_rate": 0,
    "drawdown": 0
}

@app.route("/get_signal")
def get_signal():
    decision = np.random.choice([1, -1, 0])
    confidence = np.random.uniform(0.6, 0.95)
    return jsonify({
        "decision": int(decision),
        "confidence": round(confidence, 2)
    })

@app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    if data:
        stats["balance"] = data.get("balance", 0)
        stats["equity"] = data.get("equity", 0)
    return jsonify({"status": "updated"})

@app.route("/dashboard")
def dashboard():
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)