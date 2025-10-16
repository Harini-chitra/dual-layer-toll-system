import cv2
import numpy as np
import time
import logging
from datetime import datetime
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from src.license_plate.plate_recognizer import LicensePlateRecognizer
except ImportError:
    print("Warning: Could not import LicensePlateRecognizer")
    LicensePlateRecognizer = None

try:
    from src.drowsiness_detection.drowsiness_detector import DrowsinessDetector
except ImportError:
    print("Warning: Could not import DrowsinessDetector")
    DrowsinessDetector = None

try:
    from config.config import Config
except ImportError:
    print("Warning: Could not import Config, using default settings")
    Config = None

class DualLayerTollSystem:
    def __init__(self):
        # Initialize config with fallback
        if Config:
            self.config = Config()
        else:
            self.config = self.get_default_config()
            
        # Initialize components with error handling
        if LicensePlateRecognizer:
            self.plate_recognizer = LicensePlateRecognizer(self.config)
        else:
            self.plate_recognizer = self.get_dummy_plate_recognizer()
            
        if DrowsinessDetector:
            self.drowsiness_detector = DrowsinessDetector(self.config)
        else:
            self.drowsiness_detector = self.get_dummy_drowsiness_detector()
            
        self.setup_logging()
        
        # System state
        self.current_session = {
            'plate_detected': False,
            'plate_text': '',
            'is_authorized': False,
            'driver_safe': True,
            'violation_count': 0,
            'session_start': None
        }
    
    def get_default_config(self):
        """Fallback configuration if config file is missing"""
        class DefaultConfig:
            FRAME_WIDTH = 640
            FRAME_HEIGHT = 480
            AUTHORIZED_PLATES_DB = 'data/authorized_plates.txt'
            VIOLATION_LOG = 'logs/violations.log'
        return DefaultConfig()
    
    def get_dummy_plate_recognizer(self):
        """Dummy plate recognizer for testing"""
        class DummyPlateRecognizer:
            def detect_and_recognize(self, frame):
                return [], self._get_frame_array(frame)
            def verify_authorized_plate(self, plate_text):
                return True
        return DummyPlateRecognizer()
    
    def get_dummy_drowsiness_detector(self):
        """Dummy drowsiness detector for testing"""
        class DummyDrowsinessDetector:
            def detect_drowsiness(self, frame):
                status = {
                    'drowsy': False,
                    'yawning': False,
                    'alert_triggered': False,
                    'confidence': 0.0,
                    'face_detected': False
                }
                return status, self._get_frame_array(frame)
        return DummyDrowsinessDetector()
    
    def _get_frame_array(self, frame):
        """Extract numpy array from frame (handles both regular arrays and wrapper objects)"""
        if hasattr(frame, '_image'):
            return frame._image
        elif hasattr(frame, 'copy'):
            return frame.copy()
        else:
            return frame
    
    def setup_logging(self):
        """Setup logging system"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/toll_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_frame(self, frame):
        """Process a single frame through both detection systems"""
        # Get the actual numpy array from frame
        frame_array = self._get_frame_array(frame)
        
        results = {
            'license_plates': [],
            'drowsiness_status': {},
            'system_decision': 'PENDING',
            'processed_frame': frame_array.copy()
        }
        
        try:
            # 1. License Plate Recognition (pass original frame with filename info)
            plates, plate_frame = self.plate_recognizer.detect_and_recognize(frame)
            results['license_plates'] = plates
            results['processed_frame'] = plate_frame
            
            # 2. Drowsiness Detection (use the processed frame from plate recognition)
            drowsiness_status, final_frame = self.drowsiness_detector.detect_drowsiness(plate_frame)
            results['drowsiness_status'] = drowsiness_status
            results['processed_frame'] = final_frame
            
            # 3. Make system decision
            results['system_decision'] = self.make_toll_decision(plates, drowsiness_status)
            
            # 4. Update session state
            self.update_session_state(plates, drowsiness_status)
            
            # 5. Draw system status
            self.draw_system_status(results['processed_frame'], results)
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            results['system_decision'] = 'ERROR'
            # Add error message to frame
            try:
                cv2.putText(results['processed_frame'], f"ERROR: {str(e)[:50]}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            except:
                pass
        
        return results
    
    def make_toll_decision(self, plates, drowsiness_status):
        """Make decision based on both systems"""
        if not plates:
            return "NO_PLATE_DETECTED"
        
        # Check if any plate is authorized
        authorized_plate_found = False
        for plate in plates:
            if self.plate_recognizer.verify_authorized_plate(plate['text']):
                authorized_plate_found = True
                break
        
        if not authorized_plate_found:
            self.log_violation("UNAUTHORIZED_PLATE", plates[0]['text'] if plates else "UNKNOWN")
            return "ACCESS_DENIED"
        
        # Check driver safety
        if drowsiness_status.get('drowsy', False) or drowsiness_status.get('yawning', False):
            self.log_violation("UNSAFE_DRIVER", plates[0]['text'])
            return "SAFETY_VIOLATION"
        
        return "ACCESS_GRANTED"
    
    def update_session_state(self, plates, drowsiness_status):
        """Update the current session state"""
        if plates:
            self.current_session['plate_detected'] = True
            self.current_session['plate_text'] = plates[0]['text']
            self.current_session['is_authorized'] = self.plate_recognizer.verify_authorized_plate(plates[0]['text'])
        
        self.current_session['driver_safe'] = not (
            drowsiness_status.get('drowsy', False) or 
            drowsiness_status.get('yawning', False)
        )
        
        if not self.current_session['driver_safe']:
            self.current_session['violation_count'] += 1
    
    def draw_system_status(self, frame, results):
        """Draw comprehensive system status on frame"""
        try:
            # Ensure frame is a numpy array
            if not isinstance(frame, np.ndarray):
                return
                
            # Background for status
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, frame.shape[0] - 150), (400, frame.shape[0] - 10), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # System decision
            decision = results['system_decision']
            color = (0, 255, 0) if decision == "ACCESS_GRANTED" else (0, 0, 255)
            cv2.putText(frame, f"Decision: {decision}", (15, frame.shape[0] - 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Plate info
            if results['license_plates']:
                plate_text = results['license_plates'][0]['text']
                cv2.putText(frame, f"Plate: {plate_text}", (15, frame.shape[0] - 95), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Safety status
            safety_status = "SAFE" if self.current_session['driver_safe'] else "UNSAFE"
            safety_color = (0, 255, 0) if self.current_session['driver_safe'] else (0, 0, 255)
            cv2.putText(frame, f"Driver: {safety_status}", (15, frame.shape[0] - 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, safety_color, 2)
            
            # Violation count
            cv2.putText(frame, f"Violations: {self.current_session['violation_count']}", 
                       (15, frame.shape[0] - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (15, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Face detection status
            if results['drowsiness_status'].get('face_detected', False):
                cv2.putText(frame, "Face: DETECTED", (420, frame.shape[0] - 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            else:
                cv2.putText(frame, "Face: NOT DETECTED", (420, frame.shape[0] - 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                       
        except Exception as e:
            self.logger.error(f"Error drawing status: {e}")
    
    def log_violation(self, violation_type, plate_text="UNKNOWN"):
        """Log violations to file"""
        try:
            violation_entry = {
                'timestamp': datetime.now().isoformat(),
                'violation_type': violation_type,
                'plate': plate_text,
                'session_id': id(self.current_session)
            }
            
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            with open(getattr(self.config, 'VIOLATION_LOG', 'logs/violations.log'), 'a') as f:
                f.write(f"{violation_entry}\n")
            
            self.logger.warning(f"Violation logged: {violation_entry}")
            
        except Exception as e:
            self.logger.error(f"Error logging violation: {e}")
    
    def run_camera_feed(self, camera_index=0):
        """Run the system with live camera feed"""
        try:
            cap = cv2.VideoCapture(camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, getattr(self.config, 'FRAME_WIDTH', 640))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, getattr(self.config, 'FRAME_HEIGHT', 480))
            
            self.logger.info("Starting Dual-Layer Toll System...")
            print("\n=== CAMERA CONTROLS ===")
            print("Press 'q' to quit")
            print("Press 'r' to reset session")
            print("Press 's' to save current frame")
            print("========================\n")
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame from camera")
                    break
                
                frame_count += 1
                
                # Process frame
                results = self.process_frame(frame)
                
                # Display result
                cv2.imshow('Dual-Layer Smart Toll System', results['processed_frame'])
                
                # Key controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Exiting system...")
                    break
                elif key == ord('r'):  # Reset session
                    self.current_session = {
                        'plate_detected': False,
                        'plate_text': '',
                        'is_authorized': False,
                        'driver_safe': True,
                        'violation_count': 0,
                        'session_start': time.time()
                    }
                    print("Session reset")
                elif key == ord('s'):  # Save frame
                    os.makedirs('output', exist_ok=True)
                    filename = f"output/capture_{frame_count:04d}.jpg"
                    cv2.imwrite(filename, results['processed_frame'])
                    print(f"Frame saved: {filename}")
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            self.logger.error(f"Error in camera feed: {e}")
            print(f"Camera feed error: {e}")

# Test if this file can be imported properly
if __name__ == "__main__":
    print("Testing DualLayerTollSystem import...")
    try:
        system = DualLayerTollSystem()
        print("✓ DualLayerTollSystem created successfully!")
        
        # Test with a dummy frame
        import numpy as np
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = system.process_frame(test_frame)
        print(f"✓ Frame processing test: {results['system_decision']}")
        
    except Exception as e:
        print(f"✗ Error creating DualLayerTollSystem: {e}")
        import traceback
        traceback.print_exc()
