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
        response = requests.get(API_URL, timeout=5)
        # ตรวจสอบว่า Render ส่งข้อมูลกลับมาจริงไหม
        if response.status_code == 200:
            res = response.json()
            
            with placeholder.container():
                # ส่วนที่ 1: Metrics
                col1, col2, col3 = st.columns(3)
                bal = res.get('balance', 0.0)
                eq = res.get('equity', 0.0)
                heat = res.get('market_heat', 0)
                
                col1.metric("💰 Balance", f"${bal:,.2f}")
                col2.metric("📈 Equity", f"${eq:,.2f}")
                col3.metric("🔥 Market Heat", f"{heat}%")

                # ส่วนที่ 2: กราฟ + แถบสถานะสีขาว
                st.subheader("📊 Equity Performance")
                history = res.get('equity_history', [])
                
                if history:
                    # --- ตัวหนังสือสีขาว (Status Overlay) ---
                    # เราใช้ st.write ร่วมกับพื้นหลังสีดำเพื่อให้มันแสดงผลได้แน่นอน
                    st.code(f"SYSTEM: ONLINE | BAL: ${bal:,.2f} | EQUITY: ${eq:,.2f}")
                    
                    df_chart = pd.DataFrame(history, columns=["Portfolio Equity"])
                    st.line_chart(df_chart)
                else:
                    st.info("⏳ Waiting for data from MT5...")
        else:
            st.warning("⚠️ Render Server is starting up... (Error 502)")
                
    except Exception as e:
        st.error("🔄 Connecting to Server... โปรดรอสักครู่")
        
    time.sleep(10)