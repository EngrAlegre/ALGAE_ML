#!/usr/bin/env python3
"""
AMLAC Robot - Main Control Program
Automated Machine Learning Algae Collector Robot
Grade 12 STEM Thesis Project

This is the main control loop that coordinates all robot systems:
- Camera and ML inference for algae detection
- Sensor readings (GPS, ultrasonic, IMU, weight, etc.)
- Motor control for navigation and collection
- LCD display for status updates
- Data logging to CSV

Author: AMLAC Team
"""

import time
import sys
import signal
from datetime import datetime
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# Import AMLAC modules
import config
from ml_inference import MLInference
from sensor_manager import SensorManager
from motor_controller import MotorController
from lcd_display import LCDDisplay, LCDRotator
from data_logger import DataLogger


class AMLACRobot:
    """
    Main robot control class
    Coordinates all subsystems and implements the main control loop
    """
    
    def __init__(self):
        """Initialize all robot systems"""
        print("\n" + "=" * 50)
        print("AMLAC Robot - Initialization")
        print("=" * 50 + "\n")
        
        # Initialize GPIO
        print("Setting up GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        print("✓ GPIO configured\n")
        
        # Initialize camera
        print("Initializing camera...")
        try:
            self.camera = Picamera2()
            # Configure camera for ML inference
            camera_config = self.camera.create_still_configuration(
                main={"size": (640, 480)},
                buffer_count=2
            )
            self.camera.configure(camera_config)
            self.camera.start()
            time.sleep(2)  # Allow camera to warm up
            self.camera_available = True
            print("✓ Camera initialized\n")
        except Exception as e:
            print(f"⚠ Warning: Camera not available - {e}\n")
            self.camera_available = False
        
        # Initialize ML model
        self.ml_model = MLInference()
        
        # Initialize sensors
        self.sensors = SensorManager()
        
        # Initialize motors
        self.motors = MotorController()
        
        # Initialize LCD display
        self.lcd = LCDDisplay()
        self.lcd_rotator = LCDRotator(self.lcd)
        
        # Initialize data logger
        self.logger = DataLogger()
        
        # Initialize state variables
        self.collection_count = 0
        self.running = False
        self.start_time = datetime.now()
        
        print("=" * 50)
        print("✓ All systems initialized!")
        print("=" * 50 + "\n")
        
        # Display ready message
        self.lcd.show_ready()
    
    def run(self):
        """
        Main control loop
        Continuously scans for algae and collects when detected
        """
        self.running = True
        self.lcd.show_scanning(self.collection_count)
        
        print("Starting main control loop...")
        print("Press Ctrl+C to stop\n")
        
        # Log startup
        self.logger.log_event('INFO', 'Robot started')
        
        loop_count = 0
        
        while self.running:
            try:
                loop_count += 1
                loop_start_time = time.time()
                
                # ==========================================
                # 1. CAPTURE IMAGE
                # ==========================================
                if self.camera_available:
                    image = self.camera.capture_array()
                else:
                    # If no camera, create dummy image for testing
                    import numpy as np
                    image = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # ==========================================
                # 2. RUN ML INFERENCE
                # ==========================================
                algae_detected, confidence = self.ml_model.detect(image)
                
                # ==========================================
                # 3. READ ALL SENSORS
                # ==========================================
                sensor_data = self.sensors.get_all_sensor_data()
                
                # ==========================================
                # 4. DECISION LOGIC
                # ==========================================
                
                # Check for bin full condition first (highest priority)
                if sensor_data['float_switch_active']:
                    self.handle_bin_full()
                    continue
                
                # Check for obstacles
                if sensor_data['distance'] is not None:
                    if sensor_data['distance'] < config.MIN_DISTANCE_CM:
                        self.handle_obstacle(sensor_data['distance'])
                        continue
                
                # Check for algae detection
                if algae_detected and confidence > config.CONFIDENCE_THRESHOLD:
                    self.handle_algae_detection(confidence, sensor_data)
                else:
                    # Normal scanning mode - rotate LCD display
                    self.lcd_rotator.update(sensor_data, self.collection_count)
                
                # ==========================================
                # 5. PERIODIC STATUS UPDATES
                # ==========================================
                if loop_count % 30 == 0:  # Every 30 loops (~1 minute)
                    self.print_status(sensor_data)
                
                # ==========================================
                # 6. WAIT BEFORE NEXT SCAN
                # ==========================================
                loop_duration = time.time() - loop_start_time
                sleep_time = max(0, config.MAIN_LOOP_DELAY - loop_duration)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print("\n\nStopping robot...")
                break
            except Exception as e:
                print(f"\n⚠ Error in main loop: {e}")
                self.lcd.show_error(str(e)[:16])
                self.logger.log_event('ERROR', str(e))
                time.sleep(5)
        
        # Shutdown
        self.shutdown()
    
    def handle_algae_detection(self, confidence, sensor_data):
        """
        Handle algae detection event
        
        Args:
            confidence (float): Detection confidence
            sensor_data (dict): Current sensor readings
        """
        print(f"\n🌿 ALGAE DETECTED! Confidence: {confidence:.2%}")
        
        # Display detection on LCD
        self.lcd.show_algae_detected(confidence, self.collection_count)
        
        # Stop movement (if moving)
        self.motors.stop()
        
        # Show collecting status
        time.sleep(1)
        self.lcd.show_collecting()
        
        # Activate collection mechanism
        print("Activating collection mechanism...")
        self.motors.activate_conveyor()
        time.sleep(config.COLLECTION_DURATION)
        self.motors.stop_conveyor()
        
        # Increment collection count
        self.collection_count += 1
        
        print(f"✓ Collection complete! Total collected: {self.collection_count}\n")
        
        # Log detection to CSV
        self.logger.log_detection(
            algae_detected=True,
            confidence=confidence,
            gps_lat=sensor_data['gps_lat'],
            gps_lon=sensor_data['gps_lon'],
            weight_kg=sensor_data['weight'],
            collection_count=self.collection_count,
            distance_cm=sensor_data['distance'],
            orientation=sensor_data['orientation']
        )
        
        # Reset LCD rotator
        self.lcd_rotator.reset()
    
    def handle_bin_full(self):
        """Handle bin full condition"""
        print("\n⚠ WARNING: Collection bin is full!")
        self.lcd.show_bin_full()
        self.motors.stop_all()
        
        # Log event
        self.logger.log_event('WARNING', 'Collection bin full')
        
        # Wait for user intervention
        time.sleep(10)
    
    def handle_obstacle(self, distance):
        """
        Handle obstacle detection
        
        Args:
            distance (float): Distance to obstacle in cm
        """
        print(f"\n⚠ Obstacle detected at {distance:.1f} cm")
        self.lcd.show_obstacle(distance)
        
        # Stop motors
        self.motors.stop()
        
        # Simple obstacle avoidance (can be improved)
        # Turn right for 2 seconds
        self.motors.turn_right(speed=30)
        time.sleep(2)
        self.motors.stop()
        
        time.sleep(1)
    
    def print_status(self, sensor_data):
        """
        Print status summary to console
        
        Args:
            sensor_data (dict): Current sensor readings
        """
        runtime = datetime.now() - self.start_time
        
        print("\n" + "-" * 50)
        print(f"Status Update - Runtime: {runtime}")
        print("-" * 50)
        print(f"Collections: {self.collection_count}")
        print(f"Weight: {sensor_data['weight']:.2f} kg")
        print(f"GPS: {sensor_data['gps_lat']}, {sensor_data['gps_lon']}")
        print(f"Distance: {sensor_data['distance']} cm")
        print(f"Orientation: {sensor_data['orientation']}")
        print("-" * 50 + "\n")
    
    def shutdown(self):
        """Clean shutdown of all systems"""
        print("\n" + "=" * 50)
        print("Shutting down AMLAC Robot")
        print("=" * 50 + "\n")
        
        self.running = False
        
        # Log shutdown
        self.logger.log_event('INFO', f'Robot stopped - Total collections: {self.collection_count}')
        
        # Print final statistics
        print(f"\nFinal Statistics:")
        print(f"  Total collections: {self.collection_count}")
        print(f"  Runtime: {datetime.now() - self.start_time}")
        self.logger.print_statistics()
        
        # Stop all motors
        print("Stopping motors...")
        self.motors.cleanup()
        
        # Stop camera
        if self.camera_available:
            print("Stopping camera...")
            self.camera.stop()
        
        # Cleanup sensors
        print("Cleaning up sensors...")
        self.sensors.cleanup()
        
        # Display shutdown message
        self.lcd.show_shutdown()
        self.lcd.cleanup()
        
        # Cleanup GPIO
        print("Cleaning up GPIO...")
        GPIO.cleanup()
        
        print("\n✓ Shutdown complete")
        print(f"Data saved to: {config.LOG_FILE_PATH}\n")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nReceived interrupt signal...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create and run robot
        robot = AMLACRobot()
        robot.run()
        
    except Exception as e:
        print(f"\n⚠ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
        # Attempt cleanup
        try:
            GPIO.cleanup()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()

