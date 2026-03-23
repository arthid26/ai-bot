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
            # ส่วนที่ 1: Metrics หลัก
            col1, col2, col3 = st.columns(3)
            bal = res.get('balance', 0.0)
            eq = res.get('equity', 0.0)
            heat = res.get('market_heat', 0)
            
            col1.metric("💰 Balance", f"${bal:,.2f}")
            col2.metric("📈 Equity", f"${eq:,.2f}")
            
            heat_color = "🔴 Hot" if heat > 70 else "🟢 Calm"
            col3.metric("🔥 Market Heat", f"{heat}%", f"Status: {heat_color}")

            # ส่วนที่ 2: กราฟกำไร (Equity Curve) พร้อมตัวหนังสือสีขาวมุมซ้าย
            st.subheader("📊 Equity Performance")
            
            history = res.get('equity_history', [])
            if history:
                # --- สร้างตัวหนังสือสีขาวลอยมุมซ้าย (Status Overlay) ---
                st.markdown(
                    f"""
                    <div style="
                        position: absolute; 
                        margin-top: 45px; 
                        margin-left: 20px; 
                        z-index: 100; 
                        color: white; 
                        background-color: rgba(0,0,0,0.6); 
                        padding: 8px 12px; 
                        border-radius: 5px; 
                        font-family: 'Courier New', monospace;
                        font-size: 13px;
                        line-height: 1.4;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <span style="color: #00ff00;">●</span> SYSTEM: ONLINE<br>
                        <span style="color: #ffffff;">BAL: ${bal:,.2f}</span><br>
                        <span style="color: #00fbff;">EQUITY: ${eq:,.2f}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # แสดงกราฟและตั้งชื่อคอลัมน์เพื่อให้ Legend แสดงผล
                df_chart = pd.DataFrame(history, columns=["Portfolio Equity"])
                st.line_chart(df_chart)
            else:
                st.info("⏳ Waiting for Equity Data from MT5...")
            
            # ส่วนที่ 3: ประวัติการเทรด 5 ไม้ล่าสุด
            st.subheader("📜 Last 5 Trades")
            if res.get('last_trades'):
                df = pd.DataFrame(res['last_trades'])
                st.table(df)
            else:
                st.info("ยังไม่มีประวัติการเทรดในเซสชั่นนี้")
                
    except Exception as e:
        st.error(f"Connecting to Server... {e}")
        
    time.sleep(10)