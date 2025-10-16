# Image utils 
import cv2
import numpy as np
from pathlib import Path

def resize_image(image, max_width=800, max_height=600):
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if width > max_width or height > max_height:
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(image, (new_width, new_height))
    
    return image
