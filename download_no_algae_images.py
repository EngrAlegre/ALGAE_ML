#!/usr/bin/env python3
"""
AMLAC Robot - Download Clean Water (No Algae) Images
Downloads sample images of clean water for training the negative class

NOTE: For best results, you should also take your own photos of clean water
in your actual environment (same camera, lighting, conditions)
"""

import os
import urllib.request
import ssl

# Create No_Algae folder
OUTPUT_DIR = "No_Algae"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sample clean water image URLs (royalty-free/public domain)
# These are placeholder URLs - you should replace with actual clean water images
SAMPLE_URLS = [
    # Add URLs to clean water images here
    # For now, we'll create placeholder instructions
]

def create_instructions():
    """Create instructions for collecting No_Algae images"""
    
    instructions = """
================================================================================
IMPORTANT: You Need Clean Water Images!
================================================================================

Your model needs to learn TWO things:
1. What algae looks like (you have 3,500+ images ✓)
2. What clean water looks like (you need these!)

HOW TO GET CLEAN WATER IMAGES:
==============================

Option 1: Take Your Own Photos (BEST)
-------------------------------------
- Use the same camera you'll use on the robot
- Take photos of clean water surfaces
- Include various conditions:
  * Different lighting (sunny, cloudy, morning, afternoon)
  * Different water clarity
  * Water with ripples/waves
  * Water with reflections
  * Water with debris (leaves, sticks) but NO algae

Option 2: Download from Internet
--------------------------------
Search for these on stock photo sites (Shutterstock, Pexels, Unsplash):
- "clean water surface"
- "clear pond water"
- "lake water surface"
- "river water texture"
- "water reflection"

Option 3: Use Your Existing Images
----------------------------------
If you have ANY images of clean water in your collection, 
move them to the No_Algae folder.

RECOMMENDED AMOUNT:
===================
- Minimum: 500 images
- Better: 1000+ images
- Best: Similar count to your algae images (3,500)

FOLDER STRUCTURE:
=================
D:\\Client\\ML-shawn\\
- Algae\\          (your algae images - DONE)
- No_Algae\\       (put clean water images HERE)

AFTER ADDING IMAGES:
====================
1. Run: python prepare_dataset.py
2. Run: python train_model.py
3. Get your trained model in: models/model.tflite

================================================================================
"""
    
    # Save instructions
    instructions_path = os.path.join(OUTPUT_DIR, "README_ADD_IMAGES_HERE.txt")
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(instructions)
    print(f"\nInstructions saved to: {instructions_path}")
    print(f"\nNo_Algae folder created at: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    create_instructions()

