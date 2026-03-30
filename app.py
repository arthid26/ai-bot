import streamlit as st
import requests
import time
import json
import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS

flask_app = Flask(__name__)
CORS(flask_app)

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(current_dir, "stats_db.json")

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if not os.path.exists(DB_FILE):
        # เริ่มต้นด้วยค่าว่าง เพื่อให้บอทส่งอะไรมาก็ได้
        return {}
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
    
    # ถ้าส่งมาแล้วไม่มีชื่อนี้ในระบบ ให้สร้างใหม่ทันที (ไม่สนตัวพิมพ์ใหญ่เล็ก)
    if broker not in db:
        db[broker] = {"balance": 0.0, "equity": 0.0, "equity_history": []}
    
    db[broker]["balance"] = float(data.get("balance", 0))
    db[broker]["equity"] = float(data.get("equity", 0))
    db[broker]["equity_history"].append(db[broker]["equity"])
    
    if len(db[broker]["equity_history"]) > 50: db[broker]["equity_history"].pop(0)
    
    save_data(db)
    print(f"✅ Updated {broker}: {db[broker]['balance']}")
    return jsonify({"status": "success", "broker": broker})

def run_flask():
    flask_app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

if not hasattr(st, 'already_started'):
    threading.Thread(target=run_flask, daemon=True).start()
    st.already_started = True

# --- UI ---
st.set_page_config(page_title="Sunbike AI Hybrid V7", layout="wide")

all_res = load_data()

st.title("🚀 Sunbike AI Hybrid Command Center")

if not all_res:
    st.warning("⏳ Waiting for data from MT5... Please check Stats_URL in your Bot.")
    # จำลองปุ่มทดสอบส่งข้อมูล (เพื่อเช็คว่าหน้าจอทำงานได้ไหม)
    if st.button("Test Local Update"):
        test_data = {"XM": {"balance": 1000.0, "equity": 1050.0, "equity_history": [1050.0]}}
        save_data(test_data)
        st.rerun()
else:
    tabs = st.tabs([f"📊 {b}" for b in all_res.keys()])
    for i, b in enumerate(all_res.keys()):
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
st.rerun()