import streamlit as st
import requests
import time
import pandas as pd

# 1. ตั้งค่าหน้าจอ (UI Configuration)
st.set_page_config(
    page_title="Sunbike AI Pro V4", 
    page_icon="🚀", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ปรับแต่ง CSS เพื่อความสวยงามแบบ Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { 
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Sunbike AI Pro Command Center")
st.caption("Real-time MT5 AI Intelligence Monitoring System")
st.markdown("---")

API_URL = "https://my-ai-trading.onrender.com/dashboard"
placeholder = st.empty()

while True:
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            res = response.json()
            
            with placeholder.container():
                # --- ส่วนที่ 1: การเงินหลัก (Core Metrics) ---
                col1, col2, col3, col4 = st.columns(4)
                
                bal = res.get('balance', 0.0)
                eq = res.get('equity', 0.0)
                today_p = res.get('today_profit', 0.0)
                win_rate = res.get('win_rate', 0.0)
                dd = res.get('drawdown', 0.0)
                total_t = res.get('total_trades', 0)
                floating = eq - bal
                
                # แสดงผล Metrics
                col1.metric("💰 Account Balance", f"${bal:,.2f}")
                col2.metric("📈 Current Equity", f"${eq:,.2f}", f"{floating:+,.2f} Floating")
                
                # กำไรวันนี้ (ถ้าบวกเป็นสีเขียว ถ้าลบเป็นสีแดง)
                p_label = "💵 Today Profit"
                col3.metric(p_label, f"${today_p:+,.2f}", delta_color="normal" if today_p >= 0 else "inverse")
                
                col4.metric("🎯 Win Rate", f"{win_rate:.1f}%", f"{total_t} Trades")

                st.write("") # เว้นวรรค

                # --- ส่วนที่ 2: วิเคราะห์ความเสี่ยงและกราฟเส้น ---
                c_left, c_right = st.columns([1, 3])

                with c_left:
                    st.subheader("🛡️ Risk Guard")
                    
                    # วงจรความปลอดภัย (Drawdown Alert)
                    if dd > 10:
                        st.error(f"Drawdown: {dd:.2f}% (High Risk!)")
                    elif dd > 5:
                        st.warning(f"Drawdown: {dd:.2f}% (Caution)")
                    else:
                        st.success(f"Drawdown: {dd:.2f}% (Safe)")
                    
                    st.write("---")
                    st.code(f"SYSTEM: HYBRID V3.0\nMARKET: EURUSD/EV\nSTATUS: ONLINE\nSYNC: SUCCESS", language="bash")
                    
                    if st.button("🔄 Manual Refresh"):
                        st.rerun()

                with c_right:
                    st.subheader("📊 Equity Growth Curve")
                    history = res.get('equity_history', [])
                    if history:
                        # สร้าง DataFrame และพล็อตกราฟพื้นที่ (Area Chart) ให้ดูสวยงาม
                        df_chart = pd.DataFrame(history, columns=["Portfolio Value"])
                        st.area_chart(df_chart, use_container_width=True, color="#00ff00")
                    else:
                        st.info("⏳ Waiting for more data points from MT5 to build the chart...")

        else:
            st.warning("⚠️ Render Server is starting up... Please wait about 30-60 seconds.")
                
    except Exception as e:
        st.error("🔄 Lost connection to Server. Retrying in 10s...")
        
    time.sleep(10)