from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app) # อนุญาตให้ Dashboard ดึงข้อมูลข้าม Domain ได้

# ระบบจัดเก็บข้อมูลที่รองรับ Dashboard V4.1
stats = {
    "balance": 0.0,
    "equity": 0.0,
    "today_profit": 0.0,  # เพิ่มใหม่
    "win_rate": 0.0,      # เพิ่มใหม่
    "drawdown": 0.0,      # เพิ่มใหม่
    "total_trades": 0,    # เพิ่มใหม่
    "equity_history": [],
    "multi_symbol": {},   # เพิ่มใหม่ (สำหรับตารางรายคู่เงิน)
    "market_heat": 0
}

@app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    if not data: 
        return jsonify({"error": "No data"}), 400
    
    # 1. อัปเดตข้อมูลพื้นฐานและข้อมูลเชิงลึกจาก MT5
    stats["balance"] = data.get("balance", stats["balance"])
    stats["equity"] = data.get("equity", stats["equity"])
    stats["today_profit"] = data.get("today_profit", stats["today_profit"])
    stats["win_rate"] = data.get("win_rate", stats["win_rate"])
    stats["drawdown"] = data.get("drawdown", stats["drawdown"])
    stats["total_trades"] = data.get("total_trades", stats["total_trades"])
    
    # 2. อัปเดตข้อมูลรายคู่เงิน (ตัวที่ทำให้ Dashboard ค้างถ้าไม่มี)
    stats["multi_symbol"] = data.get("multi_symbol", {})
    
    # 3. บันทึกประวัติ Equity ทำกราฟ
    stats["equity_history"].append(stats["equity"])
    if len(stats["equity_history"]) > 50:
        stats["equity_history"].pop(0)
        
    # 4. สุ่มค่าความร้อนแรงตลาด (เพื่อความสวยงามบน Dashboard)
    stats["market_heat"] = np.random.randint(30, 95)
    
    print(f"✅ Received Data: Bal: {stats['balance']} | Symbols: {list(stats['multi_symbol'].keys())}")
    return jsonify({"status": "updated"})

@app.route("/dashboard")
def dashboard():
    # ส่งข้อมูลทั้งหมดให้ Streamlit
    return jsonify(stats)

if __name__ == "__main__":
    import os
    # กำหนดพอร์ตให้รองรับ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)