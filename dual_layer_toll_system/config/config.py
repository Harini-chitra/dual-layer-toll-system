# Config file 
# Configuration file for Dual-Layer Smart Toll System

class Config:
    # License Plate Recognition Settings
    LICENSE_PLATE_CONFIDENCE_THRESHOLD = 0.7
    OCR_CONFIDENCE_THRESHOLD = 60
    PLATE_MIN_WIDTH = 50  
    PLATE_MIN_HEIGHT = 20
    PLATE_MAX_WIDTH = 400
    PLATE_MAX_HEIGHT = 200
    
    # Drowsiness Detection Settings
    EAR_THRESHOLD = 0.25
    MAR_THRESHOLD = 0.7
    CONSECUTIVE_FRAMES_THRESHOLD = 20
    YAWN_FRAMES_THRESHOLD = 15
    
    # Facial landmark detection
    SHAPE_PREDICTOR_PATH = "models/shape_predictor_68_face_landmarks.dat"
    
    # Eye landmark indices
    LEFT_EYE_START = 36
    LEFT_EYE_END = 41
    RIGHT_EYE_START = 42
    RIGHT_EYE_END = 47
    
    # Mouth landmark indices
    MOUTH_START = 48
    MOUTH_END = 67
    
    # Alert settings
    ENABLE_AUDIO_ALERTS = True
    ENABLE_VISUAL_ALERTS = True
    ALERT_SOUND_PATH = "data/alert_sound.wav"
    
    # Video processing
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30
    
    # File paths
    OUTPUT_DIR = "output/"
    LOG_DIR = "logs/"
    
    # Database settings
    AUTHORIZED_PLATES_DB = "data/authorized_plates.txt"
    VIOLATION_LOG = "logs/violations.log"
    
    # Toll rates
    TOLL_RATES = {
        "CAR": 50,
        "TRUCK": 100,
        "BUS": 75,
        "BIKE": 25
    }
