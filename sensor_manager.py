"""
Sensor Manager Module for AMLAC Robot
Handles all sensor readings: TCS34725, JSN-SR04T, MPU6050, GPS, HX711, Float Switch
"""

import time
import serial
import pynmea2
import RPi.GPIO as GPIO
from smbus2 import SMBus
import board
import busio
import adafruit_tcs34725
from hx711 import HX711
import config

class SensorManager:
    """
    Manages all sensors for the AMLAC robot.
    Provides unified interface for reading sensor data.
    """
    
    def __init__(self):
        """Initialize all sensors"""
        print("Initializing sensors...")
        
        # Initialize I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize color sensor (TCS34725)
        try:
            self.color_sensor = adafruit_tcs34725.TCS34725(self.i2c)
            self.color_sensor_available = True
            print("✓ TCS34725 color sensor initialized")
        except Exception as e:
            print(f"⚠ Warning: TCS34725 not available - {e}")
            self.color_sensor_available = False
        
        # Initialize ultrasonic sensor (JSN-SR04T)
        try:
            GPIO.setup(config.ULTRASONIC_TRIG, GPIO.OUT)
            GPIO.setup(config.ULTRASONIC_ECHO, GPIO.IN)
            GPIO.output(config.ULTRASONIC_TRIG, GPIO.LOW)
            time.sleep(0.1)
            self.ultrasonic_available = True
            print("✓ JSN-SR04T ultrasonic sensor initialized")
        except Exception as e:
            print(f"⚠ Warning: Ultrasonic sensor not available - {e}")
            self.ultrasonic_available = False
        
        # Initialize MPU6050 IMU
        try:
            self.mpu_bus = SMBus(1)
            self._init_mpu6050()
            self.mpu_available = True
            print("✓ MPU6050 IMU initialized")
        except Exception as e:
            print(f"⚠ Warning: MPU6050 not available - {e}")
            self.mpu_available = False
        
        # Initialize GPS (NEO-6M)
        try:
            self.gps_serial = serial.Serial(
                config.UART_PORT,
                config.GPS_BAUD,
                timeout=config.GPS_TIMEOUT
            )
            self.gps_available = True
            print("✓ NEO-6M GPS initialized")
        except Exception as e:
            print(f"⚠ Warning: GPS not available - {e}")
            self.gps_available = False
        
        # Initialize HX711 load cell
        try:
            self.hx711 = HX711(
                dout_pin=config.HX711_DT,
                pd_sck_pin=config.HX711_SCK
            )
            self.hx711.set_scale_ratio(config.HX711_CALIBRATION_FACTOR)
            self.hx711_available = True
            print("✓ HX711 load cell initialized")
        except Exception as e:
            print(f"⚠ Warning: HX711 not available - {e}")
            self.hx711_available = False
        
        # Initialize float switch
        try:
            GPIO.setup(config.FLOAT_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.float_switch_available = True
            print("✓ Float switch initialized")
        except Exception as e:
            print(f"⚠ Warning: Float switch not available - {e}")
            self.float_switch_available = False
        
        print("Sensor initialization complete!\n")
    
    def _init_mpu6050(self):
        """Initialize MPU6050 IMU sensor"""
        # Wake up MPU6050 (it starts in sleep mode)
        self.mpu_bus.write_byte_data(config.MPU6050_I2C_ADDRESS, 0x6B, 0)
        time.sleep(0.1)
    
    def read_color_sensor(self):
        """
        Read RGB values from TCS34725 color sensor
        
        Returns:
            tuple: (red, green, blue) values or (None, None, None) if unavailable
        """
        if not self.color_sensor_available:
            return (None, None, None)
        
        try:
            r, g, b = self.color_sensor.color_rgb_bytes
            return (r, g, b)
        except Exception as e:
            print(f"Error reading color sensor: {e}")
            return (None, None, None)
    
    def read_ultrasonic(self):
        """
        Measure distance using JSN-SR04T ultrasonic sensor
        
        Returns:
            float: Distance in centimeters or None if unavailable/timeout
        """
        if not self.ultrasonic_available:
            return None
        
        try:
            # Send trigger pulse
            GPIO.output(config.ULTRASONIC_TRIG, GPIO.HIGH)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(config.ULTRASONIC_TRIG, GPIO.LOW)
            
            # Wait for echo
            timeout_start = time.time()
            while GPIO.input(config.ULTRASONIC_ECHO) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start - timeout_start > config.ULTRASONIC_TIMEOUT:
                    return None
            
            while GPIO.input(config.ULTRASONIC_ECHO) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end - timeout_start > config.ULTRASONIC_TIMEOUT:
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound = 34300 cm/s
            distance = round(distance, 2)
            
            # Validate distance
            if 2 <= distance <= config.ULTRASONIC_MAX_DISTANCE:
                return distance
            else:
                return None
                
        except Exception as e:
            print(f"Error reading ultrasonic sensor: {e}")
            return None
    
    def read_mpu6050(self):
        """
        Read accelerometer and gyroscope data from MPU6050
        
        Returns:
            dict: Contains 'accel' (x,y,z) and 'gyro' (x,y,z) or None if unavailable
        """
        if not self.mpu_available:
            return None
        
        try:
            # Read accelerometer data (registers 0x3B to 0x40)
            accel_data = self.mpu_bus.read_i2c_block_data(
                config.MPU6050_I2C_ADDRESS, 0x3B, 6
            )
            
            # Read gyroscope data (registers 0x43 to 0x48)
            gyro_data = self.mpu_bus.read_i2c_block_data(
                config.MPU6050_I2C_ADDRESS, 0x43, 6
            )
            
            # Convert to signed values
            accel_x = self._convert_to_signed(accel_data[0], accel_data[1])
            accel_y = self._convert_to_signed(accel_data[2], accel_data[3])
            accel_z = self._convert_to_signed(accel_data[4], accel_data[5])
            
            gyro_x = self._convert_to_signed(gyro_data[0], gyro_data[1])
            gyro_y = self._convert_to_signed(gyro_data[2], gyro_data[3])
            gyro_z = self._convert_to_signed(gyro_data[4], gyro_data[5])
            
            # Scale values (default sensitivity)
            accel_scale = 16384.0  # For ±2g range
            gyro_scale = 131.0     # For ±250°/s range
            
            return {
                'accel': {
                    'x': accel_x / accel_scale,
                    'y': accel_y / accel_scale,
                    'z': accel_z / accel_scale
                },
                'gyro': {
                    'x': gyro_x / gyro_scale,
                    'y': gyro_y / gyro_scale,
                    'z': gyro_z / gyro_scale
                }
            }
            
        except Exception as e:
            print(f"Error reading MPU6050: {e}")
            return None
    
    def _convert_to_signed(self, high_byte, low_byte):
        """Convert two bytes to signed 16-bit integer"""
        value = (high_byte << 8) | low_byte
        if value > 32767:
            value -= 65536
        return value
    
    def read_gps(self):
        """
        Read GPS data from NEO-6M module
        
        Returns:
            dict: Contains 'lat', 'lon', 'altitude', 'fix_quality' or None if no fix
        """
        if not self.gps_available:
            return None
        
        try:
            # Read multiple lines to find GPGGA sentence
            for _ in range(10):  # Try up to 10 lines
                line = self.gps_serial.readline().decode('ascii', errors='ignore')
                
                if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                    try:
                        msg = pynmea2.parse(line)
                        
                        # Check if we have a valid fix
                        if msg.gps_qual >= config.GPS_VALID_FIX_QUALITY:
                            return {
                                'lat': msg.latitude,
                                'lon': msg.longitude,
                                'altitude': msg.altitude,
                                'fix_quality': msg.gps_qual
                            }
                    except pynmea2.ParseError:
                        continue
            
            return None  # No valid fix found
            
        except Exception as e:
            print(f"Error reading GPS: {e}")
            return None
    
    def read_weight(self):
        """
        Read weight from HX711 load cell
        
        Returns:
            float: Weight in kilograms or None if unavailable
        """
        if not self.hx711_available:
            return None
        
        try:
            # Get average of multiple readings for stability
            weight_grams = self.hx711.get_weight_mean(5)
            weight_kg = weight_grams / 1000.0
            return round(weight_kg, 2)
            
        except Exception as e:
            print(f"Error reading weight: {e}")
            return None
    
    def tare_scale(self):
        """Zero the load cell scale"""
        if self.hx711_available:
            try:
                self.hx711.zero()
                print("Scale tared successfully")
                return True
            except Exception as e:
                print(f"Error taring scale: {e}")
                return False
        return False
    
    def read_float_switch(self):
        """
        Read float switch state
        
        Returns:
            bool: True if bin is full, False otherwise
        """
        if not self.float_switch_available:
            return False
        
        try:
            return GPIO.input(config.FLOAT_SWITCH) == GPIO.HIGH
        except Exception as e:
            print(f"Error reading float switch: {e}")
            return False
    
    def get_all_sensor_data(self):
        """
        Read all sensors and return consolidated data
        
        Returns:
            dict: All sensor readings in a single dictionary
        """
        # Read GPS first (may take time)
        gps_data = self.read_gps()
        
        # Read other sensors
        color_rgb = self.read_color_sensor()
        distance = self.read_ultrasonic()
        imu_data = self.read_mpu6050()
        weight = self.read_weight()
        float_switch_active = self.read_float_switch()
        
        # Calculate orientation from IMU if available
        orientation = None
        if imu_data:
            # Simple tilt calculation (can be improved)
            accel = imu_data['accel']
            import math
            pitch = math.atan2(accel['y'], math.sqrt(accel['x']**2 + accel['z']**2))
            roll = math.atan2(-accel['x'], accel['z'])
            orientation = {
                'pitch': math.degrees(pitch),
                'roll': math.degrees(roll)
            }
        
        return {
            'gps_lat': gps_data['lat'] if gps_data else None,
            'gps_lon': gps_data['lon'] if gps_data else None,
            'gps_altitude': gps_data['altitude'] if gps_data else None,
            'color_rgb': color_rgb,
            'distance': distance,
            'weight': weight if weight else 0.0,
            'orientation': orientation,
            'float_switch_active': float_switch_active,
            'imu_data': imu_data
        }
    
    def cleanup(self):
        """Clean up sensor resources"""
        if self.gps_available:
            try:
                self.gps_serial.close()
            except:
                pass
        
        if self.mpu_available:
            try:
                self.mpu_bus.close()
            except:
                pass
        
        print("Sensors cleaned up")


if __name__ == "__main__":
    """Test sensor readings"""
    print("=== AMLAC Sensor Test ===\n")
    
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    try:
        sensors = SensorManager()
        
        print("\nReading sensors for 30 seconds...")
        print("Press Ctrl+C to stop\n")
        
        for i in range(15):  # 15 readings over 30 seconds
            print(f"--- Reading {i+1} ---")
            data = sensors.get_all_sensor_data()
            
            print(f"GPS: Lat={data['gps_lat']}, Lon={data['gps_lon']}")
            print(f"Color RGB: {data['color_rgb']}")
            print(f"Distance: {data['distance']} cm")
            print(f"Weight: {data['weight']} kg")
            print(f"Orientation: {data['orientation']}")
            print(f"Float Switch: {'ACTIVE' if data['float_switch_active'] else 'inactive'}")
            print()
            
            time.sleep(2)
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sensors.cleanup()
        GPIO.cleanup()
        print("Test complete")

