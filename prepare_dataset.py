#!/usr/bin/env python3
"""
AMLAC Robot - Dataset Preparation Script
Organizes images into train/val/test folders for training

Your dataset structure should be:
- Algae/           (images with algae)
- No_Algae/        (images without algae - you need to create this!)

This script will:
1. Filter only JPG/PNG files (ignores screenshots and HTML files)
2. Split into train (70%), val (15%), test (15%)
3. Create proper folder structure
"""

import os
import shutil
import random
from pathlib import Path

# Configuration
SOURCE_ALGAE_DIR = 'Algae'           # Your algae images folder
SOURCE_NO_ALGAE_DIR = 'No_Algae'     # Your no-algae images folder (create this!)
OUTPUT_DIR = 'dataset'

# Split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Valid image extensions (prioritize original photos over screenshots)
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

def get_image_files(folder):
    """Get all valid image files from folder"""
    if not os.path.exists(folder):
        print(f"⚠ Folder not found: {folder}")
        return []
    
    files = []
    for f in os.listdir(folder):
        ext = Path(f).suffix.lower()
        if ext in VALID_EXTENSIONS:
            # Prioritize original photos (IMG_*.JPG) over screenshots
            full_path = os.path.join(folder, f)
            files.append((f, full_path))
    
    return files

def analyze_dataset(folder):
    """Analyze and categorize images in the folder"""
    if not os.path.exists(folder):
        return {'original': [], 'screenshot': [], 'other': []}
    
    original = []      # IMG_*.JPG - best quality
    screenshot = []    # Screenshot_*.jpeg - lower quality
    other = []         # Other images
    
    for f in os.listdir(folder):
        ext = Path(f).suffix.lower()
        if ext not in VALID_EXTENSIONS:
            continue
            
        full_path = os.path.join(folder, f)
        
        if f.startswith('IMG_'):
            original.append((f, full_path))
        elif f.startswith('Screenshot_'):
            screenshot.append((f, full_path))
        elif ext in VALID_EXTENSIONS:
            other.append((f, full_path))
    
    return {'original': original, 'screenshot': screenshot, 'other': other}

def split_files(files, train_ratio, val_ratio, test_ratio):
    """Split files into train/val/test sets"""
    random.shuffle(files)
    
    total = len(files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    
    return {
        'train': files[:train_end],
        'val': files[train_end:val_end],
        'test': files[val_end:]
    }

def copy_files(files, dest_folder):
    """Copy files to destination folder"""
    os.makedirs(dest_folder, exist_ok=True)
    
    for filename, src_path in files:
        dst_path = os.path.join(dest_folder, filename)
        shutil.copy2(src_path, dst_path)

def main():
    print("="*60)
    print("AMLAC Robot - Dataset Preparation")
    print("="*60)
    
    # Analyze algae dataset
    print(f"\nAnalyzing '{SOURCE_ALGAE_DIR}' folder...")
    algae_analysis = analyze_dataset(SOURCE_ALGAE_DIR)
    
    print(f"\n📊 Dataset Analysis:")
    print(f"   Original photos (IMG_*.JPG): {len(algae_analysis['original'])} ← BEST QUALITY")
    print(f"   Screenshots: {len(algae_analysis['screenshot'])} ← Lower quality")
    print(f"   Other images: {len(algae_analysis['other'])}")
    
    total_algae = len(algae_analysis['original']) + len(algae_analysis['screenshot']) + len(algae_analysis['other'])
    print(f"   Total algae images: {total_algae}")
    
    # Check for no_algae folder
    print(f"\nChecking '{SOURCE_NO_ALGAE_DIR}' folder...")
    if not os.path.exists(SOURCE_NO_ALGAE_DIR):
        print(f"\n❌ ERROR: '{SOURCE_NO_ALGAE_DIR}' folder not found!")
        print("\n" + "="*60)
        print("ACTION REQUIRED:")
        print("="*60)
        print(f"\nYou need to create a '{SOURCE_NO_ALGAE_DIR}' folder with images of:")
        print("  - Clean water (no algae)")
        print("  - Water with debris but no algae")
        print("  - Empty water surfaces")
        print("\nRecommended: At least 50% of your algae count")
        print(f"  → You have {total_algae} algae images")
        print(f"  → Collect at least {total_algae // 2} no-algae images")
        print("\nThen run this script again!")
        return
    
    no_algae_analysis = analyze_dataset(SOURCE_NO_ALGAE_DIR)
    total_no_algae = len(no_algae_analysis['original']) + len(no_algae_analysis['screenshot']) + len(no_algae_analysis['other'])
    print(f"   Total no-algae images: {total_no_algae}")
    
    if total_no_algae == 0:
        print(f"\n❌ ERROR: No images found in '{SOURCE_NO_ALGAE_DIR}'!")
        print("Add images of clean water (no algae) to this folder.")
        return
    
    # Decide which images to use
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    
    # Use original photos if available, otherwise include screenshots
    use_originals_only = len(algae_analysis['original']) >= 30
    
    if use_originals_only:
        print(f"\n✅ Using ONLY original photos (IMG_*.JPG) for best quality")
        algae_files = algae_analysis['original'] + algae_analysis['other']
    else:
        print(f"\n⚠ Including screenshots to have enough training data")
        algae_files = algae_analysis['original'] + algae_analysis['screenshot'] + algae_analysis['other']
    
    # Combine no_algae files
    no_algae_files = no_algae_analysis['original'] + no_algae_analysis['screenshot'] + no_algae_analysis['other']
    
    print(f"\nFinal dataset:")
    print(f"   Algae images: {len(algae_files)}")
    print(f"   No-algae images: {len(no_algae_files)}")
    
    # Split datasets
    algae_splits = split_files(algae_files, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
    no_algae_splits = split_files(no_algae_files, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
    
    print(f"\nSplit breakdown:")
    print(f"   Train: {len(algae_splits['train'])} algae + {len(no_algae_splits['train'])} no-algae")
    print(f"   Val:   {len(algae_splits['val'])} algae + {len(no_algae_splits['val'])} no-algae")
    print(f"   Test:  {len(algae_splits['test'])} algae + {len(no_algae_splits['test'])} no-algae")
    
    # Create output directory structure
    print(f"\nCreating dataset in '{OUTPUT_DIR}/'...")
    
    for split in ['train', 'val', 'test']:
        # Copy algae images
        algae_dest = os.path.join(OUTPUT_DIR, split, 'algae')
        copy_files(algae_splits[split], algae_dest)
        
        # Copy no_algae images
        no_algae_dest = os.path.join(OUTPUT_DIR, split, 'no_algae')
        copy_files(no_algae_splits[split], no_algae_dest)
    
    print("\n" + "="*60)
    print("✅ Dataset prepared successfully!")
    print("="*60)
    print(f"\nFolder structure:")
    print(f"   {OUTPUT_DIR}/")
    print(f"   ├── train/")
    print(f"   │   ├── algae/     ({len(algae_splits['train'])} images)")
    print(f"   │   └── no_algae/  ({len(no_algae_splits['train'])} images)")
    print(f"   ├── val/")
    print(f"   │   ├── algae/     ({len(algae_splits['val'])} images)")
    print(f"   │   └── no_algae/  ({len(no_algae_splits['val'])} images)")
    print(f"   └── test/")
    print(f"       ├── algae/     ({len(algae_splits['test'])} images)")
    print(f"       └── no_algae/  ({len(no_algae_splits['test'])} images)")
    print(f"\nNext step: Run 'python train_model.py' to train the model!")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()

