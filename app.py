from flask import Flask, jsonify, request
import numpy as np
import datetime

app = Flask(__name__)

# ระบบจัดเก็บข้อมูลที่ละเอียดขึ้น
stats = {
    "balance": 0.0,
    "equity": 0.0,
    "equity_history": [],  # เก็บไว้ทำกราฟ Equity Curve
    "last_trades": [],      # เก็บประวัติ 5 ไม้ล่าสุด
    "market_heat": 0        # ความร้อนแรงของตลาด (0-100)
}

@app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    if not data: return jsonify({"error": "No data"}), 400
    
    # 1. อัปเดตยอดเงิน
    stats["balance"] = data.get("balance", stats["balance"])
    stats["equity"] = data.get("equity", stats["equity"])
    
    # 2. บันทึกประวัติ Equity (เก็บไว้ไม่เกิน 50 จุดเพื่อประหยัดพื้นที่)
    stats["equity_history"].append(stats["equity"])
    if len(stats["equity_history"]) > 50:
        stats["equity_history"].pop(0)
        
    # 3. รับประวัติการเทรด (ถ้าส่งมาจาก MT5)
    if "last_trades" in data:
        stats["last_trades"] = data["last_trades"][:5] # เอาแค่ 5 ไม้ล่าสุด
        
    # 4. คำนวณความร้อนแรงตลาด (จำลองจากความผันผวน)
    stats["market_heat"] = np.random.randint(30, 95)
    
    return jsonify({"status": "updated"})

@app.route("/dashboard")
def dashboard():
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)