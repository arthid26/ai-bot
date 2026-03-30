import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sunbike AI Multi-Broker", page_icon="🚀", layout="wide")

# CSS สำหรับ Dark Theme (เหมือนเดิมที่คุณชอบ)
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Sunbike AI Multi-Broker Command Center")
API_URL = "https://my-ai-trading.onrender.com/dashboard"

placeholder = st.empty()

while True:
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            all_res = response.json()
            
            with placeholder.container():
                # สร้าง Tabs แยกตามโบรกเกอร์
                brokers = list(all_res.keys())
                tabs = st.tabs([f"📊 {b}" for b in brokers])

                for i, broker in enumerate(brokers):
                    res = all_res[broker]
                    with tabs[i]:
                        # --- Metrics ---
                        m1, m2, m3, m4 = st.columns(4)
                        bal, eq = res.get('balance', 0.0), res.get('equity', 0.0)
                        
                        m1.metric(f"💰 {broker} Balance", f"${bal:,.2f}")
                        m2.metric("📈 Equity", f"${eq:,.2f}", f"{eq-bal:+,.2f}")
                        m3.metric("💵 Today Profit", f"${res.get('today_profit', 0.0):+,.2f}")
                        m4.metric("🎯 Win Rate", f"{res.get('win_rate', 0.0):.1f}%")

                        # --- Graph & Table ---
                        c_left, c_right = st.columns([2, 1])
                        with c_left:
                            st.subheader("Equity Curve")
                            history = res.get('equity_history', [])
                            if history:
                                st.area_chart(pd.DataFrame(history, columns=["Value"]), color="#00ff00")
                        
                        with c_right:
                            st.subheader("Active Symbols")
                            multi = res.get('multi_symbol', {})
                            if multi:
                                df = pd.DataFrame(list(multi.items()), columns=['Symbol', 'Profit'])
                                st.table(df)
                            else:
                                st.write("No active trades.")

        else:
            st.warning("Connecting to server...")
            
    except Exception as e:
        st.error(f"Connection lost. Retrying...")
    
    time.sleep(10)