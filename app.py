from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import datetime

app = Flask(__name__)

# เก็บข้อมูลพอร์ตชั่วคราว (ในอนาคตควรใช้ฐานข้อมูล)
stats = {
    "balance": 0,
    "equity": 0,
    "trades": [],
    "win_rate": 0,
    "drawdown": 0
}

@app.route("/get_signal")
def get_signal():
    # ระบบ AI หลาย Timeframe (จำลอง)
    m15_dec = np.random.choice([1, -1, 0])
    h1_dec = np.random.choice([1, -1])
    
    # ถ้าเทรนด์ใหญ่ (H1) กับจุดเข้า (M15) ตรงกัน ความมั่นใจจะสูง
    decision = h1_dec if m15_dec == h1_dec else 0
    confidence = np.random.uniform(0.85, 0.98) if decision != 0 else np.random.uniform(0.5, 0.7)
    
    return jsonify({
        "decision": int(decision),
        "confidence": round(confidence, 2),
        "timeframe_sync": "Match" if decision != 0 else "Wait"
    })

@app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    stats["balance"] = data.get("balance")
    stats["equity"] = data.get("equity")
    
    # คำนวณกำไรสะสม (จำลองกราฟ)
    if "profit" in data:
        stats["trades"].append(data["profit"])
        
    # คำนวณ Win Rate
    if len(stats["trades"]) > 0:
        wins = len([p for p in stats["trades"] if p > 0])
        stats["win_rate"] = (wins / len(stats["trades"])) * 100
        
    return jsonify({"status": "updated"})

@app.route("/dashboard")
def dashboard():
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)