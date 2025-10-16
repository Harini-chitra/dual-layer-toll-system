import os
import urllib.request
import bz2
import gzip
from pathlib import Path
import hashlib

class ModelDownloader:
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.model_urls = {
            'shape_predictor_68_face_landmarks.dat': {
                'url': 'https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2',
                'compressed': True,
                'compression': 'bz2',
                'size_mb': 99.7
            },
            'haarcascade_frontalface_default.xml': {
                'url': 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml',
                'compressed': False,
                'size_mb': 0.9
            }
        }
    
    def download_model(self, model_name):
        if model_name not in self.model_urls:
            print(f"Unknown model: {model_name}")
            return False
            
        model_info = self.model_urls[model_name]
        model_path = self.models_dir / model_name
        
        if model_path.exists():
            print(f"Model {model_name} already exists")
            return True
            
        try:
            print(f"Downloading {model_name} ({model_info['size_mb']} MB)...")
            
            if model_info['compressed']:
                compressed_path = model_path.with_suffix(model_path.suffix + f".{model_info['compression']}")
                urllib.request.urlretrieve(model_info['url'], compressed_path)
                
                # Decompress
                if model_info['compression'] == 'bz2':
                    with bz2.BZ2File(compressed_path, 'rb') as f_in:
                        with open(model_path, 'wb') as f_out:
                            f_out.write(f_in.read())
                elif model_info['compression'] == 'gz':
                    with gzip.open(compressed_path, 'rb') as f_in:
                        with open(model_path, 'wb') as f_out:
                            f_out.write(f_in.read())
                
                compressed_path.unlink()  # Remove compressed file
            else:
                urllib.request.urlretrieve(model_info['url'], model_path)
                
            print(f"Successfully downloaded {model_name}")
            return True
            
        except Exception as e:
            print(f"Error downloading {model_name}: {e}")
            return False
    
    def download_all_models(self):
        success_count = 0
        for model_name in self.model_urls:
            if self.download_model(model_name):
                success_count += 1
        
        print(f"Downloaded {success_count}/{len(self.model_urls)} models successfully")
        return success_count == len(self.model_urls)
