#!/usr/bin/env python3
"""
AMLAC Robot - ML Model Training Script
One-Class Classification using MobileNetV3-Large

This approach trains only on algae images and uses confidence thresholding
to detect algae vs non-algae.

Usage:
1. Put algae images in: Algae/
2. Run: python train_model.py
3. Output: models/model.tflite
"""

import os
import sys
import random
import shutil
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV3Large
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Configuration
IMAGE_SIZE = 224  # MobileNetV3 input size
BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 0.0001

# Dataset paths
ALGAE_DIR = 'Algae'
DATASET_DIR = 'dataset'
TRAIN_DIR = os.path.join(DATASET_DIR, 'train')
VAL_DIR = os.path.join(DATASET_DIR, 'val')
TEST_DIR = os.path.join(DATASET_DIR, 'test')

# Output paths
MODEL_SAVE_PATH = 'models/algae_classifier.h5'
TFLITE_SAVE_PATH = 'models/model.tflite'

# Valid image extensions
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


def get_image_files(folder):
    """Get all valid image files from folder (prioritize IMG_* files)"""
    if not os.path.exists(folder):
        return []
    
    original = []  # IMG_*.jpg - best quality
    other = []     # Other images
    
    for f in os.listdir(folder):
        ext = os.path.splitext(f)[1].lower()
        if ext not in VALID_EXTENSIONS:
            continue
        
        full_path = os.path.join(folder, f)
        if f.upper().startswith('IMG_'):
            original.append(full_path)
        else:
            other.append(full_path)
    
    # Prioritize original photos, then add others
    return original + other


def prepare_one_class_dataset():
    """
    Prepare dataset for one-class classification
    Uses only algae images, creates synthetic 'no_algae' class using augmentation
    """
    print("\n" + "="*60)
    print("Preparing One-Class Dataset")
    print("="*60)
    
    # Get all algae images
    algae_files = get_image_files(ALGAE_DIR)
    
    if len(algae_files) == 0:
        print(f"! No images found in {ALGAE_DIR}/")
        return False
    
    print(f"Found {len(algae_files)} algae images")
    
    # Use original photos if we have enough, otherwise use all
    original_count = len([f for f in algae_files if 'IMG_' in f.upper()])
    if original_count >= 100:
        print(f"Using {original_count} original photos (IMG_*.jpg)")
        algae_files = [f for f in algae_files if 'IMG_' in f.upper()]
    
    # Shuffle
    random.shuffle(algae_files)
    
    # Split into train/val/test
    total = len(algae_files)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)
    
    splits = {
        'train': algae_files[:train_end],
        'val': algae_files[train_end:val_end],
        'test': algae_files[val_end:]
    }
    
    print(f"\nSplit: Train={len(splits['train'])}, Val={len(splits['val'])}, Test={len(splits['test'])}")
    
    # Create directory structure
    # For one-class, we create a binary classifier:
    # - algae: real algae images
    # - no_algae: heavily augmented/transformed images (synthetic negatives)
    
    print("\nCreating dataset folders...")
    
    for split_name, files in splits.items():
        # Create algae folder
        algae_dest = os.path.join(DATASET_DIR, split_name, 'algae')
        os.makedirs(algae_dest, exist_ok=True)
        
        # Create no_algae folder (will be filled with synthetic data)
        no_algae_dest = os.path.join(DATASET_DIR, split_name, 'no_algae')
        os.makedirs(no_algae_dest, exist_ok=True)
        
        # Copy algae images
        for src_path in files:
            filename = os.path.basename(src_path)
            dst_path = os.path.join(algae_dest, filename)
            shutil.copy2(src_path, dst_path)
        
        # Create synthetic no_algae images
        # We'll use random noise and color-shifted versions
        create_synthetic_negatives(no_algae_dest, len(files))
    
    print("\n[OK] Dataset prepared successfully!")
    return True


def create_synthetic_negatives(output_dir, count):
    """
    Create synthetic 'no algae' images
    These are random patterns that don't look like algae
    """
    from PIL import Image
    
    for i in range(count):
        # Create random water-like patterns
        img_type = i % 4
        
        if img_type == 0:
            # Blue-ish water pattern
            img = np.random.randint(100, 200, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
            img[:, :, 0] = np.clip(img[:, :, 0] - 50, 0, 255)  # Less red
            img[:, :, 2] = np.clip(img[:, :, 2] + 30, 0, 255)  # More blue
        elif img_type == 1:
            # Gray water pattern
            gray = np.random.randint(80, 180, (IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
            img = np.stack([gray, gray, gray], axis=-1)
        elif img_type == 2:
            # Brown/muddy water pattern
            img = np.random.randint(60, 150, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
            img[:, :, 0] = np.clip(img[:, :, 0] + 20, 0, 255)  # More red
            img[:, :, 1] = np.clip(img[:, :, 1] - 10, 0, 255)  # Less green
            img[:, :, 2] = np.clip(img[:, :, 2] - 30, 0, 255)  # Less blue
        else:
            # Clear water with reflections
            img = np.random.randint(120, 220, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
            img[:, :, 1] = np.clip(img[:, :, 1] - 20, 0, 255)  # Less green (no algae!)
        
        # Add some texture
        noise = np.random.randint(-20, 20, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Save image
        pil_img = Image.fromarray(img)
        pil_img.save(os.path.join(output_dir, f'synthetic_{i:04d}.jpg'), quality=90)


def create_model():
    """
    Create MobileNetV3-Large based binary classification model
    """
    print("\nCreating MobileNetV3-Large model...")
    
    # Load pre-trained MobileNetV3-Large
    base_model = MobileNetV3Large(
        input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers initially
    base_model.trainable = False
    
    # Build model
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Binary classification
    ])
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"[OK] Model created")
    print(f"    Total parameters: {model.count_params():,}")
    
    return model, base_model


def prepare_data():
    """
    Prepare data generators with augmentation
    """
    print("\nPreparing data generators...")
    
    # Strong augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        zoom_range=0.3,
        shear_range=0.2
    )
    
    # No augmentation for validation/test
    val_test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Create generators
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=True
    )
    
    val_generator = val_test_datagen.flow_from_directory(
        VAL_DIR,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    test_generator = val_test_datagen.flow_from_directory(
        TEST_DIR,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    print(f"[OK] Data generators created")
    print(f"    Training samples: {train_generator.samples}")
    print(f"    Validation samples: {val_generator.samples}")
    print(f"    Test samples: {test_generator.samples}")
    print(f"    Classes: {train_generator.class_indices}")
    
    return train_generator, val_generator, test_generator


def train_model(model, base_model, train_gen, val_gen):
    """
    Train the model with two phases
    """
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        ModelCheckpoint(
            MODEL_SAVE_PATH.replace('.h5', '.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    print("\n" + "="*60)
    print("Phase 1: Training Top Layers (base frozen)")
    print("="*60)
    
    history1 = model.fit(
        train_gen,
        epochs=10,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )
    
    print("\n" + "="*60)
    print("Phase 2: Fine-tuning All Layers")
    print("="*60)
    
    # Unfreeze base model
    base_model.trainable = True
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE / 10),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    history2 = model.fit(
        train_gen,
        epochs=EPOCHS - 10,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )
    
    # Combine histories
    combined_history = {
        'loss': history1.history['loss'] + history2.history['loss'],
        'val_loss': history1.history['val_loss'] + history2.history['val_loss'],
        'accuracy': history1.history['accuracy'] + history2.history['accuracy'],
        'val_accuracy': history1.history['val_accuracy'] + history2.history['val_accuracy']
    }
    
    return combined_history


def evaluate_model(model, test_gen):
    """
    Evaluate model on test set
    """
    print("\n" + "="*60)
    print("Evaluating on Test Set")
    print("="*60)
    
    results = model.evaluate(test_gen, verbose=1)
    
    print(f"\nTest Loss: {results[0]:.4f}")
    print(f"Test Accuracy: {results[1]:.4f} ({results[1]*100:.2f}%)")
    
    return results


def plot_training_history(history):
    """
    Plot and save training history
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot accuracy
    ax1.plot(history['accuracy'], label='Training')
    ax1.plot(history['val_accuracy'], label='Validation')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Plot loss
    ax2.plot(history['loss'], label='Training')
    ax2.plot(history['val_loss'], label='Validation')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.set_title('Model Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('models/training_history.png', dpi=150)
    print("\n[OK] Training history saved to models/training_history.png")


def convert_to_tflite(model_path, tflite_path):
    """
    Convert Keras model to TensorFlow Lite (legacy - not used)
    """
    pass


def convert_to_tflite_direct(model, tflite_path):
    """
    Convert Keras model to TensorFlow Lite directly from model object
    """
    print("\n" + "="*60)
    print("Converting to TensorFlow Lite")
    print("="*60)
    
    # Convert to TFLite directly from model
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Convert
    tflite_model = converter.convert()
    
    # Save
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    
    # Get model size
    size_mb = os.path.getsize(tflite_path) / (1024 * 1024)
    print(f"[OK] Model converted to TFLite")
    print(f"    Saved to: {tflite_path}")
    print(f"    Model size: {size_mb:.2f} MB")


def main():
    """
    Main training pipeline
    """
    print("="*60)
    print("AMLAC Robot - One-Class ML Training")
    print("Model: MobileNetV3-Large")
    print("="*60)
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Max epochs: {EPOCHS}")
    
    # Check for algae folder
    if not os.path.exists(ALGAE_DIR):
        print(f"\n! Error: {ALGAE_DIR}/ folder not found!")
        return
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Prepare dataset (one-class approach)
    if not os.path.exists(TRAIN_DIR):
        if not prepare_one_class_dataset():
            return
    else:
        print("\n[OK] Using existing dataset")
    
    # Create model
    model, base_model = create_model()
    
    # Prepare data generators
    train_gen, val_gen, test_gen = prepare_data()
    
    # Train model
    history = train_model(model, base_model, train_gen, val_gen)
    
    # Evaluate
    test_results = evaluate_model(model, test_gen)
    
    # Plot training history
    plot_training_history(history)
    
    # Save final model in new format
    model.save(MODEL_SAVE_PATH.replace('.h5', '.keras'))
    
    # Convert to TFLite directly from current model (avoid loading issues)
    convert_to_tflite_direct(model, TFLITE_SAVE_PATH)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"[OK] Keras model: {MODEL_SAVE_PATH.replace('.h5', '.keras')}")
    print(f"[OK] TFLite model: {TFLITE_SAVE_PATH}")
    print(f"[OK] Test accuracy: {test_results[1]*100:.2f}%")
    print("\n" + "-"*60)
    print("IMPORTANT: One-Class Classification Notes")
    print("-"*60)
    print("This model was trained with synthetic negative samples.")
    print("For best results on your robot:")
    print("  - Use confidence threshold of 0.7-0.8")
    print("  - If accuracy is low, collect real clean water images")
    print("-"*60)
    print("\nNext steps:")
    print("  1. Copy models/model.tflite to Raspberry Pi")
    print("  2. Place in: /home/pi/amlac_robot/models/")
    print("  3. Run: python main.py")
    print("\nGood luck with your thesis!")


if __name__ == "__main__":
    random.seed(42)
    main()
