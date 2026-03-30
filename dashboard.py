import os
import sys

# บังคับให้ระบบไปรันไฟล์ app.py แทนตัวมันเอง
if __name__ == "__main__":
    # ตรวจสอบว่ามีไฟล์ app.py อยู่จริงไหม
    if os.path.exists("app.py"):
        print("🚀 Redirecting to app.py...")
        # ใช้คำสั่งรัน streamlit ผ่านระบบภายใน
        os.system(f"{sys.executable} -m streamlit run app.py --server.port {os.environ.get('PORT', 8501)} --server.address 0.0.0.0")
    else:
        print("❌ Error: app.py not found!")