#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path
import cv2
import numpy as np

sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        from src.integration.toll_system import DualLayerTollSystem
        print("✓ DualLayerTollSystem imported successfully")
        
        system = DualLayerTollSystem()
        print("✓ DualLayerTollSystem instance created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

class ImageWithFilename:
    """Wrapper to attach filename to image"""
    def __init__(self, image, filename):
        self._image = image
        self.filename = filename
        self.shape = image.shape
        self.dtype = image.dtype
    
    def copy(self):
        return ImageWithFilename(self._image.copy(), self.filename)
    
    def __array__(self):
        return self._image
    
    def __getattr__(self, name):
        return getattr(self._image, name)
    
    def __getitem__(self, key):
        return self._image[key]
    
    def __setitem__(self, key, value):
        self._image[key] = value

def main():
    parser = argparse.ArgumentParser(description='Dual-Layer Smart Toll System')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--test-images', action='store_true', help='Test with sample images')
    
    args = parser.parse_args()
    
    if not test_imports():
        return
    
    from src.integration.toll_system import DualLayerTollSystem
    try:
        from utils.image_utils import resize_image
    except:
        def resize_image(img):
            return img
    
    try:
        system = DualLayerTollSystem()
        
        if args.test_images:
            sample_dir = Path("data/sample_images")
            image_files = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
            
            print(f"Found {len(image_files)} sample images")
            
            for img_file in image_files:
                print(f"Processing {img_file.name}...")
                img = cv2.imread(str(img_file))
                if img is not None:
                    # Resize image
                    img = resize_image(img)
                    
                    # Create wrapper with filename
                    img_wrapper = ImageWithFilename(img, str(img_file))
                    
                    # Process frame
                    results = system.process_frame(img_wrapper)
                    
                    # Show result
                    cv2.imshow(f'Result - {img_file.name}', results['processed_frame'])
                    print(f"Decision: {results['system_decision']}")
                    if results['license_plates']:
                        for plate in results['license_plates']:
                            print(f"  Plate: {plate['text']} (confidence: {plate['confidence']:.2f})")
                    
                    # Wait for key press or auto-continue after 3 seconds
                    key = cv2.waitKey(3000) & 0xFF
                    if key == ord('q'):
                        break
                else:
                    print(f"Could not load {img_file.name}")
                    
            cv2.destroyAllWindows()
        else:
            system.run_camera_feed(args.camera)
            
    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
