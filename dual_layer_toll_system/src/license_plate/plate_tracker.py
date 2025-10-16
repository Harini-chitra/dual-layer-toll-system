import cv2
import numpy as np
from collections import defaultdict, deque
from typing import Dict, List, Tuple

class PlateTracker:
    def __init__(self, max_disappeared=30, max_distance=100):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
    def register(self, centroid, plate_text=""):
        self.objects[self.next_object_id] = {
            'centroid': centroid,
            'plate_text': plate_text,
            'track_history': deque(maxlen=10),
            'confidence_history': deque(maxlen=5)
        }
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
        
    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]
        
    def update(self, detections):
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.get_tracked_objects()
            
        input_centroids = []
        plate_texts = []
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            cx = int(x + w / 2.0)
            cy = int(y + h / 2.0)
            input_centroids.append((cx, cy))
            plate_texts.append(detection.get('text', ''))
            
        if len(self.objects) == 0:
            for i, centroid in enumerate(input_centroids):
                self.register(centroid, plate_texts[i])
        else:
            object_centroids = [obj['centroid'] for obj in self.objects.values()]
            object_ids = list(self.objects.keys())
            
            # Compute distance matrix
            D = np.linalg.norm(np.array(object_centroids)[:, np.newaxis] - 
                             np.array(input_centroids), axis=2)
            
            # Assign object centroids to input centroids
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_row_indices = set()
            used_col_indices = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_row_indices or col in used_col_indices:
                    continue
                    
                if D[row, col] > self.max_distance:
                    continue
                    
                object_id = object_ids[row]
                self.objects[object_id]['centroid'] = input_centroids[col]
                self.objects[object_id]['track_history'].append(input_centroids[col])
                if plate_texts[col]:
                    self.objects[object_id]['plate_text'] = plate_texts[col]
                self.disappeared[object_id] = 0
                
                used_row_indices.add(row)
                used_col_indices.add(col)
                
        return self.get_tracked_objects()
        
    def get_tracked_objects(self):
        return {obj_id: obj for obj_id, obj in self.objects.items()}
