"""
LCD Display Module for AMLAC Robot
Manages 16x2 I2C LCD display for real-time status updates
"""

import time
from RPLCD.i2c import CharLCD
import config

class LCDDisplay:
    """
    Manages the 16x2 I2C LCD display
    Shows scanning status, GPS coordinates, weight, and alerts
    """
    
    def __init__(self):
        """Initialize LCD display"""
        print("Initializing LCD display...")
        
        try:
            # Initialize LCD with I2C address 0x27
            # PCF8574 I2C expander is commonly used
            self.lcd = CharLCD(
                i2c_expander='PCF8574',
                address=config.LCD_I2C_ADDRESS,
                port=1,  # I2C port 1 on Raspberry Pi
                cols=16,
                rows=2,
                dotsize=8,
                charmap='A02',
                auto_linebreaks=True
            )
            
            # Clear display
            self.lcd.clear()
            
            # Display startup message
            self.lcd.write_string('AMLAC Robot')
            self.lcd.crlf()
            self.lcd.write_string('Initializing...')
            time.sleep(2)
            self.lcd.clear()
            
            self.lcd_available = True
            print("✓ LCD display initialized\n")
            
        except Exception as e:
            print(f"⚠ Warning: LCD not available - {e}\n")
            self.lcd_available = False
    
    def clear(self):
        """Clear the LCD display"""
        if self.lcd_available:
            try:
                self.lcd.clear()
            except Exception as e:
                print(f"Error clearing LCD: {e}")
    
    def write_line(self, line1, line2=""):
        """
        Write text to LCD (generic method)
        
        Args:
            line1 (str): Text for first line (max 16 chars)
            line2 (str): Text for second line (max 16 chars)
        """
        if not self.lcd_available:
            return
        
        try:
            self.lcd.clear()
            
            # Truncate lines to 16 characters
            line1 = str(line1)[:16]
            line2 = str(line2)[:16]
            
            # Write first line
            self.lcd.write_string(line1)
            
            # Move to second line if text provided
            if line2:
                self.lcd.crlf()
                self.lcd.write_string(line2)
                
        except Exception as e:
            print(f"Error writing to LCD: {e}")
    
    def show_scanning(self, collection_count):
        """
        Display scanning status
        
        Args:
            collection_count (int): Number of algae samples collected
        """
        line1 = "Scanning..."
        line2 = f"Collected: {collection_count}"
        self.write_line(line1, line2)
    
    def show_algae_detected(self, confidence, count):
        """
        Display algae detection alert
        
        Args:
            confidence (float): Detection confidence (0.0 to 1.0)
            count (int): Current collection count
        """
        line1 = "ALGAE DETECTED!"
        line2 = f"Cnt:{count} C:{int(confidence*100)}%"
        self.write_line(line1, line2)
    
    def show_gps(self, lat, lon):
        """
        Display GPS coordinates
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
        """
        if lat is None or lon is None:
            line1 = "GPS:"
            line2 = "No Fix"
        else:
            # Format coordinates to fit on display
            line1 = f"Lat: {lat:.4f}"
            line2 = f"Lon: {lon:.4f}"
        
        self.write_line(line1, line2)
    
    def show_weight(self, kg):
        """
        Display total collected weight
        
        Args:
            kg (float): Weight in kilograms
        """
        line1 = "Total Collected"
        line2 = f"{kg:.2f} kg"
        self.write_line(line1, line2)
    
    def show_error(self, message):
        """
        Display error message
        
        Args:
            message (str): Error message (will be truncated to fit)
        """
        line1 = "ERROR!"
        line2 = str(message)[:16]
        self.write_line(line1, line2)
    
    def show_bin_full(self):
        """Display bin full warning"""
        line1 = "*** WARNING ***"
        line2 = "BIN FULL!"
        self.write_line(line1, line2)
    
    def show_obstacle(self, distance_cm):
        """
        Display obstacle warning
        
        Args:
            distance_cm (float): Distance to obstacle in cm
        """
        line1 = "OBSTACLE!"
        line2 = f"Distance: {distance_cm:.0f}cm"
        self.write_line(line1, line2)
    
    def show_status(self, status_text):
        """
        Display general status message
        
        Args:
            status_text (str): Status message
        """
        # Split text into two lines if longer than 16 chars
        if len(status_text) <= 16:
            self.write_line(status_text)
        else:
            line1 = status_text[:16]
            line2 = status_text[16:32]
            self.write_line(line1, line2)
    
    def show_startup(self):
        """Display startup message"""
        self.write_line("AMLAC Robot", "Starting...")
        time.sleep(2)
    
    def show_ready(self):
        """Display ready message"""
        self.write_line("System Ready", "Press to Start")
    
    def show_shutdown(self):
        """Display shutdown message"""
        self.write_line("Shutting Down", "Goodbye!")
        time.sleep(2)
        self.clear()
    
    def show_collecting(self):
        """Display collection in progress"""
        self.write_line("Collecting", "Algae...")
    
    def show_sensor_data(self, distance, weight):
        """
        Display sensor data summary
        
        Args:
            distance (float): Distance reading in cm
            weight (float): Weight reading in kg
        """
        line1 = f"Dist: {distance:.0f}cm" if distance else "Dist: ---"
        line2 = f"Weight: {weight:.2f}kg"
        self.write_line(line1, line2)
    
    def show_custom(self, line1, line2=""):
        """
        Display custom message (alias for write_line)
        
        Args:
            line1 (str): First line text
            line2 (str): Second line text
        """
        self.write_line(line1, line2)
    
    def backlight_on(self):
        """Turn on LCD backlight"""
        if self.lcd_available:
            try:
                self.lcd.backlight_enabled = True
            except Exception as e:
                print(f"Error turning on backlight: {e}")
    
    def backlight_off(self):
        """Turn off LCD backlight"""
        if self.lcd_available:
            try:
                self.lcd.backlight_enabled = False
            except Exception as e:
                print(f"Error turning off backlight: {e}")
    
    def cleanup(self):
        """Clean up LCD resources"""
        if self.lcd_available:
            try:
                self.clear()
                self.lcd.close(clear=True)
            except:
                pass
        print("LCD cleaned up")


class LCDRotator:
    """
    Helper class to rotate between different LCD display modes
    """
    
    def __init__(self, lcd_display):
        """
        Initialize LCD rotator
        
        Args:
            lcd_display (LCDDisplay): LCD display instance
        """
        self.lcd = lcd_display
        self.modes = ['scanning', 'gps', 'weight']
        self.current_mode = 0
        self.last_update = time.time()
    
    def update(self, sensor_data, collection_count):
        """
        Update display based on rotation schedule
        
        Args:
            sensor_data (dict): Current sensor readings
            collection_count (int): Number of collections
        """
        current_time = time.time()
        
        # Rotate every N seconds
        if current_time - self.last_update >= config.LCD_ROTATION_INTERVAL:
            self.current_mode = (self.current_mode + 1) % len(self.modes)
            self.last_update = current_time
        
        # Display current mode
        mode = self.modes[self.current_mode]
        
        if mode == 'scanning':
            self.lcd.show_scanning(collection_count)
        elif mode == 'gps':
            self.lcd.show_gps(
                sensor_data.get('gps_lat'),
                sensor_data.get('gps_lon')
            )
        elif mode == 'weight':
            self.lcd.show_weight(sensor_data.get('weight', 0.0))
    
    def reset(self):
        """Reset rotation to first mode"""
        self.current_mode = 0
        self.last_update = time.time()


if __name__ == "__main__":
    """Test LCD display"""
    print("=== AMLAC LCD Display Test ===\n")
    
    try:
        lcd = LCDDisplay()
        
        if not lcd.lcd_available:
            print("LCD not available. Exiting test.")
            exit(1)
        
        print("Testing different display modes...")
        print("(Each display will show for 3 seconds)\n")
        
        # Test 1: Scanning
        print("1. Scanning display")
        lcd.show_scanning(collection_count=5)
        time.sleep(3)
        
        # Test 2: Algae detected
        print("2. Algae detected display")
        lcd.show_algae_detected(confidence=0.85, count=6)
        time.sleep(3)
        
        # Test 3: GPS coordinates
        print("3. GPS display")
        lcd.show_gps(lat=14.5995, lon=120.9842)
        time.sleep(3)
        
        # Test 4: Weight
        print("4. Weight display")
        lcd.show_weight(kg=2.45)
        time.sleep(3)
        
        # Test 5: Error message
        print("5. Error display")
        lcd.show_error("Sensor timeout")
        time.sleep(3)
        
        # Test 6: Bin full
        print("6. Bin full warning")
        lcd.show_bin_full()
        time.sleep(3)
        
        # Test 7: Obstacle
        print("7. Obstacle warning")
        lcd.show_obstacle(distance_cm=15.5)
        time.sleep(3)
        
        # Test 8: Collecting
        print("8. Collecting display")
        lcd.show_collecting()
        time.sleep(3)
        
        # Test 9: Backlight control
        print("9. Testing backlight")
        lcd.show_custom("Backlight", "Test")
        time.sleep(1)
        lcd.backlight_off()
        time.sleep(2)
        lcd.backlight_on()
        time.sleep(1)
        
        # Test 10: Rotation
        print("10. Testing auto-rotation (15 seconds)")
        rotator = LCDRotator(lcd)
        
        for i in range(15):
            sensor_data = {
                'gps_lat': 14.5995,
                'gps_lon': 120.9842,
                'weight': 3.25 + i * 0.1
            }
            rotator.update(sensor_data, collection_count=10)
            time.sleep(1)
        
        # Cleanup
        lcd.show_shutdown()
        lcd.cleanup()
        
        print("\n✓ LCD test complete!")
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
        lcd.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

