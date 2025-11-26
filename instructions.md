# AI Code Generation Prompt for AMLAC Robot
## Complete Python Program for Automated Machine Learning Algae Collector

---

## Project Context

You are creating a complete Python program for an autonomous water-based robot called AMLAC (Automated Machine Learning Algae Collector Robot). This is a Grade 12 STEM thesis project running on Raspberry Pi 5.

---

## System Architecture

### Hardware Configuration
- **Main Controller**: Raspberry Pi 5 (4GB RAM)
- **Camera**: Raspberry Pi Camera V2 (8MP) - CSI port
- **Display**: 16x2 I2C LCD (address 0x27)
- **Machine Learning**: TensorFlow Lite model (trained on Teachable Machine)
- **Motors**:
  - 2x DC motors (paddle wheels) controlled via L298N
  - 1x DC motor (conveyor) controlled via L298N
  - 1x Stepper motor (actuator) controlled via TB6600
- **Sensors**:
  - TCS34725 RGB color sensor (I2C address 0x29)
  - JSN-SR04T waterproof ultrasonic sensor
  - MPU6050 IMU (I2C address 0x68)
  - NEO-6M GPS module (UART /dev/serial0)
  - HX711 + Load Cell (weight measurement)
  - Float switch (digital input)
  - SIM800C GSM module (optional, UART)

### GPIO Pin Assignments
```python
# I2C Bus (shared by LCD, TCS34725, MPU6050)
I2C_SDA = 2  # GPIO 2, Physical Pin 3
I2C_SCL = 3  # GPIO 3, Physical Pin 5

# Ultrasonic Sensor (JSN-SR04T)
ULTRASONIC_TRIG = 23  # GPIO 23, Physical Pin 16
ULTRASONIC_ECHO = 24  # GPIO 24, Physical Pin 18

# Load Cell (HX711)
HX711_DT = 5   # GPIO 5, Physical Pin 29
HX711_SCK = 6  # GPIO 6, Physical Pin 31

# Float Switch
FLOAT_SWITCH = 17  # GPIO 17, Physical Pin 11

# L298N Motor Driver (Paddle Motors)
# Motor 1 (Left Paddle)
MOTOR1_IN1 = 12  # GPIO 12, Physical Pin 32
MOTOR1_IN2 = 13  # GPIO 13, Physical Pin 33
MOTOR1_ENA = 19  # GPIO 19, Physical Pin 35

# Motor 2 (Right Paddle)
MOTOR2_IN3 = 16  # GPIO 16, Physical Pin 36
MOTOR2_IN4 = 26  # GPIO 26, Physical Pin 37
MOTOR2_ENB = 20  # GPIO 20, Physical Pin 38

# TB6600 Stepper Driver (Conveyor/Actuator)
STEPPER_PUL = 22  # GPIO 22, Physical Pin 15
STEPPER_DIR = 27  # GPIO 27, Physical Pin 13
STEPPER_ENA = 18  # GPIO 18, Physical Pin 12

# UART (GPS and SIM800C share, must switch between them)
UART_PORT = '/dev/serial0'
GPS_BAUD = 9600
SIM800C_BAUD = 115200
```

---

## Program Requirements

### Project Structure
Create the following files:
```
/home/pi/amlac_robot/
├── main.py              # Main control loop
├── ml_inference.py      # ML model inference
├── sensor_manager.py    # All sensor reading functions
├── motor_controller.py  # Motor control (L298N + TB6600)
├── lcd_display.py       # LCD display management
├── data_logger.py       # CSV data logging
├── config.py            # Configuration and constants
└── models/
    └── model.tflite     # Teachable Machine exported model
```

### Core Functionality

#### 1. ML Inference Module (`ml_inference.py`)
- Load TensorFlow Lite model from `/home/pi/amlac_robot/models/model.tflite`
- Accept image array from Picamera2
- Preprocess image to 224x224 (standard Teachable Machine size)
- Run inference
- Return: (is_algae_detected: bool, confidence: float)
- Threshold: confidence > 0.7 means algae detected

#### 2. Sensor Manager Module (`sensor_manager.py`)
- **TCS34725 Color Sensor**: Read RGB values, return as tuple
- **JSN-SR04T Ultrasonic**: Measure distance in cm, handle timeout
- **MPU6050 IMU**: Read accelerometer and gyroscope data
- **NEO-6M GPS**: Parse NMEA sentences ($GPGGA), return lat/lon
- **HX711 Load Cell**: Read weight in kg, include tare function
- **Float Switch**: Read digital state (HIGH/LOW)
- All readings bundled into a dictionary: `get_all_sensor_data()`

#### 3. Motor Controller Module (`motor_controller.py`)
- **L298N Control**:
  - `set_paddle_speed(left_speed, right_speed)` - PWM 0-100
  - `move_forward(speed)`, `move_backward(speed)`, `turn_left(speed)`, `turn_right(speed)`, `stop()`
  - `activate_conveyor()`, `stop_conveyor()`
- **TB6600 Control**:
  - `step_motor(steps, direction)` - for actuator movement
  - `enable_stepper()`, `disable_stepper()`

#### 4. LCD Display Module (`lcd_display.py`)
- Initialize 16x2 I2C LCD (PCF8574, address 0x27)
- Display methods:
  - `show_scanning(collection_count)` - "Scanning... / Collected: N"
  - `show_algae_detected(confidence, count)` - "ALGAE DETECTED! / Cnt:N C:XX%"
  - `show_gps(lat, lon)` - "Lat: XX.XXXX / Lon: XX.XXXX"
  - `show_weight(kg)` - "Total Collected / X.XX kg"
  - `show_error(message)` - Display error messages
- Rotating display: cycle through scanning → GPS → weight every 5 seconds

#### 5. Data Logger Module (`data_logger.py`)
- Create CSV file: `collection_log.csv`
- Headers: `Timestamp, Algae_Detected, Confidence, GPS_Lat, GPS_Lon, Weight_kg, Collection_Count, Distance_cm, Orientation`
- Append row on each detection event
- Timestamp format: `YYYY-MM-DD HH:MM:SS`

#### 6. Main Control Loop (`main.py`)
**Initialization:**
1. Import all modules
2. Initialize GPIO (BCM mode)
3. Initialize Picamera2
4. Load ML model
5. Initialize all sensors
6. Initialize motors
7. Initialize LCD
8. Create data logger
9. Set initial variables: `collection_count = 0`, `lcd_cycle = 0`

**Main Loop:**
```
while True:
    try:
        # 1. Capture image
        image = camera.capture_array()
        
        # 2. Run ML inference
        algae_detected, confidence = ml_model.detect(image)
        
        # 3. Read all sensors
        sensor_data = sensors.get_all_sensor_data()
        
        # 4. Decision logic
        if algae_detected and confidence > 0.7:
            # Display detection on LCD
            lcd.show_algae_detected(confidence, collection_count)
            
            # Activate collection mechanism
            motors.activate_conveyor()
            time.sleep(5)  # Collect for 5 seconds
            motors.stop_conveyor()
            
            # Increment count
            collection_count += 1
            
            # Log data to CSV
            logger.log_detection(
                algae_detected=True,
                confidence=confidence,
                gps_lat=sensor_data['gps_lat'],
                gps_lon=sensor_data['gps_lon'],
                weight_kg=sensor_data['weight'],
                collection_count=collection_count,
                distance_cm=sensor_data['distance'],
                orientation=sensor_data['orientation']
            )
            
        else:
            # Rotate LCD display between different info
            lcd_cycle = (lcd_cycle + 1) % 3
            
            if lcd_cycle == 0:
                lcd.show_scanning(collection_count)
            elif lcd_cycle == 1 and sensor_data['gps_lat'] is not None:
                lcd.show_gps(sensor_data['gps_lat'], sensor_data['gps_lon'])
            elif lcd_cycle == 2:
                lcd.show_weight(sensor_data['weight'])
        
        # 5. Check float switch (bin full warning)
        if sensor_data['float_switch_active']:
            lcd.show_error("BIN FULL!")
            motors.stop_all()
            time.sleep(10)
        
        # 6. Wait before next scan
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\nStopping robot...")
        break
    except Exception as e:
        print(f"Error: {e}")
        lcd.show_error(f"Error: {str(e)[:16]}")
        time.sleep(5)

# Cleanup
motors.stop_all()
GPIO.cleanup()
camera.stop()
print("Robot stopped. Data saved to collection_log.csv")
```

---

## Code Requirements

### Python Version & Libraries
- Python 3.9+
- Required packages (include pip install commands in comments):
  ```python
  # pip3 install tflite-runtime
  # pip3 install picamera2
  # pip3 install RPi.GPIO
  # pip3 install adafruit-circuitpython-tcs34725
  # pip3 install smbus2
  # pip3 install RPLCD
  # pip3 install hx711
  # pip3 install pynmea2 pyserial
  # pip3 install numpy pillow
  ```

### Code Style
- Use clear, descriptive variable names
- Add docstrings to all classes and functions
- Include inline comments for complex logic
- Use try-except blocks for error handling
- Log errors to console with timestamps
- Use constants from `config.py` for all GPIO pins and settings

### Error Handling
- Graceful degradation: if one sensor fails, continue with others
- Timeout handling for ultrasonic and GPS
- Retry logic for I2C communication errors
- Safe motor shutdown on exception

### Performance
- Camera capture at ~1 FPS (adequate for algae detection)
- ML inference should complete in < 500ms
- Total loop time: ~2 seconds per cycle
- Efficient GPIO usage (cleanup on exit)

---

## Special Considerations

### 1. TensorFlow Model Format
The model is exported from Teachable Machine as a standard TF file:
just check the Algae-Model by teachable ml folder

### 2. GPS Parsing
- GPS may take 1-2 minutes to get satellite lock
- Return None if no valid fix yet
- Parse $GPGGA sentence for lat/lon
- Handle decimal degree conversion

### 3. HX711 Calibration
- Include `tare()` function to zero the scale
- Calibration factor may need adjustment
- Average multiple readings for stability

### 4. LCD Display Rotation
- Automatically cycle between different views every 5 seconds
- Pause rotation when algae is detected
- Show priority messages (errors, bin full) immediately

### 5. Motor Safety
- Always stop motors before GPIO cleanup
- Use PWM for smooth speed control
- Include direction reversal capability
- Emergency stop on exception

### 6. CSV Data Logging
- Create file if doesn't exist
- Append mode to preserve previous runs
- Flush after each write to prevent data loss
- Include timestamp for every entry

---

## Testing Strategy

Each module should be testable independently:

### Test Scripts to Include

**test_camera.py**
```python
# Capture and save test image
# Verify camera is working
```

**test_ml_model.py**
```python
# Load model and run inference on test images
# Print confidence scores
```

**test_sensors.py**
```python
# Read each sensor individually
# Print values to console
```

**test_motors.py**
```python
# Test each motor individually
# Verify direction and speed control
```

**test_lcd.py**
```python
# Display test messages
# Verify all characters visible
```

---

## Output Format

Generate complete, production-ready Python code for all modules with:
1. Proper imports and dependencies
2. Full error handling
3. Detailed comments and docstrings
4. Configuration constants
5. Testing functions
6. Main execution guard (`if __name__ == "__main__":`)

Make the code beginner-friendly but professional - this is for Grade 12 students learning robotics and ML.

---

## Additional Notes

- The robot operates autonomously on water
- Power: 12V battery for motors, 5V regulated for Pi
- All code runs locally on Raspberry Pi 5 (no cloud dependencies)
- Model inference happens on-device using TFLite
- Data logged to CSV for later analysis
- LCD provides real-time status during operation

---

## Generate Complete Code

Based on the above specifications, generate all Python files with complete implementation. Include:
- All imports
- All GPIO pin definitions
- All sensor initialization
- All motor control logic
- All ML inference code
- Main control loop
- Error handling
- Data logging
- LCD display management
- Testing functions

Make the code production-ready for their thesis defense!
