import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

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

# เปลี่ยน URL ให้ตรงกับแอปของคุณ (ตรวจสอบชื่อ my-ai-trading อีกครั้ง)
API_URL = "https://my-ai-trading.onrender.com/dashboard"

# จองพื้นที่สำหรับแสดงสถานะ (Error/Warning) ไว้ด้านบนสุดของเนื้อหา
status_msg = st.empty()
# จองพื้นที่สำหรับเนื้อหาหลัก
placeholder = st.empty()

while True:
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            res = response.json()
            
            # ✅ ล้างแถบ Error/Warning ออกทันทีเมื่อเชื่อมต่อสำเร็จ
            status_msg.empty()
            
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
                
                col1.metric("💰 Account Balance", f"${bal:,.2f}")
                col2.metric("📈 Current Equity", f"${eq:,.2f}", f"{floating:+,.2f} Floating")
                
                # กำไรวันนี้
                col3.metric("💵 Today Profit", f"${today_p:+,.2f}", delta_color="normal" if today_p >= 0 else "inverse")
                col4.metric("🎯 Win Rate", f"{win_rate:.1f}%", f"{total_t} Trades")

                st.write("") 

                # --- ส่วนที่ 2: วิเคราะห์ความเสี่ยงและกราฟเส้น ---
                c_left, c_right = st.columns([1, 3])

                with c_left:
                    st.subheader("🛡️ Risk Guard")
                    if dd > 10:
                        st.error(f"Drawdown: {dd:.2f}% (High Risk!)")
                    elif dd > 5:
                        st.warning(f"Drawdown: {dd:.2f}% (Caution)")
                    else:
                        st.success(f"Drawdown: {dd:.2f}% (Safe)")
                    
                    st.write("---")
                    st.code(f"SYSTEM: HYBRID V4.0\nSTATUS: ONLINE\nSYNC: SUCCESS", language="bash")
                    
                    if st.button("🔄 Manual Refresh"):
                        st.rerun()

                with c_right:
                    st.subheader("📊 Equity Growth Curve")
                    history = res.get('equity_history', [])
                    if history:
                        df_chart = pd.DataFrame(history, columns=["Portfolio Value"])
                        st.area_chart(df_chart, use_container_width=True, color="#00ff00")
                    else:
                        st.info("⏳ Waiting for more data points from MT5...")

                st.markdown("---")

                # --- ส่วนที่ 3: รายละเอียดรายคู่เงิน (Multi-Symbol View) ---
                st.subheader("📋 Active Positions Summary")
                multi_data = res.get('multi_symbol', {})

                if multi_data and isinstance(multi_data, dict) and len(multi_data) > 0:
                    col_table, col_pie = st.columns([2, 1])
                    
                    with col_table:
                        df_multi = pd.DataFrame(list(multi_data.items()), columns=['Symbol', 'Profit ($)'])
                        
                        def color_profit(val):
                            color = '#00ff00' if val > 0 else '#ff4b4b'
                            return f'color: {color}'
                        
                        st.dataframe(
                            df_multi.style.applymap(color_profit, subset=['Profit ($)']).format({'Profit ($)': '{:.2f}'}),
                            use_container_width=True,
                            hide_index=True
                        )

                    with col_pie:
                        if df_multi['Profit ($)'].abs().sum() > 0:
                            fig = px.pie(df_multi, values=df_multi['Profit ($)'].abs(), names='Symbol', 
                                        hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=200)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.write("📊 No profit data to display chart.")
                else:
                    st.info("🟢 No active positions at the moment.")

        else:
            # ใช้ status_msg ในการแสดงคำเตือน เพื่อให้หายไปเมื่อเชื่อมต่อได้
            status_msg.warning("⚠️ Render Server is starting up... Please wait.")
                
    except Exception as e:
        # ✅ เมื่อเกิด Error จะแสดงที่ status_msg เพียงแถบเดียว ไม่สะสมซ้อนกัน
        status_msg.error(f"🔄 Lost connection to Server. Retrying in 10s...")
        
    time.sleep(10)