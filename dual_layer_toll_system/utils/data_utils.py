# dual_layer_toll_system/utils/data_utils.py
import cv2
import numpy as np
import os
from pathlib import Path

def load_sample_images():
    """Load sample images for testing"""
    sample_dir = Path("data/sample_images")
    image_files = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
    
    images = []
    for img_file in image_files:
        img = cv2.imread(str(img_file))
        if img is not None:
            images.append((str(img_file), img))
    
    return images

def create_alert_sound():
    """Create a simple alert sound file"""
    try:
        import numpy as np
        from scipy.io.wavfile import write
        
        # Generate a simple beep sound
        sample_rate = 44100
        duration = 1.0  # seconds
        frequency = 800  # Hz
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.5
        
        # Convert to 16-bit integers
        audio_data = (audio_data * 32767).astype(np.int16)
        
        write("data/alert_sound.wav", sample_rate, audio_data)
        print("Alert sound created successfully!")
        
    except ImportError:
        print("scipy not available, skipping alert sound creation")

def resize_image(image, max_width=800, max_height=600):
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if width > max_width or height > max_height:
        # Calculate the scaling factor
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height))
    
    return image
