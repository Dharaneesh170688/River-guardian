import onnx
m = onnx.load('app/src/main/assets/model_qnn/hrposenet_int8.onnx')
print('Inputs:')
for i in m.graph.input:
    shape = [d.dim_value if d.HasField('dim_value') else d.dim_param for d in i.type.tensor_type.shape.dim]
    print(f'Name: {i.name}, Type: {i.type.tensor_type.elem_type}, Shape: {shape}')
