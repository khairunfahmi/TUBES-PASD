"""
Script untuk melatih ulang model water potability dan export ke ONNX.
Dataset: Kaggle Water Potability Dataset
"""
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. Download dataset
# ============================================================
print("Menggunakan dataset yang sudah ada: water_potability.csv")

# ============================================================
# 2. Load dan preprocessing
# ============================================================
import csv

rows = []
with open("water_potability.csv", newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Total baris: {len(rows)}")

feature_cols = ['ph','Hardness','Solids','Chloramines','Sulfate',
                'Conductivity','Organic_carbon','Trihalomethanes','Turbidity']
label_col = 'Potability'

# Hitung mean tiap kolom untuk imputasi NaN
means = {}
for col in feature_cols:
    vals = [float(r[col]) for r in rows if r[col].strip() not in ('', 'nan', 'NaN')]
    means[col] = sum(vals) / len(vals)
    print(f"  {col}: mean={means[col]:.4f}, missing={len(rows)-len(vals)}")

# Buat X dan y
X_list, y_list = [], []
for row in rows:
    try:
        x = []
        for col in feature_cols:
            val = row[col].strip()
            if val in ('', 'nan', 'NaN'):
                x.append(means[col])
            else:
                x.append(float(val))
        y = int(row[label_col])
        X_list.append(x)
        y_list.append(y)
    except Exception:
        continue

X = np.array(X_list, dtype=np.float32)
y = np.array(y_list, dtype=np.int64)
print(f"\nShape X: {X.shape}, Shape y: {y.shape}")
print(f"Distribusi kelas: 0={sum(y==0)}, 1={sum(y==1)}")

# ============================================================
# 3. Train/test split manual (80/20)
# ============================================================
np.random.seed(42)
idx = np.random.permutation(len(X))
split = int(len(X) * 0.8)
X_train, X_test = X[idx[:split]], X[idx[split:]]
y_train, y_test = y[idx[:split]], y[idx[split:]]
print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# ============================================================
# 4. Latih RandomForestClassifier
# ============================================================
from sklearn.ensemble import RandomForestClassifier

print("\nMelatih RandomForestClassifier...")
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=20,
    min_samples_split=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = sum(y_pred == y_test) / len(y_test)
print(f"Akurasi test: {acc:.4f} ({acc*100:.1f}%)")

# ============================================================
# 5. Simpan model pkl
# ============================================================
import pickle
with open('model/water_potability_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("Model pkl disimpan: model/water_potability_model.pkl")

# ============================================================
# 6. Export ke ONNX dengan zipmap=False (output tensor biasa)
# ============================================================
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

print("\nMengonversi ke ONNX...")
initial_type = [('float_input', FloatTensorType([None, 9]))]
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=17,
    options={type(model): {'zipmap': False}}
)

onnx_bytes = onnx_model.SerializeToString()
with open('model/water_potability_model.onnx', 'wb') as f:
    f.write(onnx_bytes)
with open('public/model/water_potability_model.onnx', 'wb') as f:
    f.write(onnx_bytes)
print("ONNX disimpan: model/ dan public/model/")

# ============================================================
# 7. Verifikasi ONNX
# ============================================================
import onnxruntime as ort

sess = ort.InferenceSession('public/model/water_potability_model.onnx')
print("\nOutput names:", [o.name for o in sess.get_outputs()])
print("Output types:", [o.type for o in sess.get_outputs()])

test_cases = [
    ('Normal pH=7, Hardness=150,...', [7.0, 150, 350, 2.0, 150, 300, 5.0, 50, 3.0]),
    ('Bahaya pH=2, semua ekstrem', [2.0, 500, 5000, 20.0, 1000, 1000, 30.0, 200, 20.0]),
]
print()
for lbl, f in test_cases:
    Xp = np.array([f], dtype=np.float32)
    pkl_pred = model.predict(Xp)[0]
    onnx_pred = sess.run(['label'], {'float_input': Xp})[0][0]
    match = "SAMA" if pkl_pred == onnx_pred else "BEDA"
    status = "AMAN" if onnx_pred == 1 else "TIDAK AMAN"
    print(f"{lbl}: pkl={pkl_pred} | onnx={onnx_pred} ({status}) | {match}")

print("\nSelesai! Model siap digunakan.")
