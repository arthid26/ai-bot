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

# กำหนด Path ไฟล์ให้แน่นอน (ใช้ที่เดียวกับไฟล์โค้ด)
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(current_dir, "stats_db.json")

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if not os.path.exists(DB_FILE):
        return {"XM": {"balance": 0.0, "equity": 0.0, "equity_history": []},
                "Exness": {"balance": 0.0, "equity": 0.0, "equity_history": []}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

@flask_app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    broker = data.get("broker", "Unknown")
    db = load_data()
    
    if broker not in db:
        db[broker] = {"balance": 0.0, "equity": 0.0, "equity_history": []}
    
    db[broker]["balance"] = data.get("balance", 0)
    db[broker]["equity"] = data.get("equity", 0)
    db[broker]["equity_history"].append(db[broker]["equity"])
    
    if len(db[broker]["equity_history"]) > 50: db[broker]["equity_history"].pop(0)
    
    save_data(db)
    return jsonify({"status": "success", "received": broker})

def run_flask():
    flask_app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

if not hasattr(st, 'already_started'):
    threading.Thread(target=run_flask, daemon=True).start()
    st.already_started = True

# --- 2. ส่วนของ FRONTEND (Streamlit) ---
st.set_page_config(page_title="Sunbike AI Hybrid V6", layout="wide")

# ส่วน Debug (เอาไว้เช็คว่าไฟล์มาไหม)
with st.sidebar:
    st.header("⚙️ System Check")
    if os.path.exists(DB_FILE):
        st.success(f"Database File: Found")
        st.write(f"Last Updated: {time.ctime(os.path.getmtime(DB_FILE))}")
    else:
        st.error("Database File: Not Found (Waiting for bot...)")

st.title("🚀 Sunbike AI Hybrid Command Center")
placeholder = st.empty()

while True:
    all_res = load_data()
    with placeholder.container():
        if all_res:
            tabs = st.tabs([f"📊 {b}" for b in all_res.keys()])
            for i, b in enumerate(all_res.keys()):
                res = all_res[b]
                with tabs[i]:
                    c1, c2 = st.columns(2)
                    c1.metric("Balance", f"${res['balance']:,.2f}")
                    c2.metric("Equity", f"${res['equity']:,.2f}")
                    if res['equity_history']:
                        st.line_chart(res['equity_history'])
    time.sleep(5)