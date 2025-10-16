class CameraConfig:
    # Default camera settings
    DEFAULT_CAMERA_INDEX = 0
    BACKUP_CAMERA_INDEX = 1
    
    # Video capture settings
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30
    
    # Camera properties
    BRIGHTNESS = 0.5
    CONTRAST = 0.5
    SATURATION = 0.5
    
    # Processing settings
    SKIP_FRAMES = 2  # Process every nth frame for performance
    MAX_PROCESSING_TIME = 0.1  # Maximum time per frame in seconds
    
    # Auto-adjustment settings
    AUTO_EXPOSURE = True
    AUTO_WHITE_BALANCE = True
    
    # Recording settings (optional)
    ENABLE_RECORDING = False
    RECORDING_FORMAT = 'mp4v'
    RECORDING_QUALITY = 0.8
    
    # Multiple camera support
    CAMERA_POSITIONS = {
        0: "ENTRY_GATE",
        1: "EXIT_GATE", 
        2: "BACKUP_CAMERA"
    }
    
    # Image quality settings
    IMAGE_QUALITY = 95  # JPEG quality for saved images
    SAVE_DETECTION_IMAGES = True
    DETECTION_IMAGES_DIR = "output/detections"
