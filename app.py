from flask import Flask, jsonify
import numpy as np
import datetime

app = Flask(__name__)

# --- จำลองส่วนของ AI Ensemble (ในอนาคตเราจะใส่ Model จริงตรงนี้) ---
def get_ai_signal():
    # โหวตจาก 3 Models (Random Forest, XGBoost, LGBM)
    models = [np.random.choice([1, -1]), np.random.choice([1, -1]), np.random.choice([1, -1])]
    score = sum(models)
    
    decision = 0
    if score >= 2: decision = 1  # Buy
    if score <= -2: decision = -1 # Sell
    
    confidence = np.random.uniform(0.65, 0.95) # ความเชื่อมั่น
    return decision, confidence, models

@app.route("/")
def home():
    return "AI Trading Server is Online!"

@app.route("/get_signal")
def signal():
    decision, confidence, models = get_ai_signal()
    return jsonify({
        "status": "success",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decision": decision,
        "confidence": round(confidence, 2),
        "m1": int(models[0]),
        "m2": int(models[1]),
        "m3": int(models[2])
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)