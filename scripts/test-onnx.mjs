import { InferenceSession, Tensor } from 'onnxruntime-web';

const modelUrl = 'http://127.0.0.1:5173/model/water_potability_model.onnx';

const session = await InferenceSession.create(modelUrl);

const features = [6.8, 150, 350, 1.5, 150, 300, 2.5, 50, 0.5];
const inputTensor = new Tensor('float32', Float32Array.from(features), [1, 9]);

const outputMap = await session.run({ float_input: inputTensor });
console.log('output keys', Object.keys(outputMap));

for (const [name, tensor] of Object.entries(outputMap)) {
  console.log('--- output:', name);
  console.log('dims:', tensor.dims);
  console.log('type:', tensor.type);
  console.log('data constructor:', tensor.data?.constructor?.name);
  const dataArr = Array.from(tensor.data);
  console.log('data:', dataArr);
}

