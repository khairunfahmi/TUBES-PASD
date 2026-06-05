"""
Export ONNX tanpa opsi zipmap (default).
Di JS kita hanya request output_label saja, tidak menyentuh output_probability (Sequence<Map>).
"""
import numpy as np
import pickle, warnings
warnings.filterwarnings('ignore')

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort

print("Memuat model pkl yang baru...")
with open('model/water_potability_model.pkl', 'rb') as f:
    model = pickle.load(f)

print(f"Model: {type(model).__name__}, n_estimators={model.n_estimators}")

print("\nMengonversi ke ONNX (default, tanpa zipmap override)...")
initial_type = [('float_input', FloatTensorType([None, 9]))]
onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=17
    # TIDAK ada options zipmap — biarkan default
)

onnx_bytes = onnx_model.SerializeToString()
with open('model/water_potability_model.onnx', 'wb') as f:
    f.write(onnx_bytes)
with open('public/model/water_potability_model.onnx', 'wb') as f:
    f.write(onnx_bytes)
print("ONNX tersimpan.")

sess = ort.InferenceSession('public/model/water_potability_model.onnx')
print("Output names:", [o.name for o in sess.get_outputs()])
print("Output types:", [o.type for o in sess.get_outputs()])

# Test dengan range dataset yang sebenarnya
# Means: ph=7.08, Hardness=196, Solids=22014, Chloramines=7.12, Sulfate=333,
#        Conductivity=426, Organic_carbon=14.28, Trihalomethanes=66.4, Turbidity=3.97
tests = [
    ('pH rendah + parameter ekstrem', [5.0, 100.0, 10000.0, 3.0, 200.0, 300.0, 8.0, 30.0, 2.0]),
    ('pH tinggi + parameter ekstrem', [9.5, 300.0, 40000.0, 12.0, 500.0, 600.0, 20.0, 100.0, 6.0]),
    ('Nilai mean dataset',            [7.08, 196.0, 22014.0, 7.12, 333.0, 426.0, 14.28, 66.4, 3.97]),
]

label_out_name = [o.name for o in sess.get_outputs()][0]
print(f"\nLabel output name: '{label_out_name}'")
print()

for lbl, f in tests:
    X = np.array([f], dtype=np.float32)
    pkl_pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    # Hanya request label — tidak menyentuh Sequence<Map>
    onnx_pred = sess.run([label_out_name], {'float_input': X})[0][0]
    match = "SAMA" if pkl_pred == onnx_pred else "BEDA"
    status = "AMAN" if onnx_pred == 1 else "TIDAK AMAN"
    print(f"{lbl}")
    print(f"  pkl={pkl_pred} prob=[{proba[0]:.2f},{proba[1]:.2f}] | onnx={onnx_pred} ({status}) | {match}")
