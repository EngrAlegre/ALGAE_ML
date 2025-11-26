#!/usr/bin/env python3
"""
Test script for Raspberry Pi Camera
Captures and saves test images to verify camera functionality
"""

import time
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image
import numpy as np

def test_camera():
    """Test camera capture and save images"""
    print("=== AMLAC Camera Test ===\n")
    
    try:
        # Initialize camera
        print("Initializing camera...")
        camera = Picamera2()
        
        # Configure camera
        camera_config = camera.create_still_configuration(
            main={"size": (640, 480)}
        )
        camera.configure(camera_config)
        
        # Start camera
        camera.start()
        print("✓ Camera started")
        
        # Allow camera to warm up
        print("Warming up camera (2 seconds)...")
        time.sleep(2)
        
        # Capture multiple test images
        print("\nCapturing test images...\n")
        
        for i in range(5):
            print(f"Capturing image {i+1}/5...")
            
            # Capture image
            image_array = camera.capture_array()
            
            # Convert to PIL Image
            image = Image.fromarray(image_array.astype('uint8'), 'RGB')
            
            # Save image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'/home/pi/amlac_robot/test_image_{timestamp}_{i+1}.jpg'
            image.save(filename)
            
            print(f"  ✓ Saved: {filename}")
            print(f"  Image size: {image.size}")
            print(f"  Array shape: {image_array.shape}")
            print()
            
            time.sleep(1)
        
        # Stop camera
        camera.stop()
        print("✓ Camera stopped")
        
        print("\n=== Camera Test Complete ===")
        print("Check the saved images to verify camera quality")
        
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_camera()

