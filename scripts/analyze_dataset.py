"""
Analisis dataset untuk memahami range nilai sesungguhnya dan
menemukan sampel yang diprediksi AMAN vs TIDAK AMAN.
"""
import csv, pickle, numpy as np, warnings
warnings.filterwarnings('ignore')

with open('model/water_potability_model.pkl','rb') as f:
    model = pickle.load(f)

feature_cols = ['ph','Hardness','Solids','Chloramines','Sulfate',
                'Conductivity','Organic_carbon','Trihalomethanes','Turbidity']

rows = []
with open('water_potability.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

means = {}
stds  = {}
mins  = {}
maxs  = {}
for col in feature_cols:
    vals = [float(r[col]) for r in rows if r[col].strip() not in ('','nan','NaN')]
    means[col] = np.mean(vals)
    stds[col]  = np.std(vals)
    mins[col]  = np.min(vals)
    maxs[col]  = np.max(vals)

print("=== STATISTIK DATASET SESUNGGUHNYA ===")
print(f"{'Feature':<20} {'Min':>8} {'Mean':>10} {'Max':>10} {'Std':>10}")
print("-"*62)
for col in feature_cols:
    print(f"{col:<20} {mins[col]:>8.2f} {means[col]:>10.2f} {maxs[col]:>10.2f} {stds[col]:>10.2f}")

# Cari sampel AMAN (class=1) yang diprediksi benar oleh model
print("\n=== SAMPEL DARI DATASET YANG DIPREDIKSI AMAN (class=1) ===")
aman_count = 0
for row in rows:
    try:
        x = [float(row[c]) if row[c].strip() not in ('','nan','NaN') else means[c] for c in feature_cols]
        y_true = int(row['Potability'])
        if y_true == 1:
            X = np.array([x], dtype=np.float32)
            pred = model.predict(X)[0]
            proba = model.predict_proba(X)[0]
            if pred == 1 and aman_count < 3:
                print(f"\nSampel AMAN #{aman_count+1} (prob_aman={proba[1]:.2f}):")
                for i, col in enumerate(feature_cols):
                    print(f"  {col}: {x[i]:.4f}")
                aman_count += 1
    except:
        pass

print(f"\n=== PERBANDINGAN RANGE UI vs DATASET ===")
ui_ranges = {
    'ph': (6.5, 8.5), 'Hardness': (0, 200), 'Solids': (0, 500),
    'Chloramines': (0, 4), 'Sulfate': (0, 250), 'Conductivity': (0, 400),
    'Organic_carbon': (0, 10), 'Trihalomethanes': (0, 80), 'Turbidity': (0, 5)
}
print(f"{'Feature':<20} {'UI_min':>8} {'UI_max':>8} {'DS_mean':>10} {'DS_max':>10} {'COCOK?':>8}")
print("-"*68)
for col in feature_cols:
    ui_min, ui_max = ui_ranges[col]
    match = "OK" if abs(ui_max - means[col]) / max(means[col],1) < 1.0 else "SALAH!"
    print(f"{col:<20} {ui_min:>8.1f} {ui_max:>8.1f} {means[col]:>10.2f} {maxs[col]:>10.2f} {match:>8}")
