"""
Configuration file for AMLAC Robot
Contains all GPIO pin assignments and system constants
"""

# ===========================
# GPIO Pin Assignments
# ===========================

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

# ===========================
# UART Configuration
# ===========================
UART_PORT = '/dev/serial0'
GPS_BAUD = 9600
SIM800C_BAUD = 115200

# ===========================
# I2C Device Addresses
# ===========================
LCD_I2C_ADDRESS = 0x27
TCS34725_I2C_ADDRESS = 0x29
MPU6050_I2C_ADDRESS = 0x68

# ===========================
# ML Model Configuration
# ===========================
MODEL_PATH = '/home/pi/amlac_robot/models/model.tflite'
MODEL_INPUT_SIZE = 224  # Teachable Machine standard size
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for algae detection

# ===========================
# System Timing
# ===========================
MAIN_LOOP_DELAY = 2  # Seconds between scans
COLLECTION_DURATION = 5  # Seconds to run conveyor when collecting
LCD_ROTATION_INTERVAL = 5  # Seconds between LCD display changes
ULTRASONIC_TIMEOUT = 1.0  # Seconds
GPS_TIMEOUT = 2.0  # Seconds

# ===========================
# Motor Configuration
# ===========================
PWM_FREQUENCY = 1000  # Hz for motor PWM
DEFAULT_SPEED = 50  # Default motor speed (0-100)
TURN_SPEED = 40  # Speed for turning maneuvers

# ===========================
# Sensor Configuration
# ===========================
HX711_CALIBRATION_FACTOR = 2280  # Adjust based on your load cell
ULTRASONIC_MAX_DISTANCE = 400  # cm
GPS_VALID_FIX_QUALITY = 1  # Minimum GPS fix quality

# ===========================
# Data Logging
# ===========================
LOG_FILE_PATH = '/home/pi/amlac_robot/collection_log.csv'
LOG_HEADERS = [
    'Timestamp',
    'Algae_Detected',
    'Confidence',
    'GPS_Lat',
    'GPS_Lon',
    'Weight_kg',
    'Collection_Count',
    'Distance_cm',
    'Orientation'
]

# ===========================
# Safety Limits
# ===========================
MAX_WEIGHT_KG = 10.0  # Maximum collection bin capacity
MIN_DISTANCE_CM = 10.0  # Minimum safe distance for obstacle avoidance

