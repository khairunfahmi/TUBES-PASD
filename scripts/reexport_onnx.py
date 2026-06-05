import pickle, warnings
import numpy as np
warnings.filterwarnings('ignore')

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort

print("Memuat model pkl...")
with open('model/water_potability_model.pkl', 'rb') as f:
    model = pickle.load(f)

print(f"Model: {type(model).__name__}")
print(f"n_features: {model.n_features_in_}")
print(f"classes: {model.classes_}")

# Export ke ONNX
print("\nMengonversi ke ONNX...")
initial_type = [('float_input', FloatTensorType([None, 9]))]
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=17,
    options={type(model): {'zipmap': False}}  # output sebagai tensor biasa, bukan Map
)

# Simpan file baru
output_path = 'model/water_potability_model.onnx'
with open(output_path, 'wb') as f:
    f.write(onnx_model.SerializeToString())
print(f"ONNX tersimpan: {output_path}")

# Verifikasi hasil
print("\nVerifikasi model ONNX baru...")
sess = ort.InferenceSession(output_path)
print("Output names:", [o.name for o in sess.get_outputs()])
print("Output types:", [o.type for o in sess.get_outputs()])

test_cases = [
    ('Nilai normal/aman',    [7.0, 150, 350, 2.0, 150, 300, 5.0, 50, 3.0]),
    ('Nilai bahaya pH',      [2.0, 500, 5000, 20.0, 1000, 1000, 30.0, 200, 20.0]),
    ('Nilai nol semua',      [0.0]*9),
    ('Nilai 100 semua',      [100.0]*9),
]

print("\n=== PKL vs ONNX BARU ===")
for label, features in test_cases:
    X = np.array([features], dtype=np.float32)
    pkl_pred = model.predict(X)[0]
    # output_label sekarang adalah tensor biasa karena zipmap=False
    onnx_out = sess.run(None, {'float_input': X})
    onnx_pred = onnx_out[0][0]
    match = "SAMA ✓" if pkl_pred == onnx_pred else "BEDA ✗"
    print(f"{label}: pkl={pkl_pred} | onnx={onnx_pred} | {match}")

print("\nSelesai! Salin model ke public/model/ ...")
import shutil
shutil.copy(output_path, 'public/model/water_potability_model.onnx')
print("Berhasil disalin ke public/model/water_potability_model.onnx")
