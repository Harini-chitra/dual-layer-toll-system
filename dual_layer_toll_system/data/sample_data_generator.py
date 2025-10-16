import cv2
import numpy as np
import os
from pathlib import Path
import json

class SampleDataGenerator:
    def __init__(self):
        self.data_dir = Path("data")
        self.sample_images_dir = self.data_dir / "sample_images"
        self.sample_images_dir.mkdir(parents=True, exist_ok=True)
    
    def create_sample_authorized_plates(self):
        """Create sample authorized plates database"""
        sample_plates = [
            "MH01AB1234", "DL02CD5678", "KA03EF9012", 
            "TN04GH3456", "UP05IJ7890", "WB06KL2468",
            "GJ07MN1357", "RJ08PQ9753", "MP09RS8642",
            "HR10TU5319"
        ]
        
        authorized_file = self.data_dir / "authorized_plates.txt"
        with open(authorized_file, 'w') as f:
            for plate in sample_plates:
                f.write(f"{plate}\n")
        
        print(f"Created authorized plates database with {len(sample_plates)} entries")
    
    def create_vehicle_database(self):
        """Create sample vehicle information database"""
        vehicles_data = []
        plate_types = ["CAR", "TRUCK", "BUS", "BIKE"]
        
        for i, plate in enumerate(["MH01AB1234", "DL02CD5678", "KA03EF9012", "TN04GH3456", "UP05IJ7890"]):
            vehicle_info = {
                "plate_number": plate,
                "owner_name": f"Owner_{i+1}",
                "vehicle_type": plate_types[i % len(plate_types)],
                "registration_date": f"2023-{(i%12)+1:02d}-01",
                "expiry_date": f"2028-{(i%12)+1:02d}-01",
                "is_active": True
            }
            vehicles_data.append(vehicle_info)
        
        vehicles_file = self.data_dir / "vehicles_database.json"
        with open(vehicles_file, 'w') as f:
            json.dump(vehicles_data, f, indent=2)
        
        print(f"Created vehicle database with {len(vehicles_data)} entries")
    
    def create_toll_rates_config(self):
        """Create toll rates configuration"""
        toll_rates = {
            "CAR": 50,
            "TRUCK": 120,
            "BUS": 80,
            "BIKE": 20,
            "HEAVY_VEHICLE": 150,
            "EMERGENCY": 0
        }
        
        rates_file = self.data_dir / "toll_rates.json"
        with open(rates_file, 'w') as f:
            json.dump(toll_rates, f, indent=2)
        
        print("Created toll rates configuration")
    
    def generate_synthetic_plate_image(self, plate_text, output_path):
        """Generate a synthetic license plate image for testing"""
        # Create a blank image (license plate dimensions)
        img = np.ones((60, 200, 3), dtype=np.uint8) * 255
        
        # Draw border
        cv2.rectangle(img, (2, 2), (197, 57), (0, 0, 0), 2)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        thickness = 2
        
        # Calculate text size and position
        text_size = cv2.getTextSize(plate_text, font, font_scale, thickness)[0]
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = (img.shape[0] + text_size[1]) // 2
        
        # Draw text
        cv2.putText(img, plate_text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)
        
        # Save image
        cv2.imwrite(str(output_path), img)
        return img
    
    def create_sample_plate_images(self):
        """Create sample license plate images"""
        sample_plates = ["MH01AB1234", "DL02CD5678", "KA03EF9012", "TN04GH3456", "UP05IJ7890"]
        
        for plate in sample_plates:
            output_path = self.sample_images_dir / f"{plate}.jpg"
            self.generate_synthetic_plate_image(plate, output_path)
        
        print(f"Generated {len(sample_plates)} sample plate images")
    
    def create_alert_sound(self):
        """Create a simple alert sound using numpy"""
        try:
            import numpy as np
            from scipy.io.wavfile import write
            
            # Generate a simple beep sound
            sample_rate = 44100
            duration = 1.0
            frequency = 800
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.5
            
            # Convert to 16-bit integers
            audio_data = (audio_data * 32767).astype(np.int16)
            
            alert_file = self.data_dir / "alert_sound.wav"
            write(str(alert_file), sample_rate, audio_data)
            print("Created alert sound file")
            
        except ImportError:
            print("scipy not available, creating placeholder alert file")
            alert_file = self.data_dir / "alert_sound.wav"
            alert_file.touch()
    
    def generate_all_sample_data(self):
        """Generate all sample data"""
        print("Generating sample data...")
        
        self.create_sample_authorized_plates()
        self.create_vehicle_database() 
        self.create_toll_rates_config()
        self.create_sample_plate_images()
        self.create_alert_sound()
        
        print("Sample data generation completed!")
