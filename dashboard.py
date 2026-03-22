import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Sunbike AI Dashboard", layout="centered")

# หัวข้อ Dashboard
st.title("🤖 Sunbike AI Trend Dashboard")

# URL ของ Render ของคุณ
API_URL = "https://my-ai-trading.onrender.com/dashboard"

placeholder = st.empty()

while True:
    try:
        # ดึงข้อมูลจาก Cloud
        res = requests.get(API_URL).json()
        
        with placeholder.container():
            # แสดงค่า Balance และ Equity เป็นตัวเลขใหญ่ๆ
            col1, col2 = st.columns(2)
            col1.metric("💰 Balance", f"${res['balance']:,.2f}")
            col2.metric("📈 Equity", f"${res['equity']:,.2f}")
            
            # แสดงสถานะความมั่นใจของ AI
            st.write("---")
            st.subheader("📊 AI Analytics")
            st.progress(int(res.get('win_rate', 0))) # แถบพลัง Win Rate
            st.write(f"Win Rate: {res.get('win_rate', 0)}%")
            
            # แสดงกราฟกำไร (ถ้ามีข้อมูล trades)
            if res['trades']:
                st.line_chart(res['trades'])
            else:
                st.info("⏳ รอข้อมูลการเทรดนัดแรกจากตลาดวันจันทร์...")

    except Exception as e:
        st.error(f"กำลังเชื่อมต่อกับ Server... ")
        
    time.sleep(10) # อัปเดตหน้าจอทุก 10 วินาที