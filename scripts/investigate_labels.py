"""
Test model dengan sample aktual dari dataset untuk investigasi inversi label
"""
import numpy as np, csv, pickle, warnings
warnings.filterwarnings('ignore')
import onnxruntime as ort

# Load dataset
rows = []
with open('water_potability.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

feature_cols = ['ph','Hardness','Solids','Chloramines','Sulfate',
                'Conductivity','Organic_carbon','Trihalomethanes','Turbidity']

# Hitung mean untuk imputasi
means = {}
for col in feature_cols:
    vals = [float(r[col]) for r in rows if r[col].strip() not in ('','nan','NaN')]
    means[col] = sum(vals)/len(vals)

# Load samples class 0 dan class 1 dari dataset
class0_samples = []
class1_samples = []
for row in rows:
    try:
        x = [float(row[c]) if row[c].strip() not in ('','nan','NaN') else means[c] for c in feature_cols]
        y = int(row['Potability'])
        if y == 0 and len(class0_samples) < 5:
            class0_samples.append((x, y))
        elif y == 1 and len(class1_samples) < 5:
            class1_samples.append((x, y))
    except:
        continue

# Load models
with open('model/water_potability_model.pkl','rb') as f:
    model = pickle.load(f)
sess = ort.InferenceSession('public/model/water_potability_model.onnx')
label_name = [o.name for o in sess.get_outputs()][0]

print("=== SAMPLE KELAS 0 (TIDAK AMAN di dataset) ===")
for x, y_true in class0_samples:
    X = np.array([x], dtype=np.float32)
    pkl_pred = model.predict(X)[0]
    onnx_pred = sess.run([label_name], {'float_input': X})[0][0]
    print(f"  true={y_true} pkl={pkl_pred} onnx={onnx_pred}")

print("\n=== SAMPLE KELAS 1 (AMAN di dataset) ===")
for x, y_true in class1_samples:
    X = np.array([x], dtype=np.float32)
    pkl_pred = model.predict(X)[0]
    onnx_pred = sess.run([label_name], {'float_input': X})[0][0]
    print(f"  true={y_true} pkl={pkl_pred} onnx={onnx_pred}")

print(f"\nLabel output name: '{label_name}'")
print(f"Model classes_: {model.classes_}")

# Hitung akurasi ONNX vs pkl pada 100 sample pertama
print("\n=== AKURASI PADA 100 SAMPLE ===")
X_all, y_all = [], []
for row in rows[:200]:
    try:
        x = [float(row[c]) if row[c].strip() not in ('','nan','NaN') else means[c] for c in feature_cols]
        y_all.append(int(row['Potability']))
        X_all.append(x)
    except:
        pass
X_all = np.array(X_all[:100], dtype=np.float32)
y_all = np.array(y_all[:100])

pkl_preds = model.predict(X_all)
onnx_preds = np.array([sess.run([label_name], {'float_input': X_all[i:i+1]})[0][0] for i in range(len(X_all))])

print(f"pkl accuracy: {(pkl_preds==y_all).mean():.3f}")
print(f"onnx accuracy: {(onnx_preds==y_all).mean():.3f}")
print(f"onnx inverted accuracy: {(1-onnx_preds==y_all).mean():.3f}")
print(f"pkl vs onnx same: {(pkl_preds==onnx_preds).mean():.3f}")
