import onnx
import onnxruntime
from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantType, QuantFormat
import numpy as np
import os
from PIL import Image

class RandomDataReader(CalibrationDataReader):
    def __init__(self, input_name, shape, dtype=np.int32):
        self.input_name = input_name
        self.shape = shape
        self.dtype = dtype
        self.enum_data_dicts = iter([{self.input_name: np.random.randint(0, 256, size=self.shape).astype(self.dtype)} for _ in range(50)])

    def get_next(self):
        return next(self.enum_data_dicts, None)

class ImageDataReader(CalibrationDataReader):
    def __init__(self, image_dir, input_name, shape):
        self.input_name = input_name
        self.shape = shape
        self.data_dicts = []
        
        # Load and preprocess images
        image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        # Use at most 50 images for calibration
        image_files = image_files[:50]
        
        batch_size, height, width, channels = shape
        # In our Kotlin code, the input shape might be [1, H, W, C] for NHWC or [1, C, H, W] for NCHW
        is_nchw = (shape[1] == 3 or shape[1] == 1)
        h = shape[2] if is_nchw else shape[1]
        w = shape[3] if is_nchw else shape[2]

        for img_path in image_files:
            try:
                img = Image.open(img_path).convert('RGB')
                img = img.resize((w, h))
                img_data = np.array(img).astype(np.int32)
                
                # NCHW vs NHWC based on expected shape
                if is_nchw:
                    img_data = np.transpose(img_data, (2, 0, 1)) # HWC to CHW
                    
                img_data = np.expand_dims(img_data, axis=0) # Add batch dim
                self.data_dicts.append({self.input_name: img_data})
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                
        self.enum_data_dicts = iter(self.data_dicts)

    def get_next(self):
        return next(self.enum_data_dicts, None)

def main():
    model_path = "app/src/main/assets/model_generic.onnx"
    output_model_path = "app/src/main/assets/model_qnn/hrposenet_int8.onnx"
    
    print(f"Loading model from {model_path}...")
    session = onnxruntime.InferenceSession(model_path)
    
    input_name = session.get_inputs()[0].name
    input_shape = session.get_inputs()[0].shape
    
    # Handle dynamic batch size for calibration shape
    if isinstance(input_shape[0], str) or input_shape[0] <= 0:
        input_shape[0] = 1
        
    print(f"Input Name: {input_name}, Input Shape: {input_shape}")
    
    # See if there's a dataset directory provided by the user
    dataset_dir = "Dataset/validation"
    if os.path.exists(dataset_dir) and len(os.listdir(dataset_dir)) > 0:
        print(f"Found calibration images in {dataset_dir}, using ImageDataReader...")
        data_reader = ImageDataReader(dataset_dir, input_name, input_shape)
    else:
        print("No calibration dataset found. Using RandomDataReader for calibration...")
        data_reader = RandomDataReader(input_name, input_shape)
        
    print(f"Starting quantization to INT8...")
    
    # Quantize static
    # Use QDQ format which is recommended for execution providers like QNN/NNAPI
    quantize_static(
        model_input=model_path,
        model_output=output_model_path,
        calibration_data_reader=data_reader,
        quant_format=QuantFormat.QDQ,
        activation_type=QuantType.QUInt8,
        weight_type=QuantType.QUInt8
    )
    
    print(f"Quantization complete! Saved to {output_model_path}")
    print(f"Original size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
    print(f"Quantized size: {os.path.getsize(output_model_path) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()
