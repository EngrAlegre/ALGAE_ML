"""
Data Logger Module for AMLAC Robot
Handles CSV logging of all detection events and sensor data
"""

import csv
import os
from datetime import datetime
import config

class DataLogger:
    """
    Logs all algae detection events and sensor data to CSV file
    """
    
    def __init__(self, log_file_path=None):
        """
        Initialize data logger
        
        Args:
            log_file_path (str): Path to CSV log file
        """
        if log_file_path is None:
            log_file_path = config.LOG_FILE_PATH
        
        self.log_file_path = log_file_path
        self.headers = config.LOG_HEADERS
        
        print(f"Initializing data logger...")
        print(f"Log file: {self.log_file_path}")
        
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Created directory: {log_dir}")
        
        # Check if file exists
        self.file_exists = os.path.isfile(self.log_file_path)
        
        # Create file with headers if it doesn't exist
        if not self.file_exists:
            self._create_log_file()
            print("✓ New log file created with headers")
        else:
            print("✓ Using existing log file")
        
        print()
    
    def _create_log_file(self):
        """Create new CSV file with headers"""
        try:
            with open(self.log_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers)
            self.file_exists = True
        except Exception as e:
            print(f"Error creating log file: {e}")
    
    def log_detection(self, algae_detected, confidence, gps_lat, gps_lon,
                     weight_kg, collection_count, distance_cm, orientation):
        """
        Log an algae detection event
        
        Args:
            algae_detected (bool): Whether algae was detected
            confidence (float): Detection confidence (0.0 to 1.0)
            gps_lat (float): GPS latitude
            gps_lon (float): GPS longitude
            weight_kg (float): Current weight in kg
            collection_count (int): Total collection count
            distance_cm (float): Distance reading in cm
            orientation (dict): Orientation data (pitch, roll)
        """
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Format orientation data
            orientation_str = ""
            if orientation:
                pitch = orientation.get('pitch', 0)
                roll = orientation.get('roll', 0)
                orientation_str = f"P:{pitch:.1f} R:{roll:.1f}"
            
            # Prepare row data
            row = [
                timestamp,
                'Yes' if algae_detected else 'No',
                f"{confidence:.4f}" if confidence else "0.0000",
                f"{gps_lat:.6f}" if gps_lat is not None else "N/A",
                f"{gps_lon:.6f}" if gps_lon is not None else "N/A",
                f"{weight_kg:.2f}" if weight_kg is not None else "0.00",
                collection_count,
                f"{distance_cm:.2f}" if distance_cm is not None else "N/A",
                orientation_str
            ]
            
            # Append to CSV file
            with open(self.log_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
            
            # Flush to ensure data is written immediately
            # (This is automatic with 'with' statement, but being explicit)
            
            print(f"[LOG] {timestamp} - Algae: {algae_detected}, Confidence: {confidence:.2%}, Count: {collection_count}")
            
        except Exception as e:
            print(f"Error logging data: {e}")
    
    def log_event(self, event_type, message, sensor_data=None):
        """
        Log a general event (errors, warnings, status changes)
        
        Args:
            event_type (str): Type of event (ERROR, WARNING, INFO)
            message (str): Event message
            sensor_data (dict): Optional sensor data to include
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create a special row for events
            row = [
                timestamp,
                event_type,
                message,
                sensor_data.get('gps_lat', 'N/A') if sensor_data else 'N/A',
                sensor_data.get('gps_lon', 'N/A') if sensor_data else 'N/A',
                sensor_data.get('weight', 'N/A') if sensor_data else 'N/A',
                'N/A',
                sensor_data.get('distance', 'N/A') if sensor_data else 'N/A',
                'N/A'
            ]
            
            with open(self.log_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
            
            print(f"[{event_type}] {timestamp} - {message}")
            
        except Exception as e:
            print(f"Error logging event: {e}")
    
    def get_statistics(self):
        """
        Calculate statistics from log file
        
        Returns:
            dict: Statistics including total detections, average confidence, etc.
        """
        if not self.file_exists:
            return {}
        
        try:
            total_rows = 0
            total_detections = 0
            confidence_sum = 0.0
            confidence_count = 0
            
            with open(self.log_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    total_rows += 1
                    
                    # Count detections
                    if row['Algae_Detected'] == 'Yes':
                        total_detections += 1
                        
                        # Sum confidence values
                        try:
                            conf = float(row['Confidence'])
                            confidence_sum += conf
                            confidence_count += 1
                        except:
                            pass
            
            # Calculate averages
            avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 0.0
            detection_rate = total_detections / total_rows if total_rows > 0 else 0.0
            
            return {
                'total_rows': total_rows,
                'total_detections': total_detections,
                'average_confidence': avg_confidence,
                'detection_rate': detection_rate
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}
    
    def print_statistics(self):
        """Print statistics to console"""
        stats = self.get_statistics()
        
        if not stats:
            print("No statistics available")
            return
        
        print("\n=== Data Logger Statistics ===")
        print(f"Total log entries: {stats['total_rows']}")
        print(f"Total detections: {stats['total_detections']}")
        print(f"Average confidence: {stats['average_confidence']:.2%}")
        print(f"Detection rate: {stats['detection_rate']:.2%}")
        print("=" * 30 + "\n")
    
    def export_summary(self, output_file=None):
        """
        Export a summary report
        
        Args:
            output_file (str): Path to output summary file
        """
        if output_file is None:
            output_file = self.log_file_path.replace('.csv', '_summary.txt')
        
        try:
            stats = self.get_statistics()
            
            with open(output_file, 'w') as f:
                f.write("AMLAC Robot - Data Collection Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Log file: {self.log_file_path}\n\n")
                
                f.write("Statistics:\n")
                f.write(f"  Total log entries: {stats.get('total_rows', 0)}\n")
                f.write(f"  Total detections: {stats.get('total_detections', 0)}\n")
                f.write(f"  Average confidence: {stats.get('average_confidence', 0):.2%}\n")
                f.write(f"  Detection rate: {stats.get('detection_rate', 0):.2%}\n")
            
            print(f"Summary exported to: {output_file}")
            
        except Exception as e:
            print(f"Error exporting summary: {e}")
    
    def backup_log(self):
        """Create a backup of the current log file"""
        if not self.file_exists:
            print("No log file to backup")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.log_file_path.replace('.csv', f'_backup_{timestamp}.csv')
            
            import shutil
            shutil.copy2(self.log_file_path, backup_path)
            
            print(f"Log backed up to: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"Error backing up log: {e}")
            return None
    
    def clear_log(self, create_backup=True):
        """
        Clear the log file (optionally create backup first)
        
        Args:
            create_backup (bool): Whether to create backup before clearing
        """
        if create_backup:
            self.backup_log()
        
        try:
            self._create_log_file()
            print("Log file cleared")
        except Exception as e:
            print(f"Error clearing log: {e}")


if __name__ == "__main__":
    """Test data logger"""
    print("=== AMLAC Data Logger Test ===\n")
    
    # Use test log file
    test_log_path = '/home/pi/amlac_robot/test_log.csv'
    
    try:
        logger = DataLogger(log_file_path=test_log_path)
        
        print("Testing data logging...\n")
        
        # Test 1: Log detection events
        print("1. Logging detection events")
        for i in range(5):
            logger.log_detection(
                algae_detected=(i % 2 == 0),
                confidence=0.75 + (i * 0.05),
                gps_lat=14.5995 + (i * 0.0001),
                gps_lon=120.9842 + (i * 0.0001),
                weight_kg=1.5 + (i * 0.3),
                collection_count=i + 1,
                distance_cm=25.5 + (i * 2),
                orientation={'pitch': 2.5, 'roll': -1.2}
            )
        
        print()
        
        # Test 2: Log events
        print("2. Logging system events")
        logger.log_event('INFO', 'System started')
        logger.log_event('WARNING', 'Low battery detected')
        logger.log_event('ERROR', 'Sensor timeout')
        
        print()
        
        # Test 3: Get statistics
        print("3. Calculating statistics")
        logger.print_statistics()
        
        # Test 4: Export summary
        print("4. Exporting summary")
        logger.export_summary()
        
        print()
        
        # Test 5: Backup
        print("5. Creating backup")
        backup_path = logger.backup_log()
        
        print("\n✓ Data logger test complete!")
        print(f"Test log file: {test_log_path}")
        
        # Cleanup test files
        print("\nCleaning up test files...")
        import os
        if os.path.exists(test_log_path):
            os.remove(test_log_path)
            print(f"Removed: {test_log_path}")
        
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"Removed: {backup_path}")
        
        summary_file = test_log_path.replace('.csv', '_summary.txt')
        if os.path.exists(summary_file):
            os.remove(summary_file)
            print(f"Removed: {summary_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

