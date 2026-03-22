import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Sunbike AI Pro", layout="wide")

st.title("🚀 Sunbike AI Pro Command Center")

API_URL = "https://my-ai-trading.onrender.com/dashboard"
placeholder = st.empty()

while True:
    try:
        res = requests.get(API_URL).json()
        with placeholder.container():
            # ส่วนที่ 1: Metrics หลัก และความร้อนแรงตลาด
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Balance", f"${res['balance']:,.2f}")
            col2.metric("📈 Equity", f"${res['equity']:,.2f}")
            
            heat = res.get('market_heat', 0)
            heat_color = "🔴 Hot" if heat > 70 else "🟢 Calm"
            col3.metric("🔥 Market Heat", f"{heat}%", f"Status: {heat_color}")

            # ส่วนที่ 2: กราฟกำไร (Equity Curve)
            st.subheader("📊 Equity Curve (Last 50 Updates)")
            if res['equity_history']:
                st.line_chart(res['equity_history'])
            
            # ส่วนที่ 3: ประวัติการเทรด 5 ไม้ล่าสุด
            st.subheader("📜 Last 5 Trades")
            if res['last_trades']:
                df = pd.DataFrame(res['last_trades'])
                st.table(df) # แสดงเป็นตารางสวยๆ
            else:
                st.info("ยังไม่มีประวัติการเทรดในเซสชั่นนี้")
                
    except Exception as e:
        st.error("Connecting to Server...")
    time.sleep(10)