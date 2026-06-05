"""
Backend Flask - Prediksi kualitas air menggunakan model .pkl
Pendekatan: Hybrid scoring (Rule-based + ML probability)
"""
import warnings
warnings.filterwarnings('ignore')

import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Konfigurasi range aman (harus sinkron dengan featureConfig di App.jsx) ──
FEATURE_CONFIG = {
    'ph':              {'min': 6.5,   'max': 8.5,   'label': 'Tingkat pH'},
    'Hardness':        {'min': 150,   'max': 250,   'label': 'Kekerasan Air'},
    'Solids':          {'min': 10000, 'max': 35000, 'label': 'TDS (Padatan)'},
    'Chloramines':     {'min': 5,     'max': 9,     'label': 'Kloramin'},
    'Sulfate':         {'min': 280,   'max': 400,   'label': 'Sulfat'},
    'Conductivity':    {'min': 300,   'max': 600,   'label': 'Konduktivitas'},
    'Organic_carbon':  {'min': 8,     'max': 20,    'label': 'Karbon Organik'},
    'Trihalomethanes': {'min': 30,    'max': 100,   'label': 'Trihalometana'},
    'Turbidity':       {'min': 1.5,   'max': 5,     'label': 'Kekeruhan'},
}

FEATURE_ORDER = list(FEATURE_CONFIG.keys())

# ── Load model ──
print("Memuat model pkl...")
with open('model/water_potability_model.pkl', 'rb') as f:
    model = pickle.load(f)
print(f"Model siap: {type(model).__name__}")


def rule_score(values: dict) -> float:
    """
    Hitung skor berbasis aturan range aman.
    Setiap fitur dalam range aman mendapat skor penuh,
    fitur di luar range mendapat skor berdasarkan jarak dari batas.
    Return: float 0.0 – 1.0
    """
    scores = []
    for key, cfg in FEATURE_CONFIG.items():
        val = values[key]
        lo, hi = cfg['min'], cfg['max']
        mid = (lo + hi) / 2
        half_range = (hi - lo) / 2

        if lo <= val <= hi:
            # Dalam range — skor penuh
            scores.append(1.0)
        else:
            # Luar range — skor turun proporsional
            dist = max(val - hi, lo - val)          # jarak ke batas terdekat
            penalty = min(dist / (half_range + 1e-9), 1.0)
            scores.append(max(0.0, 1.0 - penalty))

    return float(np.mean(scores))


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Data tidak ditemukan'}), 400

        values = {}
        for key in FEATURE_ORDER:
            if key not in data:
                return jsonify({'error': f'Fitur "{key}" tidak ada'}), 400
            values[key] = float(data[key])

        features = [values[k] for k in FEATURE_ORDER]
        X = np.array([features], dtype=np.float64)

        # ── ML prediction ──
        ml_prob_aman = float(model.predict_proba(X)[0][1])   # prob class=1

        # ── Rule-based score ──
        rb_score = rule_score(values)

        # ── Hybrid: 55% rule-based + 45% ML ──
        hybrid_score = 0.55 * rb_score + 0.45 * ml_prob_aman

        # ── Override: jika ML sangat yakin, ikuti ML ──
        if ml_prob_aman < 0.15:
            potability = 0   # ML sangat yakin TIDAK AMAN
        elif ml_prob_aman > 0.85:
            potability = 1   # ML sangat yakin AMAN
        else:
            potability = 1 if hybrid_score >= 0.5 else 0

        # Detail per fitur (untuk debugging / transparansi)
        detail = {}
        for key, cfg in FEATURE_CONFIG.items():
            v = values[key]
            status = 'normal' if cfg['min'] <= v <= cfg['max'] else 'out_of_range'
            detail[key] = {'value': v, 'status': status, 'min': cfg['min'], 'max': cfg['max']}

        return jsonify({
            'potability':    potability,          # 0 = tidak aman, 1 = aman
            'hybrid_score':  round(hybrid_score, 3),
            'ml_prob_aman':  round(ml_prob_aman, 3),
            'rule_score':    round(rb_score, 3),
            'detail':        detail,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': type(model).__name__})


if __name__ == '__main__':
    print("Server berjalan di http://localhost:5000")
    app.run(port=5000, debug=False)

