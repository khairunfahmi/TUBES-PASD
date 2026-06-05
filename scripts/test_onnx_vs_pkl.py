import onnxruntime as ort
import numpy as np
import pickle, warnings
warnings.filterwarnings('ignore')

print("=" * 65)
print("TEST ONNX MODEL")
print("=" * 65)

sess = ort.InferenceSession('model/water_potability_model.onnx')
print("Input names :", [i.name for i in sess.get_inputs()])
print("Output names:", [o.name for o in sess.get_outputs()])
print("Output types:", [o.type for o in sess.get_outputs()])
print()

test_cases = [
    ('Nilai normal/aman',    [7.0, 150, 350, 2.0, 150, 300, 5.0, 50, 3.0]),
    ('Nilai bahaya pH',      [2.0, 500, 5000, 20.0, 1000, 1000, 30.0, 200, 20.0]),
    ('Nilai nol semua',      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    ('Nilai 100 semua',      [100.0]*9),
]

for label, features in test_cases:
    X = np.array([features], dtype=np.float32)
    out = sess.run(['output_label'], {'float_input': X})
    pred = out[0][0]
    status = "AMAN" if pred == 1 else "TIDAK AMAN"
    print(f"{label}")
    print(f"  -> ONNX Prediksi: {pred} ({status})")

print()
print("=" * 65)
print("PERBANDINGAN PKL vs ONNX")
print("=" * 65)

with open('model/water_potability_model.pkl', 'rb') as f:
    model = pickle.load(f)

for label, features in test_cases:
    X = np.array([features], dtype=np.float32)
    pkl_pred = model.predict(X)[0]
    onnx_pred = sess.run(['output_label'], {'float_input': X})[0][0]
    match = "SAMA" if pkl_pred == onnx_pred else "BEDA!"
    print(f"{label}: pkl={pkl_pred} | onnx={onnx_pred} | {match}")
