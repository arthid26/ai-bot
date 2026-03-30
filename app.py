import streamlit as st
import requests
import time
import json
import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- 1. ส่วนของ BACKEND (Flask) ---
flask_app = Flask(__name__)
CORS(flask_app)

DB_FILE = "stats_db.json"

# ฟังก์ชันช่วยโหลด/เซฟข้อมูลลงไฟล์
def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if not os.path.exists(DB_FILE):
        return {"XM": {"balance": 0.0, "equity": 0.0, "equity_history": [], "multi_symbol": {}},
                "Exness": {"balance": 0.0, "equity": 0.0, "equity_history": [], "multi_symbol": {}}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

@flask_app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    broker = data.get("broker", "Unknown")
    db = load_data()
    
    if broker not in db:
        db[broker] = {"balance": 0.0, "equity": 0.0, "equity_history": [], "multi_symbol": {}}
    
    db[broker]["balance"] = data.get("balance", db[broker]["balance"])
    db[broker]["equity"] = data.get("equity", db[broker]["equity"])
    db[broker]["multi_symbol"] = data.get("multi_symbol", {})
    
    db[broker]["equity_history"].append(db[broker]["equity"])
    if len(db[broker]["equity_history"]) > 50: db[broker]["equity_history"].pop(0)
    
    save_data(db) # เขียนลงไฟล์ทันที
    return jsonify({"status": "updated"})

def run_flask():
    flask_app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

# รัน Backend
if not hasattr(st, 'already_started'):
    threading.Thread(target=run_flask, daemon=True).start()
    st.already_started = True

# --- 2. ส่วนของ FRONTEND (Streamlit) ---
st.set_page_config(page_title="Sunbike AI Hybrid V5", layout="wide")
st.title("🚀 Sunbike AI Hybrid Command Center")

placeholder = st.empty()

while True:
    all_res = load_data() # อ่านข้อมูลจากไฟล์โดยตรง
    with placeholder.container():
        brokers = list(all_res.keys())
        tabs = st.tabs([f"📊 {b}" for b in brokers])
        
        for i, b in enumerate(brokers):
            res = all_res[b]
            with tabs[i]:
                c1, c2, c3 = st.columns(3)
                bal, eq = res['balance'], res['equity']
                c1.metric("Balance", f"${bal:,.2f}")
                c2.metric("Equity", f"${eq:,.2f}")
                c3.metric("Floating", f"${eq - bal:+,.2f}")
                
                if res['equity_history']:
                    st.line_chart(res['equity_history'])
    
    time.sleep(5)