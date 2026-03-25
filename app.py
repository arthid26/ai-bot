from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # อนุญาตให้ Dashboard ดึงข้อมูลได้ไม่ติด Block

# ตัวแปรเก็บข้อมูลสำหรับส่งให้ Dashboard
dashboard_data = {
    "balance": 0.0,
    "equity": 0.0,
    "today_profit": 0.0,
    "win_rate": 0.0,
    "drawdown": 0.0,
    "total_trades": 0,
    "equity_history": [],
    "multi_symbol": {} # ช่องรับข้อมูลรายคู่เงิน
}

@app.route('/update_stats', methods=['POST'])
def update_stats():
    global dashboard_data
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400

        # รับค่าและบันทึกลงตัวแปร
        dashboard_data["balance"] = data.get("balance", dashboard_data["balance"])
        dashboard_data["equity"] = data.get("equity", dashboard_data["equity"])
        dashboard_data["today_profit"] = data.get("today_profit", dashboard_data["today_profit"])
        dashboard_data["win_rate"] = data.get("win_rate", dashboard_data["win_rate"])
        dashboard_data["drawdown"] = data.get("drawdown", dashboard_data["drawdown"])
        dashboard_data["total_trades"] = data.get("total_trades", dashboard_data["total_trades"])
        
        # รับก้อน Multi-Symbol (ตัวนี้สำคัญมาก)
        dashboard_data["multi_symbol"] = data.get("multi_symbol", {})

        # เก็บประวัติทำกราฟ (ถ้าค่าเปลี่ยน)
        dashboard_data["equity_history"].append(dashboard_data["equity"])
        if len(dashboard_data["equity_history"]) > 50:
            dashboard_data["equity_history"].pop(0)

        print("✅ Received data from MT5")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify(dashboard_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) # Render มักใช้พอร์ตนี้