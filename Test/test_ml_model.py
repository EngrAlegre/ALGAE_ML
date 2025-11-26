#!/usr/bin/env python3
"""
Test script for ML model inference
Tests TensorFlow Lite model with sample images
"""

import sys
import numpy as np
from PIL import Image
import config
from ml_inference import MLInference

def test_ml_model():
    """Test ML model loading and inference"""
    print("=== AMLAC ML Model Test ===\n")
    
    try:
        # Initialize ML model
        print("Loading ML model...")
        ml_model = MLInference()
        
        if not ml_model.model_loaded:
            print("⚠ Failed to load model")
            print(f"Expected model path: {config.MODEL_PATH}")
            print("\nPlease ensure:")
            print("1. Model file exists at the specified path")
            print("2. Model is in TFLite format (.tflite)")
            print("3. Model was exported from Teachable Machine")
            return
        
        print("✓ Model loaded successfully\n")
        
        # Benchmark inference speed
        print("--- Benchmarking Inference Speed ---")
        avg_time = ml_model.benchmark(num_runs=10)
        
        if avg_time < 500:
            print(f"✓ Inference speed is good: {avg_time:.2f} ms (< 500ms target)")
        else:
            print(f"⚠ Inference speed is slow: {avg_time:.2f} ms (> 500ms target)")
        
        print()
        
        # Test with random images
        print("--- Testing with Random Images ---")
        
        for i in range(5):
            print(f"\nTest {i+1}/5:")
            
            # Create random test image
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Run inference
            is_algae, confidence = ml_model.detect(test_image)
            
            print(f"  Result: {'ALGAE DETECTED' if is_algae else 'No algae'}")
            print(f"  Confidence: {confidence:.2%}")
            
            # Get detailed predictions
            predictions = ml_model.get_detailed_predictions(test_image)
            print(f"  Detailed predictions:")
            for class_name, score in predictions.items():
                print(f"    {class_name}: {score:.2%}")
        
        print("\n--- Testing with Sample Images (if available) ---")
        
        # Try to load and test actual images if they exist
        import os
        sample_dir = '/home/pi/amlac_robot/test_images/'
        
        if os.path.exists(sample_dir):
            image_files = [f for f in os.listdir(sample_dir) if f.endswith(('.jpg', '.png'))]
            
            if image_files:
                print(f"Found {len(image_files)} sample images\n")
                
                for img_file in image_files[:5]:  # Test first 5 images
                    img_path = os.path.join(sample_dir, img_file)
                    print(f"Testing: {img_file}")
                    
                    # Load image
                    image = Image.open(img_path)
                    image_array = np.array(image)
                    
                    # Run inference
                    is_algae, confidence = ml_model.detect(image_array)
                    
                    print(f"  Result: {'ALGAE DETECTED' if is_algae else 'No algae'}")
                    print(f"  Confidence: {confidence:.2%}\n")
            else:
                print("No sample images found in test_images directory")
        else:
            print(f"Sample directory not found: {sample_dir}")
            print("Create this directory and add test images for better testing")
        
        print("\n=== ML Model Test Complete ===")
        
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ml_model()

