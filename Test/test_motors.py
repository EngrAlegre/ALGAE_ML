#!/usr/bin/env python3
"""
Test script for motor control
Tests L298N paddle motors and TB6600 stepper motor
"""

import time
import RPi.GPIO as GPIO
from motor_controller import MotorController

def test_motors():
    """Test all motors with safety checks"""
    print("=== AMLAC Motors Test ===\n")
    print("⚠ WARNING: Ensure robot is safely positioned!")
    print("⚠ Motors will run for short durations")
    print("⚠ Press Ctrl+C at any time to stop\n")
    
    input("Press ENTER to continue or Ctrl+C to cancel...")
    print()
    
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    try:
        # Initialize motors
        motors = MotorController()
        
        # Test 1: Forward movement
        print("\n--- Test 1: Forward Movement ---")
        print("Moving forward at 30% speed for 2 seconds...")
        motors.move_forward(30)
        time.sleep(2)
        motors.stop()
        print("✓ Forward test complete")
        time.sleep(1)
        
        # Test 2: Backward movement
        print("\n--- Test 2: Backward Movement ---")
        print("Moving backward at 30% speed for 2 seconds...")
        motors.move_backward(30)
        time.sleep(2)
        motors.stop()
        print("✓ Backward test complete")
        time.sleep(1)
        
        # Test 3: Left turn
        print("\n--- Test 3: Left Turn ---")
        print("Turning left at 30% speed for 2 seconds...")
        motors.turn_left(30)
        time.sleep(2)
        motors.stop()
        print("✓ Left turn test complete")
        time.sleep(1)
        
        # Test 4: Right turn
        print("\n--- Test 4: Right Turn ---")
        print("Turning right at 30% speed for 2 seconds...")
        motors.turn_right(30)
        time.sleep(2)
        motors.stop()
        print("✓ Right turn test complete")
        time.sleep(1)
        
        # Test 5: Speed variations
        print("\n--- Test 5: Speed Variations ---")
        for speed in [20, 40, 60, 80]:
            print(f"Testing speed: {speed}%")
            motors.move_forward(speed)
            time.sleep(1)
        motors.stop()
        print("✓ Speed variation test complete")
        time.sleep(1)
        
        # Test 6: Individual motor control
        print("\n--- Test 6: Individual Motor Control ---")
        print("Left motor only (50% speed, 1 second)...")
        motors.set_paddle_speed(50, 0)
        time.sleep(1)
        motors.stop()
        time.sleep(0.5)
        
        print("Right motor only (50% speed, 1 second)...")
        motors.set_paddle_speed(0, 50)
        time.sleep(1)
        motors.stop()
        print("✓ Individual motor test complete")
        time.sleep(1)
        
        # Test 7: Stepper motor (conveyor)
        print("\n--- Test 7: Stepper Motor (Conveyor) ---")
        print("Running stepper motor forward (500 steps)...")
        motors.enable_stepper()
        motors.step_motor(500, direction='forward', speed=1000)
        time.sleep(0.5)
        
        print("Running stepper motor backward (500 steps)...")
        motors.step_motor(500, direction='backward', speed=1000)
        motors.disable_stepper()
        print("✓ Stepper motor test complete")
        time.sleep(1)
        
        # Test 8: Collection sequence
        print("\n--- Test 8: Full Collection Sequence ---")
        print("Simulating algae collection...")
        motors.activate_conveyor()
        motors.stop_conveyor()
        print("✓ Collection sequence test complete")
        
        print("\n=== All Motor Tests Complete ===")
        print("✓ All motors functioning correctly")
        
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        motors.cleanup()
        GPIO.cleanup()
        print("Motors stopped and cleanup complete")

if __name__ == "__main__":
    test_motors()

