"""
Flask API Server untuk Water Potability Prediction Model
Menggunakan ngrok untuk expose API ke internet
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

# ============================================================
# Inisialisasi Flask App
# ============================================================
app = Flask(__name__)
CORS(app)  # Mengizinkan semua request dari domain berbeda (CORS)

# ============================================================
# Load Model ML
# ============================================================
MODEL_PATH = os.path.join(os.path.dirname(__file__), "water_potability_model.pkl")

print(f"[INFO] Memuat model dari: {MODEL_PATH}")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
print("[OK] Model berhasil dimuat!")

# ============================================================
# Route: Health Check
# ============================================================
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "message": "Water Potability API aktif",
        "endpoints": {
            "/predict": "POST - Prediksi kualitas air",
            "/": "GET - Health check"
        }
    })

# ============================================================
# Route: Prediksi Kualitas Air
# ============================================================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Urutan fitur sesuai model training
        feature_order = [
            "ph", "Hardness", "Solids", "Chloramines",
            "Sulfate", "Conductivity", "Organic_carbon",
            "Trihalomethanes", "Turbidity"
        ]

        # Validasi: Pastikan semua fitur tersedia
        missing = [f for f in feature_order if f not in data]
        if missing:
            return jsonify({
                "error": f"Parameter yang hilang: {', '.join(missing)}"
            }), 400

        # Konversi input menjadi array numpy
        features = np.array([[float(data[f]) for f in feature_order]])

        # Prediksi menggunakan model
        prediction = model.predict(features)[0]

        # Coba ambil probabilitas (jika model mendukung)
        confidence = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)[0]
            confidence = {
                "tidak_layak": round(float(proba[0]) * 100, 2),
                "layak": round(float(proba[1]) * 100, 2)
            }

        return jsonify({
            "potability": int(prediction),
            "label": "Layak Minum" if prediction == 1 else "Tidak Layak",
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Main: Jalankan Flask saja (ngrok dijalankan terpisah)
# ============================================================
if __name__ == "__main__":
    PORT = 5000
    print(f"\n[INFO] Flask server berjalan di http://127.0.0.1:{PORT}")
    print("[INFO] Jalankan ngrok terpisah: ngrok http {PORT}\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
