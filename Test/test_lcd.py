#!/usr/bin/env python3
"""
Test script for LCD display
Tests all display modes and messages
"""

import time
from lcd_display import LCDDisplay, LCDRotator

def test_lcd():
    """Test LCD display functionality"""
    print("=== AMLAC LCD Display Test ===\n")
    
    try:
        # Initialize LCD
        lcd = LCDDisplay()
        
        if not lcd.lcd_available:
            print("⚠ LCD not available")
            print("Check I2C connection and address (default: 0x27)")
            return
        
        print("LCD initialized successfully")
        print("Testing different display modes...\n")
        print("(Each display will show for 3 seconds)\n")
        
        # Test 1: Startup
        print("1. Startup message")
        lcd.show_startup()
        time.sleep(3)
        
        # Test 2: Scanning
        print("2. Scanning display")
        lcd.show_scanning(collection_count=5)
        time.sleep(3)
        
        # Test 3: Algae detected
        print("3. Algae detected")
        lcd.show_algae_detected(confidence=0.85, count=6)
        time.sleep(3)
        
        # Test 4: Collecting
        print("4. Collecting display")
        lcd.show_collecting()
        time.sleep(3)
        
        # Test 5: GPS coordinates
        print("5. GPS display (with fix)")
        lcd.show_gps(lat=14.5995, lon=120.9842)
        time.sleep(3)
        
        print("6. GPS display (no fix)")
        lcd.show_gps(lat=None, lon=None)
        time.sleep(3)
        
        # Test 7: Weight
        print("7. Weight display")
        lcd.show_weight(kg=2.45)
        time.sleep(3)
        
        # Test 8: Sensor data
        print("8. Sensor data display")
        lcd.show_sensor_data(distance=25.5, weight=3.20)
        time.sleep(3)
        
        # Test 9: Error message
        print("9. Error display")
        lcd.show_error("Sensor timeout")
        time.sleep(3)
        
        # Test 10: Bin full warning
        print("10. Bin full warning")
        lcd.show_bin_full()
        time.sleep(3)
        
        # Test 11: Obstacle warning
        print("11. Obstacle warning")
        lcd.show_obstacle(distance_cm=15.5)
        time.sleep(3)
        
        # Test 12: Custom messages
        print("12. Custom messages")
        lcd.show_custom("Hello", "AMLAC!")
        time.sleep(3)
        
        # Test 13: Backlight control
        print("13. Backlight control")
        lcd.show_custom("Backlight", "Test")
        time.sleep(1)
        
        print("   Turning backlight off...")
        lcd.backlight_off()
        time.sleep(2)
        
        print("   Turning backlight on...")
        lcd.backlight_on()
        time.sleep(1)
        
        # Test 14: LCD rotation
        print("14. Testing auto-rotation (15 seconds)")
        rotator = LCDRotator(lcd)
        
        for i in range(15):
            sensor_data = {
                'gps_lat': 14.5995,
                'gps_lon': 120.9842,
                'weight': 3.25 + i * 0.1
            }
            rotator.update(sensor_data, collection_count=10 + i)
            time.sleep(1)
        
        # Test 15: Long text handling
        print("15. Long text handling")
        lcd.show_custom("This is a very long line", "that will be truncated")
        time.sleep(3)
        
        # Cleanup
        print("\n16. Shutdown display")
        lcd.show_shutdown()
        lcd.cleanup()
        
        print("\n=== LCD Test Complete ===")
        print("✓ All display modes working correctly")
        
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
        lcd.cleanup()
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lcd()

