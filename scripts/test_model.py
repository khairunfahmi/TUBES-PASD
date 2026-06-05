import pickle, warnings
warnings.filterwarnings('ignore')

with open('model/water_potability_model.pkl', 'rb') as f:
    model = pickle.load(f)

import numpy as np

test_cases = [
    ('Nilai normal/aman',    [7.0, 150, 350, 2.0, 150, 300, 5.0, 50, 3.0]),
    ('Nilai bahaya pH',      [2.0, 500, 5000, 20.0, 1000, 1000, 30.0, 200, 20.0]),
    ('Nilai sangat ekstrem', [0.1, 999, 9999, 50.0, 2000, 2000, 50.0, 500, 50.0]),
    ('Nilai nol semua',      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    ('Nilai 100 semua',      [100, 100, 100, 100, 100, 100, 100, 100, 100]),
]

print(f'Classes: {model.classes_}  (0=tidak aman, 1=aman)')
print('-' * 65)
for label, features in test_cases:
    X = np.array([features])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    status = "AMAN" if pred == 1 else "TIDAK AMAN"
    print(f'{label}')
    print(f'  -> Prediksi: {pred} ({status})  Prob[0]={proba[0]:.2f}  Prob[1]={proba[1]:.2f}')
print('-' * 65)
