#!/usr/bin/env python3
"""
Test script for all sensors
Tests each sensor individually and displays readings
"""

import time
import RPi.GPIO as GPIO
from sensor_manager import SensorManager

def test_sensors():
    """Test all sensors individually"""
    print("=== AMLAC Sensors Test ===\n")
    
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    try:
        # Initialize sensors
        sensors = SensorManager()
        
        print("\nStarting sensor test (30 seconds)")
        print("Press Ctrl+C to stop early\n")
        print("-" * 60)
        
        for i in range(15):  # 15 readings over 30 seconds
            print(f"\n--- Reading {i+1}/15 ---")
            print(f"Time: {time.strftime('%H:%M:%S')}")
            
            # Test color sensor
            print("\n1. Color Sensor (TCS34725):")
            color_rgb = sensors.read_color_sensor()
            if color_rgb[0] is not None:
                print(f"   R: {color_rgb[0]}, G: {color_rgb[1]}, B: {color_rgb[2]}")
            else:
                print("   Not available")
            
            # Test ultrasonic sensor
            print("\n2. Ultrasonic Sensor (JSN-SR04T):")
            distance = sensors.read_ultrasonic()
            if distance is not None:
                print(f"   Distance: {distance:.2f} cm")
            else:
                print("   Not available or out of range")
            
            # Test IMU
            print("\n3. IMU (MPU6050):")
            imu_data = sensors.read_mpu6050()
            if imu_data:
                print(f"   Accel: X={imu_data['accel']['x']:.2f}, "
                      f"Y={imu_data['accel']['y']:.2f}, "
                      f"Z={imu_data['accel']['z']:.2f} g")
                print(f"   Gyro:  X={imu_data['gyro']['x']:.2f}, "
                      f"Y={imu_data['gyro']['y']:.2f}, "
                      f"Z={imu_data['gyro']['z']:.2f} °/s")
            else:
                print("   Not available")
            
            # Test GPS
            print("\n4. GPS (NEO-6M):")
            gps_data = sensors.read_gps()
            if gps_data:
                print(f"   Latitude: {gps_data['lat']:.6f}")
                print(f"   Longitude: {gps_data['lon']:.6f}")
                print(f"   Altitude: {gps_data['altitude']} m")
                print(f"   Fix Quality: {gps_data['fix_quality']}")
            else:
                print("   No GPS fix (may take 1-2 minutes)")
            
            # Test load cell
            print("\n5. Load Cell (HX711):")
            weight = sensors.read_weight()
            if weight is not None:
                print(f"   Weight: {weight:.2f} kg")
            else:
                print("   Not available")
            
            # Test float switch
            print("\n6. Float Switch:")
            float_active = sensors.read_float_switch()
            print(f"   Status: {'ACTIVE (bin full)' if float_active else 'Inactive (bin not full)'}")
            
            print("\n" + "-" * 60)
            
            time.sleep(2)
        
        print("\n=== Sensor Test Complete ===")
        
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sensors.cleanup()
        GPIO.cleanup()
        print("Cleanup complete")

if __name__ == "__main__":
    test_sensors()

