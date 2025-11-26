#!/usr/bin/env python3
"""
AMLAC Robot - Model Testing Script for Windows
Tests the trained TFLite model with images on Windows

Usage:
    python test_model_windows.py [image_path]
    
If no image path provided, will test with images from Algae folder
"""

import os
import sys
import numpy as np
from PIL import Image
import tensorflow as tf

# Model path
MODEL_PATH = 'models/model.tflite'
CONFIDENCE_THRESHOLD = 0.5  # Lower threshold for one-class model (synthetic negatives)

def load_tflite_model(model_path):
    """Load TensorFlow Lite model"""
    if not os.path.exists(model_path):
        print(f"❌ Error: Model not found at {model_path}")
        print("   Make sure you've trained the model first!")
        return None
    
    print(f"Loading model from {model_path}...")
    
    try:
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print(f"✓ Model loaded successfully")
        print(f"  Input shape: {input_details[0]['shape']}")
        print(f"  Output shape: {output_details[0]['shape']}")
        
        return interpreter, input_details, output_details
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None, None

def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess image for model input"""
    try:
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to model input size
        img = img.resize(target_size, Image.LANCZOS)
        
        # Convert to numpy array and normalize
        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array, img
    except Exception as e:
        print(f"❌ Error loading image {image_path}: {e}")
        return None, None

def predict_image(interpreter, input_details, output_details, image_array):
    """Run inference on image"""
    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], image_array)
    
    # Run inference
    interpreter.invoke()
    
    # Get output
    output_data = interpreter.get_tensor(output_details[0]['index'])
    
    # Get prediction (binary classification: 0=algae, 1=no_algae)
    prediction = float(output_data[0][0])
    
    # Model output interpretation:
    # - Output is sigmoid: 0.0 to 1.0
    # - Class 0 (algae): output close to 0.0
    # - Class 1 (no_algae): output close to 1.0
    # So: algae_probability = 1.0 - prediction
    algae_probability = 1.0 - prediction
    
    return algae_probability, prediction

def test_single_image(image_path, interpreter, input_details, output_details):
    """Test a single image"""
    print(f"\n{'='*60}")
    print(f"Testing: {os.path.basename(image_path)}")
    print(f"{'='*60}")
    
    # Preprocess
    img_array, original_img = preprocess_image(image_path)
    if img_array is None:
        return
    
    # Predict
    algae_prob, raw_pred = predict_image(interpreter, input_details, output_details, img_array)
    
    # Determine result
    is_algae = algae_prob > CONFIDENCE_THRESHOLD
    
    # Display results
    print(f"Raw Model Output: {raw_pred:.4f} (0=algae, 1=no_algae)")
    print(f"Algae Probability: {algae_prob:.2%}")
    print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD:.2%}")
    print(f"\nResult: {'🌿 ALGAE DETECTED!' if is_algae else '💧 No Algae'}")
    print(f"Confidence: {algae_prob:.2%}")
    
    if is_algae:
        print("✓ Would trigger collection mechanism")
    else:
        print("○ Would continue scanning")
    
    # Note about one-class model
    if 0.4 < algae_prob < 0.6:
        print("\n⚠ Note: Low confidence - model trained with synthetic negatives")
        print("   Consider: Lower threshold or retrain with real clean water images")
    
    return is_algae, algae_prob

def test_multiple_images(folder_path, interpreter, input_details, output_details, num_images=10):
    """Test multiple images from a folder"""
    print(f"\n{'='*60}")
    print(f"Testing {num_images} images from: {folder_path}")
    print(f"{'='*60}")
    
    # Get image files
    image_files = []
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
            image_files.append(os.path.join(folder_path, f))
    
    if len(image_files) == 0:
        print(f"❌ No images found in {folder_path}")
        return
    
    # Limit to num_images
    image_files = image_files[:num_images]
    
    print(f"Found {len(image_files)} images to test\n")
    
    results = []
    for img_path in image_files:
        is_algae, confidence = test_single_image(img_path, interpreter, input_details, output_details)
        results.append((is_algae, confidence))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    total = len(results)
    detected = sum(1 for r in results if r[0])
    avg_confidence = sum(r[1] for r in results) / total
    
    print(f"Total images tested: {total}")
    print(f"Algae detected: {detected} ({detected/total*100:.1f}%)")
    print(f"Average confidence: {avg_confidence:.2%}")
    print(f"Min confidence: {min(r[1] for r in results):.2%}")
    print(f"Max confidence: {max(r[1] for r in results):.2%}")

def main():
    """Main function"""
    print("="*60)
    print("AMLAC Robot - Model Testing (Windows)")
    print("="*60)
    
    # Load model
    result = load_tflite_model(MODEL_PATH)
    if result[0] is None:
        return
    
    interpreter, input_details, output_details = result
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Test single image
        image_path = sys.argv[1]
        if os.path.exists(image_path):
            test_single_image(image_path, interpreter, input_details, output_details)
        else:
            print(f"❌ Image not found: {image_path}")
    else:
        # Test multiple images from Algae folder
        algae_folder = 'Algae'
        if os.path.exists(algae_folder):
            # Test 10 random images
            test_multiple_images(algae_folder, interpreter, input_details, output_details, num_images=10)
        else:
            print(f"❌ Algae folder not found: {algae_folder}")
            print("\nUsage:")
            print("  python test_model_windows.py [image_path]")
            print("\nExample:")
            print("  python test_model_windows.py Algae/IMG_4003.JPG")

if __name__ == "__main__":
    main()

