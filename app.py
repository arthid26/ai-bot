import streamlit as st
import requests
import time
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading  # เปลี่ยนจาก multiprocessing เป็น threading เพื่อความเบา
import os

# --- 1. ส่วนของ BACKEND (Flask) ---
flask_app = Flask(__name__)
CORS(flask_app)

# ตัวแปรเก็บข้อมูล (Global)
if 'stats_db' not in st.session_state:
    stats_db = {
        "XM": {"balance": 0.0, "equity": 0.0, "equity_history": [], "multi_symbol": {}},
        "Exness": {"balance": 0.0, "equity": 0.0, "equity_history": [], "multi_symbol": {}}
    }
else:
    stats_db = st.session_state.stats_db

@flask_app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    broker = data.get("broker", "Unknown")
    if broker not in stats_db:
        stats_db[broker] = {"balance": 0.0, "equity": 0.0, "equity_history": [], "multi_symbol": {}}
    
    target = stats_db[broker]
    target["balance"] = data.get("balance", target["balance"])
    target["equity"] = data.get("equity", target["equity"])
    target["multi_symbol"] = data.get("multi_symbol", {})
    
    target["equity_history"].append(target["equity"])
    if len(target["equity_history"]) > 50: target["equity_history"].pop(0)
    return jsonify({"status": "updated"})

@flask_app.route("/dashboard_data")
def dashboard_data():
    return jsonify(stats_db)

# ฟังก์ชันสำหรับรัน Flask แยก Thread (ใช้พอร์ต 5001 เพื่อไม่ให้ชนกับ Streamlit)
def run_flask():
    flask_app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

# สั่งรัน Backend ทันทีที่เปิดแอป (รันแค่ครั้งเดียว)
if not hasattr(st, 'already_started'):
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
    st.already_started = True

# --- 2. ส่วนของ FRONTEND (Streamlit) ---
st.set_page_config(page_title="Sunbike AI Hybrid", layout="wide")

st.title("🚀 Sunbike AI Hybrid Command Center")
st.caption("Monitoring: XM & Exness Real-time")

placeholder = st.empty()

while True:
    try:
        # ดึงข้อมูลจาก Flask พอร์ต 5001
        response = requests.get("http://127.0.0.1:5001/dashboard_data", timeout=2)
        if response.status_code == 200:
            all_res = response.json()
            with placeholder.container():
                brokers = list(all_res.keys())
                tabs = st.tabs([f"📊 {b}" for b in brokers])
                
                for i, b in enumerate(brokers):
                    res = all_res[b]
                    with tabs[i]:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Balance", f"${res['balance']:,.2f}")
                        c2.metric("Equity", f"${res['equity']:,.2f}")
                        c3.metric("Floating", f"${res['equity'] - res['balance']:+,.2f}")
                        
                        if res['equity_history']:
                            st.subheader("Growth Curve")
                            st.line_chart(res['equity_history'])
                        
                        if res['multi_symbol']:
                            st.subheader("Positions")
                            st.write(res['multi_symbol'])
    except:
        st.info("🔄 Connecting to internal backend...")
    
    time.sleep(5)