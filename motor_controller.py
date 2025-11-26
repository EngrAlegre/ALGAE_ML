"""
Motor Controller Module for AMLAC Robot
Controls L298N (paddle motors) and TB6600 (stepper motor)
"""

import time
import RPi.GPIO as GPIO
import config

class MotorController:
    """
    Controls all motors for the AMLAC robot:
    - L298N: Two DC motors for paddle wheels
    - TB6600: Stepper motor for conveyor/actuator
    """
    
    def __init__(self):
        """Initialize all motor controllers"""
        print("Initializing motors...")
        
        # Setup L298N Motor 1 (Left Paddle)
        GPIO.setup(config.MOTOR1_IN1, GPIO.OUT)
        GPIO.setup(config.MOTOR1_IN2, GPIO.OUT)
        GPIO.setup(config.MOTOR1_ENA, GPIO.OUT)
        
        # Setup L298N Motor 2 (Right Paddle)
        GPIO.setup(config.MOTOR2_IN3, GPIO.OUT)
        GPIO.setup(config.MOTOR2_IN4, GPIO.OUT)
        GPIO.setup(config.MOTOR2_ENB, GPIO.OUT)
        
        # Setup TB6600 Stepper Motor
        GPIO.setup(config.STEPPER_PUL, GPIO.OUT)
        GPIO.setup(config.STEPPER_DIR, GPIO.OUT)
        GPIO.setup(config.STEPPER_ENA, GPIO.OUT)
        
        # Initialize PWM for DC motors
        self.pwm_motor1 = GPIO.PWM(config.MOTOR1_ENA, config.PWM_FREQUENCY)
        self.pwm_motor2 = GPIO.PWM(config.MOTOR2_ENB, config.PWM_FREQUENCY)
        
        # Start PWM with 0% duty cycle
        self.pwm_motor1.start(0)
        self.pwm_motor2.start(0)
        
        # Disable stepper motor initially
        GPIO.output(config.STEPPER_ENA, GPIO.HIGH)  # HIGH = disabled for TB6600
        
        # Initialize motor states
        self.motor1_speed = 0
        self.motor2_speed = 0
        self.stepper_enabled = False
        
        print("✓ Motors initialized\n")
    
    def set_paddle_speed(self, left_speed, right_speed):
        """
        Set speed for both paddle motors
        
        Args:
            left_speed (int): Speed for left motor (-100 to 100)
            right_speed (int): Speed for right motor (-100 to 100)
                              Positive = forward, Negative = backward
        """
        # Clamp speeds to valid range
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        # Set left motor (Motor 1)
        if left_speed > 0:
            GPIO.output(config.MOTOR1_IN1, GPIO.HIGH)
            GPIO.output(config.MOTOR1_IN2, GPIO.LOW)
            self.pwm_motor1.ChangeDutyCycle(abs(left_speed))
        elif left_speed < 0:
            GPIO.output(config.MOTOR1_IN1, GPIO.LOW)
            GPIO.output(config.MOTOR1_IN2, GPIO.HIGH)
            self.pwm_motor1.ChangeDutyCycle(abs(left_speed))
        else:
            GPIO.output(config.MOTOR1_IN1, GPIO.LOW)
            GPIO.output(config.MOTOR1_IN2, GPIO.LOW)
            self.pwm_motor1.ChangeDutyCycle(0)
        
        # Set right motor (Motor 2)
        if right_speed > 0:
            GPIO.output(config.MOTOR2_IN3, GPIO.HIGH)
            GPIO.output(config.MOTOR2_IN4, GPIO.LOW)
            self.pwm_motor2.ChangeDutyCycle(abs(right_speed))
        elif right_speed < 0:
            GPIO.output(config.MOTOR2_IN3, GPIO.LOW)
            GPIO.output(config.MOTOR2_IN4, GPIO.HIGH)
            self.pwm_motor2.ChangeDutyCycle(abs(right_speed))
        else:
            GPIO.output(config.MOTOR2_IN3, GPIO.LOW)
            GPIO.output(config.MOTOR2_IN4, GPIO.LOW)
            self.pwm_motor2.ChangeDutyCycle(0)
        
        self.motor1_speed = left_speed
        self.motor2_speed = right_speed
    
    def move_forward(self, speed=None):
        """
        Move robot forward
        
        Args:
            speed (int): Speed 0-100 (default from config)
        """
        if speed is None:
            speed = config.DEFAULT_SPEED
        
        self.set_paddle_speed(speed, speed)
        print(f"Moving forward at speed {speed}")
    
    def move_backward(self, speed=None):
        """
        Move robot backward
        
        Args:
            speed (int): Speed 0-100 (default from config)
        """
        if speed is None:
            speed = config.DEFAULT_SPEED
        
        self.set_paddle_speed(-speed, -speed)
        print(f"Moving backward at speed {speed}")
    
    def turn_left(self, speed=None):
        """
        Turn robot left (left motor backward, right motor forward)
        
        Args:
            speed (int): Speed 0-100 (default from config)
        """
        if speed is None:
            speed = config.TURN_SPEED
        
        self.set_paddle_speed(-speed, speed)
        print(f"Turning left at speed {speed}")
    
    def turn_right(self, speed=None):
        """
        Turn robot right (left motor forward, right motor backward)
        
        Args:
            speed (int): Speed 0-100 (default from config)
        """
        if speed is None:
            speed = config.TURN_SPEED
        
        self.set_paddle_speed(speed, -speed)
        print(f"Turning right at speed {speed}")
    
    def stop(self):
        """Stop both paddle motors"""
        self.set_paddle_speed(0, 0)
        print("Motors stopped")
    
    def enable_stepper(self):
        """Enable stepper motor"""
        GPIO.output(config.STEPPER_ENA, GPIO.LOW)  # LOW = enabled for TB6600
        self.stepper_enabled = True
        time.sleep(0.01)  # Small delay for driver to enable
    
    def disable_stepper(self):
        """Disable stepper motor"""
        GPIO.output(config.STEPPER_ENA, GPIO.HIGH)  # HIGH = disabled for TB6600
        self.stepper_enabled = False
    
    def step_motor(self, steps, direction='forward', speed=1000):
        """
        Move stepper motor a specific number of steps
        
        Args:
            steps (int): Number of steps to move
            direction (str): 'forward' or 'backward'
            speed (int): Steps per second (default 1000)
        """
        if not self.stepper_enabled:
            self.enable_stepper()
        
        # Set direction
        if direction == 'forward':
            GPIO.output(config.STEPPER_DIR, GPIO.HIGH)
        else:
            GPIO.output(config.STEPPER_DIR, GPIO.LOW)
        
        # Calculate delay between pulses
        delay = 1.0 / (speed * 2)  # Divide by 2 for HIGH and LOW states
        
        # Generate step pulses
        for _ in range(steps):
            GPIO.output(config.STEPPER_PUL, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(config.STEPPER_PUL, GPIO.LOW)
            time.sleep(delay)
    
    def activate_conveyor(self):
        """
        Activate conveyor belt (stepper motor)
        Runs for the duration specified in config
        """
        print("Activating conveyor...")
        self.enable_stepper()
        
        # Run conveyor for collection
        # Adjust steps based on your conveyor design
        total_steps = 2000  # Example: 2000 steps for one collection cycle
        self.step_motor(total_steps, direction='forward', speed=1000)
        
        print("Conveyor cycle complete")
    
    def stop_conveyor(self):
        """Stop conveyor belt"""
        self.disable_stepper()
        print("Conveyor stopped")
    
    def stop_all(self):
        """Emergency stop - stop all motors immediately"""
        # Stop paddle motors
        self.stop()
        
        # Stop and disable stepper
        self.stop_conveyor()
        
        print("ALL MOTORS STOPPED")
    
    def cleanup(self):
        """Clean up motor resources"""
        # Stop all motors
        self.stop_all()
        
        # Stop PWM
        self.pwm_motor1.stop()
        self.pwm_motor2.stop()
        
        print("Motors cleaned up")


if __name__ == "__main__":
    """Test motor control"""
    print("=== AMLAC Motor Test ===\n")
    print("WARNING: Make sure robot is safely positioned!")
    print("Motors will run for short durations\n")
    
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    try:
        motors = MotorController()
        
        # Test sequence
        print("\n1. Testing forward movement...")
        motors.move_forward(30)
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        print("\n2. Testing backward movement...")
        motors.move_backward(30)
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        print("\n3. Testing left turn...")
        motors.turn_left(30)
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        print("\n4. Testing right turn...")
        motors.turn_right(30)
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        print("\n5. Testing conveyor/stepper motor...")
        motors.activate_conveyor()
        motors.stop_conveyor()
        time.sleep(1)
        
        print("\n6. Testing speed variations...")
        for speed in [20, 50, 80]:
            print(f"   Speed: {speed}%")
            motors.move_forward(speed)
            time.sleep(1)
        motors.stop()
        
        print("\nMotor test complete!")
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        motors.cleanup()
        GPIO.cleanup()
        print("Test complete")

