import pandas as pd
import pickle
import numpy as np
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('water_potability.csv')
feature_cols = ['ph','Hardness','Solids','Chloramines','Sulfate',
                'Conductivity','Organic_carbon','Trihalomethanes','Turbidity']

# Isi NaN dengan mean
for col in feature_cols:
    df[col].fillna(df[col].mean(), inplace=True)

with open('model/water_potability_model.pkl','rb') as f:
    model = pickle.load(f)

print("=== STATISTIK DATASET SESUNGGUHNYA ===")
print(df[feature_cols].describe().round(2).to_string())

# Cari 3 sampel AMAN (class=1) yang diprediksi benar
df1 = df[df['Potability']==1].copy()
X1 = df1[feature_cols].values.astype(np.float32)
preds = model.predict(X1)
probas = model.predict_proba(X1)

correct_idx = np.where(preds == 1)[0]
print(f"\n=== SAMPEL AMAN DARI DATASET (prediksi benar: {len(correct_idx)}/{len(df1)}) ===")
for i in correct_idx[:3]:
    print(f"\nSampel AMAN #{i} (prob_aman={probas[i][1]:.2f}):")
    for col in feature_cols:
        print(f"  {col}: {df1.iloc[i][col]:.4f}")

print("\n=== RANGE UI vs DATASET ===")
ui_max = {'ph':8.5,'Hardness':200,'Solids':500,'Chloramines':4,'Sulfate':250,
          'Conductivity':400,'Organic_carbon':10,'Trihalomethanes':80,'Turbidity':5}
for col in feature_cols:
    ds_mean = df[col].mean()
    ds_max = df[col].max()
    cocok = "OK" if ui_max[col] >= ds_mean * 0.5 else "SALAH!"
    print(f"  {col:<20}: UI_max={ui_max[col]:<8} DS_mean={ds_mean:<10.1f} DS_max={ds_max:<10.1f} {cocok}")
