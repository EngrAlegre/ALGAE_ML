# AMLAC Robot - Automated Machine Learning Algae Collector

**Grade 12 STEM Thesis Project**

An autonomous water-based robot that uses machine learning to detect and collect algae from water surfaces.

---

## 🌊 Project Overview

AMLAC (Automated Machine Learning Algae Collector Robot) is a Raspberry Pi-based autonomous robot designed to:
- Detect algae using computer vision and machine learning
- Collect algae samples automatically
- Log collection data with GPS coordinates
- Display real-time status on LCD screen

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
cd /home/pi/amlac_robot
chmod +x setup.sh
./setup.sh
sudo reboot
```

### 2. Add Your ML Model
```bash
# Copy your trained model to:
cp /path/to/model.tflite /home/pi/amlac_robot/models/model.tflite
```

### 3. Test Components
```bash
cd /home/pi/amlac_robot/Test
python3 test_camera.py
python3 test_sensors.py
python3 test_lcd.py
python3 test_motors.py  # Ensure robot is safely positioned!
```

### 4. Run the Robot
```bash
cd /home/pi/amlac_robot
python3 main.py
```

---

## 🛠️ Hardware Components

### Main Controller
- **Raspberry Pi 5** (4GB RAM)
- **Raspberry Pi Camera V2** (8MP)

### Sensors
- **TCS34725** - RGB color sensor (I2C)
- **JSN-SR04T** - Waterproof ultrasonic sensor
- **MPU6050** - 6-axis IMU (accelerometer + gyroscope)
- **NEO-6M** - GPS module
- **HX711 + Load Cell** - Weight measurement
- **Float Switch** - Bin full detection

### Actuators
- **2x DC Motors** - Paddle wheels (L298N driver)
- **1x Stepper Motor** - Conveyor belt (TB6600 driver)

### Display & Output
- **16x2 I2C LCD** - Status display
- **CSV Data Logger** - Collection records

---

## 📁 Project Structure

```
/home/pi/amlac_robot/
├── main.py              # Main control loop
├── ml_inference.py      # ML model inference
├── sensor_manager.py    # Sensor reading functions
├── motor_controller.py  # Motor control (L298N + TB6600)
├── lcd_display.py       # LCD display management
├── data_logger.py       # CSV data logging
├── config.py            # Configuration and constants
├── requirements.txt     # Python dependencies
├── setup.sh             # Automated setup script
├── run_robot.sh         # Convenient run script
├── README.md            # This file
├── Test/                # Test scripts folder
│   ├── test_camera.py
│   ├── test_ml_model.py
│   ├── test_sensors.py
│   ├── test_motors.py
│   └── test_lcd.py
└── models/
    └── model.tflite     # TensorFlow Lite model
```

---

## 📊 Data Logging

All detection events are logged to `collection_log.csv` with the following data:
- Timestamp
- Algae detection status
- Confidence score
- GPS coordinates (latitude, longitude)
- Weight collected (kg)
- Collection count
- Distance reading (cm)
- Orientation (pitch, roll)

### View Log File
```bash
cat /home/pi/amlac_robot/collection_log.csv
```

---

## ⚙️ Configuration

Edit `config.py` to customize:
- GPIO pin assignments
- ML model path and confidence threshold
- Sensor I2C addresses
- Motor speeds and timing
- Data logging settings

### Key Settings

```python
# ML Model
MODEL_PATH = '/home/pi/amlac_robot/models/model.tflite'
CONFIDENCE_THRESHOLD = 0.7  # 70% confidence required

# Timing
MAIN_LOOP_DELAY = 2  # Seconds between scans
COLLECTION_DURATION = 5  # Seconds to run conveyor

# Motor Speeds
DEFAULT_SPEED = 50  # 0-100%
TURN_SPEED = 40
```

---

## 🔧 Troubleshooting

### Camera Not Working
```bash
# Check camera connection
vcgencmd get_camera

# Should show: supported=1 detected=1
```

### I2C Devices Not Detected
```bash
# Scan I2C bus
sudo i2cdetect -y 1

# Expected addresses:
# 0x27 - LCD
# 0x29 - TCS34725 color sensor
# 0x68 - MPU6050 IMU
```

### GPS Not Getting Fix
- GPS may take 1-2 minutes to acquire satellite lock
- Ensure GPS antenna has clear view of sky
- Check UART connection: `/dev/serial0`

### Model Inference Slow
- Ensure you're using TFLite model (not full TensorFlow)
- Check model input size (224x224 recommended)
- Consider using quantized model for faster inference

### Motors Not Running
```bash
# Check GPIO setup
gpio readall

# Verify L298N and TB6600 connections
# Ensure power supply is adequate (12V for motors)
```

---

## 📝 GPIO Pin Reference

| Component | GPIO Pin | Physical Pin |
|-----------|----------|--------------|
| I2C SDA | GPIO 2 | Pin 3 |
| I2C SCL | GPIO 3 | Pin 5 |
| Ultrasonic TRIG | GPIO 23 | Pin 16 |
| Ultrasonic ECHO | GPIO 24 | Pin 18 |
| HX711 DT | GPIO 5 | Pin 29 |
| HX711 SCK | GPIO 6 | Pin 31 |
| Float Switch | GPIO 17 | Pin 11 |
| Motor1 IN1 | GPIO 12 | Pin 32 |
| Motor1 IN2 | GPIO 13 | Pin 33 |
| Motor1 ENA | GPIO 19 | Pin 35 |
| Motor2 IN3 | GPIO 16 | Pin 36 |
| Motor2 IN4 | GPIO 26 | Pin 37 |
| Motor2 ENB | GPIO 20 | Pin 38 |
| Stepper PUL | GPIO 22 | Pin 15 |
| Stepper DIR | GPIO 27 | Pin 13 |
| Stepper ENA | GPIO 18 | Pin 12 |

---

## 🎓 Educational Notes

This project demonstrates:
- **Machine Learning**: TensorFlow Lite for on-device inference
- **Computer Vision**: Image classification for algae detection
- **Robotics**: Motor control, sensor fusion, autonomous navigation
- **Embedded Systems**: Raspberry Pi GPIO, I2C, UART communication
- **Data Science**: CSV logging, data collection for analysis
- **Python Programming**: Object-oriented design, error handling

---

## 📚 Resources

- [Teachable Machine](https://teachablemachine.withgoogle.com/) - Train ML models
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [TensorFlow Lite Guide](https://www.tensorflow.org/lite)

---

**Good luck with your thesis defense! 🎓🌿**

