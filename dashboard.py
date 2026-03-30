from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# โครงสร้างข้อมูลใหม่: แยกเก็บตามชื่อโบรกเกอร์ที่ส่งมาจาก Portfolio Manager
stats_db = {
    "XM": {
        "balance": 0.0, "equity": 0.0, "today_profit": 0.0,
        "win_rate": 0.0, "drawdown": 0.0, "total_trades": 0,
        "equity_history": [], "multi_symbol": {}, "market_heat": 50
    },
    "Exness": {
        "balance": 0.0, "equity": 0.0, "today_profit": 0.0,
        "win_rate": 0.0, "drawdown": 0.0, "total_trades": 0,
        "equity_history": [], "multi_symbol": {}, "market_heat": 50
    }
}

@app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    if not data: return jsonify({"error": "No data"}), 400
    
    # รับชื่อโบรกเกอร์ (Exness หรือ XM) ที่เราตั้งไว้ในบอท Portfolio Manager
    broker = data.get("broker", "Unknown")
    
    if broker not in stats_db:
        stats_db[broker] = {
            "balance": 0.0, "equity": 0.0, "today_profit": 0.0,
            "win_rate": 0.0, "drawdown": 0.0, "total_trades": 0,
            "equity_history": [], "multi_symbol": {}, "market_heat": 50
        }

    target = stats_db[broker]
    target["balance"] = data.get("balance", target["balance"])
    target["equity"] = data.get("equity", target["equity"])
    target["today_profit"] = data.get("today_profit", 0.0)
    target["win_rate"] = data.get("win_rate", 0.0)
    target["drawdown"] = data.get("drawdown", 0.0)
    target["total_trades"] = data.get("total_trades", 0)
    target["multi_symbol"] = data.get("multi_symbol", {})
    
    target["equity_history"].append(target["equity"])
    if len(target["equity_history"]) > 50:
        target["equity_history"].pop(0)
        
    target["market_heat"] = np.random.randint(30, 95)
    
    print(f"✅ Received from {broker} | Bal: {target['balance']}")
    return jsonify({"status": "updated", "broker": broker})

@app.route("/dashboard")
def dashboard():
    return jsonify(stats_db)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)