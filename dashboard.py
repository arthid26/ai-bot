import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Sunbike AI Pro V4.2", page_icon="🚀", layout="wide")

# ปรับสไตล์ให้ดู Terminal มากขึ้น
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Sunbike AI Pro Command Center")
st.caption("Intelligence Multi-Symbol Monitoring System")
st.markdown("---")

# *** ตรวจสอบ URL ให้ตรงกับแอปจริงของคุณ ***
API_URL = "https://my-ai-trading.onrender.com/dashboard"
placeholder = st.empty()

while True:
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            res = response.json()
            
            with placeholder.container():
                # --- ส่วนที่ 1: CORE METRICS ---
                m1, m2, m3, m4 = st.columns(4)
                
                bal = res.get('balance', 0.0)
                eq = res.get('equity', 0.0)
                today_p = res.get('today_profit', 0.0)
                win_rate = res.get('win_rate', 0.0)
                floating = eq - bal
                
                m1.metric("💰 Balance", f"${bal:,.2f}")
                m2.metric("📈 Equity", f"${eq:,.2f}", f"{floating:+,.2f} Floating")
                m3.metric("💵 Today Profit", f"${today_p:+,.2f}", delta_color="normal" if today_p >= 0 else "inverse")
                m4.metric("🎯 Win Rate", f"{win_rate:.1f}%")

                st.write("")

                # --- ส่วนที่ 2: RISK & EQUITY CURVE ---
                c_left, c_right = st.columns([1, 3])

                with c_left:
                    st.subheader("🛡️ Risk Guard")
                    dd = res.get('drawdown', 0.0)
                    if dd > 10:
                        st.error(f"Drawdown: {dd:.2f}% (High!)")
                    elif dd > 5:
                        st.warning(f"Drawdown: {dd:.2f}% (Caution)")
                    else:
                        st.success(f"Drawdown: {dd:.2f}% (Safe)")
                    
                    st.write("---")
                    st.code(f"SYSTEM: ONLINE\nTRADES: {res.get('total_trades', 0)}")
                    if st.button("🔄 Refresh"): st.rerun()

                with c_right:
                    st.subheader("📊 Equity Growth")
                    history = res.get('equity_history', [])
                    if history:
                        st.area_chart(pd.DataFrame(history, columns=["Equity"]), color="#00ff00")
                    else:
                        st.info("⏳ Waiting for history data...")

                st.markdown("---")

                # --- ส่วนที่ 3: MULTI-SYMBOL ANALYSIS ---
                st.subheader("📋 Active Positions Summary")
                multi_data = res.get('multi_symbol', {})

                if isinstance(multi_data, dict) and len(multi_data) > 0:
                    col_t, col_p = st.columns([2, 1])
                    
                    with col_t:
                        df_multi = pd.DataFrame(list(multi_data.items()), columns=['Symbol', 'Profit ($)'])
                        # ใส่สีเขียว/แดง ในตาราง
                        st.dataframe(
                            df_multi.style.applymap(lambda x: f"color: {'#00ff00' if x > 0 else '#ff4b4b'}", subset=['Profit ($)'])
                            .format({'Profit ($)': '{:.2f}'}),
                            use_container_width=True
                        )

                    with col_pie:
                        # วาดวงกลมเฉพาะเมื่อมีกำไร/ขาดทุนที่ไม่ใช่ 0
                        if df_multi['Profit ($)'].abs().sum() > 0:
                            fig = px.pie(df_multi, values=df_multi['Profit ($)'].abs(), names='Symbol', hole=0.4)
                            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("🟢 No active positions currently.")

        else:
            st.warning("⚠️ Server is starting up... Please wait.")
                
    except Exception as e:
        st.error("🔄 Lost connection to Server. Retrying...")
        
    time.sleep(10)