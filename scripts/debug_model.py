import onnxruntime as ort
import numpy as np, pickle, warnings
warnings.filterwarnings('ignore')

sess = ort.InferenceSession('public/model/water_potability_model.onnx')
with open('model/water_potability_model.pkl','rb') as f:
    model = pickle.load(f)

# Range yang sesuai dengan dataset sesungguhnya
tests = [
    [7.0, 196.0, 22000.0, 7.0, 333.0, 426.0, 14.0, 66.0, 3.9],
    [5.0, 100.0, 10000.0, 3.0, 200.0, 300.0, 8.0, 30.0, 2.0],
    [9.0, 300.0, 40000.0, 12.0, 500.0, 600.0, 20.0, 100.0, 6.0],
]

print("Debugging pkl vs ONNX:")
for i, t in enumerate(tests):
    X = np.array([t], dtype=np.float32)
    pkl_pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    outs = sess.run(None, {'float_input': X})
    onnx_label = outs[0][0]
    onnx_prob = outs[1][0] if len(outs) > 1 else None
    print(f"Test {i+1}: pkl={pkl_pred} proba=[{proba[0]:.2f},{proba[1]:.2f}] onnx_label={onnx_label} onnx_prob={onnx_prob}")

# Cek apakah model rf trees berfungsi normal
print("\nFeature importances:")
for i, imp in enumerate(model.feature_importances_):
    print(f"  Feature {i}: {imp:.4f}")

print("\nOutput tensor shapes:")
outs_sample = sess.run(None, {'float_input': np.array([tests[0]], dtype=np.float32)})
for i, o in enumerate(outs_sample):
    print(f"  Output {i}: shape={np.array(o).shape} dtype={np.array(o).dtype} value={o}")
