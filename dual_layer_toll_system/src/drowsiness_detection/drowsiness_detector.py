# Drowsiness detector 
import cv2
import numpy as np
import logging
import time

class DrowsinessDetector:
    def __init__(self, config):
        self.config = config
        
        # Try to initialize face detection
        try:
            import dlib
            self.detector = dlib.get_frontal_face_detector()
            shape_predictor_path = getattr(config, 'SHAPE_PREDICTOR_PATH', 'models/shape_predictor_68_face_landmarks.dat')
            try:
                self.predictor = dlib.shape_predictor(shape_predictor_path)
                print("✓ Dlib facial landmark predictor loaded successfully")
            except:
                print("Warning: Could not load facial landmark predictor, using basic detection")
                self.predictor = None
        except ImportError:
            print("Warning: Dlib not available, using OpenCV for face detection")
            self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.predictor = None
        
        self.drowsy_frame_count = 0
        self.yawn_frame_count = 0
        self.last_alert_time = 0
        
        try:
            import pygame
            pygame.mixer.init()
            print("✓ Audio system initialized")
        except:
            print("Warning: Could not initialize audio system")
        
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_drowsiness(self, frame):
        """Main drowsiness detection function"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        drowsiness_status = {
            'drowsy': False,
            'yawning': False,
            'alert_triggered': False,
            'confidence': 0.0,
            'face_detected': False
        }
        
        try:
            # Detect faces
            if hasattr(self.detector, 'detectMultiScale'):  # OpenCV detector
                faces = self.detector.detectMultiScale(gray, 1.1, 4)
                drowsiness_status['face_detected'] = len(faces) > 0
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, "Face Detected", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    break
            else:  # Dlib detector
                faces = self.detector(gray)
                drowsiness_status['face_detected'] = len(faces) > 0
                
                for face in faces:
                    x, y, w, h = face.left(), face.top(), face.width(), face.height()
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, "Face Detected", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    break
            
            # Display face detection status
            face_status = "FACE DETECTED" if drowsiness_status['face_detected'] else "NO FACE"
            color = (0, 255, 0) if drowsiness_status['face_detected'] else (0, 0, 255)
            cv2.putText(frame, face_status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        except Exception as e:
            self.logger.error(f"Error in drowsiness detection: {e}")
        
        return drowsiness_status, frame
    
    def trigger_alert(self, status):
        """Trigger audio and visual alerts"""
        try:
            print("\a", end="")  # System beep
        except:
            pass
        
        self.logger.warning(f"Alert triggered - Drowsy: {status['drowsy']}, Yawning: {status['yawning']}")
