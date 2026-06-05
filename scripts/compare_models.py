"""
Retrain dengan HistGradientBoosting (handle NaN natively) dan model lain.
"""
import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import balanced_accuracy_score
from sklearn.impute import SimpleImputer

df = pd.read_csv('water_potability.csv')
feature_cols = ['ph','Hardness','Solids','Chloramines','Sulfate',
                'Conductivity','Organic_carbon','Trihalomethanes','Turbidity']

# Imputasi mean dulu
for c in feature_cols:
    df[c].fillna(df[c].mean(), inplace=True)

X = df[feature_cols].values.astype(np.float64)  # float64 agar kompatibel semua model
y = df['Potability'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")

# Nilai test
mean_vals  = np.array([[7.08, 196.0, 22014.0, 7.12, 333.0, 426.0, 14.28, 66.4, 3.97]])
mid_vals   = np.array([[7.5,  200.0, 20000.0, 7.5,  340.0, 430.0, 14.0,  65.0, 4.0]])
aman_vals  = np.array([[9.02, 128.10, 19859.68, 8.02, 300.15, 451.14, 14.77, 73.78, 3.99]])
bahaya_vals = np.array([[4.37, 188.65, 29542.34, 8.12, 301.02, 456.31, 16.35, 46.70, 4.65]])

candidates = {
    'RandomForest balanced': RandomForestClassifier(
        n_estimators=500, max_depth=None, min_samples_leaf=2,
        class_weight='balanced', random_state=42, n_jobs=-1
    ),
    'ExtraTrees balanced': ExtraTreesClassifier(
        n_estimators=500, max_depth=None, min_samples_leaf=2,
        class_weight='balanced', random_state=42, n_jobs=-1
    ),
    'HistGradientBoosting': HistGradientBoostingClassifier(
        max_iter=500, max_depth=8, learning_rate=0.05,
        class_weight='balanced', random_state=42
    ),
    'LogisticRegression': Pipeline([
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression(class_weight='balanced', C=1.0, max_iter=1000, random_state=42))
    ]),
}

print("\n=== EVALUASI MODEL ===")
best_model = None
best_score = 0
best_name  = ''

for name, clf in candidates.items():
    clf.fit(X_train, y_train)
    y_pred   = clf.predict(X_test)
    bal_acc  = balanced_accuracy_score(y_test, y_pred)
    acc      = (y_pred == y_test).mean()
    n_aman   = sum(y_pred == 1)

    p_mean   = clf.predict_proba(mean_vals)[0]
    p_mid    = clf.predict_proba(mid_vals)[0]
    p_aman   = clf.predict_proba(aman_vals)[0]
    p_bahaya = clf.predict_proba(bahaya_vals)[0]

    pred_mean = 'AMAN' if clf.predict(mean_vals)[0]==1 else 'TIDAK AMAN'
    pred_mid  = 'AMAN' if clf.predict(mid_vals)[0]==1  else 'TIDAK AMAN'

    print(f"\n{name}:")
    print(f"  Acc={acc:.3f}  BalAcc={bal_acc:.3f}  Prediksi AMAN di test={n_aman}/{len(y_pred)}")
    print(f"  Nilai mean dataset  -> {pred_mean} (prob_aman={p_mean[1]:.2f})")
    print(f"  Nilai mid-range     -> {pred_mid}  (prob_aman={p_mid[1]:.2f})")
    print(f"  Preset AMAN         -> prob_aman={p_aman[1]:.2f}")
    print(f"  Preset TIDAK AMAN   -> prob_aman={p_bahaya[1]:.2f}")

    if bal_acc > best_score:
        best_score = bal_acc
        best_model = clf
        best_name  = name

print(f"\n>>> MODEL TERPILIH: {best_name} (BalAcc={best_score:.3f})")

with open('model/water_potability_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
print("Model disimpan ke model/water_potability_model.pkl")
