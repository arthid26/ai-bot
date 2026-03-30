import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
from flask import Flask, jsonify, request
from flask_cors import CORS
import multiprocessing
import os
import numpy as np

# ==========================================
# PART 1: FLASK BACKEND (รันเบื้องหลัง)
# ==========================================
def run_flask():
    flask_app = Flask(__name__)
    CORS(flask_app)

    # ใช้ Dictionary เก็บข้อมูลแยกโบรกเกอร์
    stats_db = {
        "XM": {"balance": 0.0, "equity": 0.0, "today_profit": 0.0, "equity_history": [], "multi_symbol": {}},
        "Exness": {"balance": 0.0, "equity": 0.0, "today_profit": 0.0, "equity_history": [], "multi_symbol": {}}
    }

    @flask_app.route("/update_stats", methods=["POST"])
    def update_stats():
        data = request.json
        broker = data.get("broker", "Unknown")
        if broker not in stats_db:
            stats_db[broker] = {"balance": 0.0, "equity": 0.0, "today_profit": 0.0, "equity_history": [], "multi_symbol": {}}
        
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

    # รัน Flask ที่พอร์ต 5000 (ภายในเครื่อง)
    flask_app.run(host="0.0.0.0", port=5000)

# ==========================================
# PART 2: STREAMLIT FRONTEND (หน้าจอแสดงผล)
# ==========================================
def main_ui():
    st.set_page_config(page_title="Sunbike AI Hybrid", layout="wide")
    st.title("🚀 Sunbike AI Hybrid Command Center")

    # ดึงข้อมูลจาก Flask ภายในเครื่องเอง
    API_URL = "http://127.0.0.1:5000/dashboard_data"
    placeholder = st.empty()

    while True:
        try:
            response = requests.get(API_URL, timeout=5)
            if response.status_code == 200:
                all_res = response.json()
                with placeholder.container():
                    brokers = list(all_res.keys())
                    tabs = st.tabs([f"📊 {b}" for b in brokers])
                    for i, b in enumerate(brokers):
                        res = all_res[b]
                        with tabs[i]:
                            c1, c2 = st.columns(2)
                            c1.metric("Balance", f"${res['balance']:,.2f}")
                            c2.metric("Equity", f"${res['equity']:,.2f}")
                            
                            st.subheader("Equity Curve")
                            if res['equity_history']:
                                st.area_chart(res['equity_history'])
            else:
                st.warning("Waiting for Data...")
        except:
            st.error("Connecting to Backend...")
        time.sleep(5)

# ==========================================
# RUN BOTH
# ==========================================
if __name__ == "__main__":
    # เริ่มรัน Flask เป็น Process แยก
    flask_process = multiprocessing.Process(target=run_flask)
    flask_process.daemon = True
    flask_process.start()
    
    # รัน Streamlit UI
    main_ui()