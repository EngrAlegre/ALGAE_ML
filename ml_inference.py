"""
ML Inference Module for AMLAC Robot
Handles TensorFlow Lite model loading and inference for algae detection
"""

import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
import config

class MLInference:
    """
    Machine Learning inference engine for algae detection
    Uses TensorFlow Lite model trained on Teachable Machine
    """
    
    def __init__(self, model_path=None):
        """
        Initialize ML model
        
        Args:
            model_path (str): Path to TFLite model file
        """
        if model_path is None:
            model_path = config.MODEL_PATH
        
        print(f"Loading ML model from {model_path}...")
        
        try:
            # Load TFLite model
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Get input shape
            self.input_shape = self.input_details[0]['shape']
            self.input_height = self.input_shape[1]
            self.input_width = self.input_shape[2]
            
            print(f"✓ Model loaded successfully")
            print(f"  Input shape: {self.input_shape}")
            print(f"  Input size: {self.input_width}x{self.input_height}")
            print(f"  Output shape: {self.output_details[0]['shape']}\n")
            
            self.model_loaded = True
            
        except Exception as e:
            print(f"⚠ Error loading model: {e}")
            self.model_loaded = False
    
    def preprocess_image(self, image_array):
        """
        Preprocess image for model input
        
        Args:
            image_array (numpy.ndarray): Raw image from camera
            
        Returns:
            numpy.ndarray: Preprocessed image ready for inference
        """
        # Convert to PIL Image if needed
        if isinstance(image_array, np.ndarray):
            # Handle different image formats (RGB, RGBA, BGR)
            if len(image_array.shape) == 3:
                if image_array.shape[2] == 4:  # RGBA
                    image_array = image_array[:, :, :3]  # Remove alpha channel
                elif image_array.shape[2] == 3:  # RGB or BGR
                    pass  # Already in correct format
            
            image = Image.fromarray(image_array.astype('uint8'), 'RGB')
        else:
            image = image_array
        
        # Resize to model input size (usually 224x224 for Teachable Machine)
        image = image.resize((self.input_width, self.input_height), Image.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(image, dtype=np.float32)
        
        # Normalize pixel values to [0, 1] or [-1, 1] depending on model
        # Teachable Machine typically uses [0, 1] normalization
        image_array = image_array / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def detect(self, image_array):
        """
        Run inference on image to detect algae
        
        Args:
            image_array (numpy.ndarray): Image from camera
            
        Returns:
            tuple: (is_algae_detected: bool, confidence: float)
        """
        if not self.model_loaded:
            print("Model not loaded, cannot perform inference")
            return (False, 0.0)
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_array)
            
            # Set input tensor
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                processed_image
            )
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output tensor
            output_data = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )
            
            # Get predictions (assuming binary classification: algae vs no algae)
            # For Teachable Machine, output is typically [no_algae_prob, algae_prob]
            predictions = output_data[0]
            
            # Get algae confidence (assuming class 1 is algae)
            # Adjust index based on your model's class order
            if len(predictions) >= 2:
                algae_confidence = float(predictions[1])  # Class 1: Algae
            else:
                algae_confidence = float(predictions[0])
            
            # Determine if algae is detected based on threshold
            is_algae_detected = algae_confidence > config.CONFIDENCE_THRESHOLD
            
            return (is_algae_detected, algae_confidence)
            
        except Exception as e:
            print(f"Error during inference: {e}")
            return (False, 0.0)
    
    def get_detailed_predictions(self, image_array):
        """
        Get detailed prediction scores for all classes
        
        Args:
            image_array (numpy.ndarray): Image from camera
            
        Returns:
            dict: Dictionary with class names and confidence scores
        """
        if not self.model_loaded:
            return {}
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_array)
            
            # Set input tensor
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                processed_image
            )
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output tensor
            output_data = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )
            
            predictions = output_data[0]
            
            # Return predictions for each class
            # Adjust class names based on your Teachable Machine model
            result = {
                'no_algae': float(predictions[0]) if len(predictions) > 0 else 0.0,
                'algae': float(predictions[1]) if len(predictions) > 1 else 0.0
            }
            
            return result
            
        except Exception as e:
            print(f"Error getting detailed predictions: {e}")
            return {}
    
    def benchmark(self, num_runs=10):
        """
        Benchmark inference speed
        
        Args:
            num_runs (int): Number of inference runs to average
            
        Returns:
            float: Average inference time in milliseconds
        """
        if not self.model_loaded:
            print("Model not loaded")
            return 0.0
        
        import time
        
        # Create dummy image
        dummy_image = np.random.randint(
            0, 255,
            (self.input_height, self.input_width, 3),
            dtype=np.uint8
        )
        
        times = []
        
        print(f"Running {num_runs} inference benchmarks...")
        
        for i in range(num_runs):
            start_time = time.time()
            self.detect(dummy_image)
            end_time = time.time()
            
            inference_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(inference_time)
            print(f"  Run {i+1}: {inference_time:.2f} ms")
        
        avg_time = sum(times) / len(times)
        print(f"\nAverage inference time: {avg_time:.2f} ms")
        
        return avg_time


if __name__ == "__main__":
    """Test ML inference"""
    print("=== AMLAC ML Inference Test ===\n")
    
    try:
        # Initialize ML model
        ml_model = MLInference()
        
        if not ml_model.model_loaded:
            print("Failed to load model. Please check model path.")
            exit(1)
        
        # Benchmark inference speed
        print("\n--- Benchmarking inference speed ---")
        avg_time = ml_model.benchmark(num_runs=10)
        
        if avg_time < 500:
            print("✓ Inference speed is good (< 500ms)")
        else:
            print("⚠ Inference speed is slow (> 500ms)")
        
        # Test with sample images if available
        print("\n--- Testing with sample image ---")
        
        # Create a test image (random noise)
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        print("Running inference on test image...")
        is_algae, confidence = ml_model.detect(test_image)
        
        print(f"Result: {'ALGAE DETECTED' if is_algae else 'No algae'}")
        print(f"Confidence: {confidence:.2%}")
        
        # Get detailed predictions
        print("\n--- Detailed predictions ---")
        predictions = ml_model.get_detailed_predictions(test_image)
        for class_name, score in predictions.items():
            print(f"{class_name}: {score:.2%}")
        
        print("\n✓ ML inference test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

