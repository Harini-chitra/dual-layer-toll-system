#!/usr/bin/env python3
import sys
import os
import time
import cv2
import numpy as np
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

from src.integration.toll_system import DualLayerTollSystem

class SimpleTollSystem:
    def __init__(self):
        self.system = DualLayerTollSystem()
        self.driver_safe = True
        
    def run_toll_booth(self, camera_index=0):
        """Run the simplified toll booth system"""
        
        # Test camera first
        print("🔍 Testing camera connection...")
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("❌ Error: Could not open camera. Please check camera connection.")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("\n" + "="*60)
        print("🚗 SMART TOLL BOOTH SYSTEM 🚗")
        print("="*60)
        print("\n📋 PROCESS:")
        print("1. FACE CHECK (3 seconds)")
        print("2. LICENSE PLATE SCAN")
        print("3. ACCESS DECISION")
        print("\nPress 'q' to quit anytime")
        print("="*60 + "\n")
        
        try:
            # STEP 1: Face Detection
            self.step1_face_check(cap)
            
            if self.driver_safe:
                # STEP 2: License Plate Detection
                self.step2_plate_scan(cap)
            
        except KeyboardInterrupt:
            print("\n👋 System stopped by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def step1_face_check(self, cap):
        """Step 1: Face and drowsiness detection"""
        print("👤 STEP 1: FACE & DROWSINESS CHECK")
        print("Look at the camera. Close your eyes to test drowsiness detection.")
        print("Analysis will run for 3 seconds...\n")
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        start_time = time.time()
        analysis_duration = 3.0
        eye_closure_count = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Camera error")
                break
            
            frame_count += 1
            elapsed = time.time() - start_time
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw progress
            progress = min(elapsed / analysis_duration, 1.0)
            cv2.rectangle(frame, (50, 50), (590, 100), (0, 0, 0), -1)
            cv2.rectangle(frame, (60, 60), (60 + int(520 * progress), 80), (0, 255, 0), -1)
            cv2.putText(frame, f"Face Analysis: {elapsed:.1f}s / {analysis_duration}s", 
                       (60, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Face detection
            if len(faces) > 0:
                face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Eye detection
                face_roi_gray = gray[y:y+h, x:x+w]
                face_roi_color = frame[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(face_roi_gray, 1.1, 3)
                
                if len(eyes) >= 2:
                    cv2.putText(frame, "👀 Eyes: OPEN", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(face_roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                elif len(eyes) == 1:
                    cv2.putText(frame, "😑 Eyes: PARTIAL", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    eye_closure_count += 1
                else:
                    cv2.putText(frame, "😴 Eyes: CLOSED", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    eye_closure_count += 1
                
                cv2.putText(frame, "Face Detected", (x, y+h+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            else:
                cv2.putText(frame, "❌ No Face Detected", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Instructions
            cv2.putText(frame, "Look at camera - Close eyes to test drowsiness", 
                       (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Show frame
            cv2.imshow('🚗 Toll System - Face Check', frame)
            
            # Check for quit
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                raise KeyboardInterrupt
            
            # Complete analysis
            if elapsed >= analysis_duration:
                break
        
        # Analysis results
        drowsiness_ratio = eye_closure_count / max(frame_count, 1)
        
        cv2.destroyAllWindows()
        
        print(f"\n📊 FACE ANALYSIS RESULTS:")
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Eye closure ratio: {drowsiness_ratio:.2f}")
        
        if drowsiness_ratio > 0.3:  # 30% of frames with closed/partial eyes
            print("😴 RESULT: DRIVER APPEARS DROWSY")
            print("⚠️  SAFETY VIOLATION - Access will be denied")
            self.driver_safe = False
            
            # Show violation message
            self.show_violation_screen("DROWSY DRIVER DETECTED")
        else:
            print("😊 RESULT: DRIVER IS ALERT")
            print("✅ Proceeding to license plate scan...")
            self.driver_safe = True
            time.sleep(2)
    
    def step2_plate_scan(self, cap):
        """Step 2: License plate detection"""
        print("\n🔍 STEP 2: LICENSE PLATE SCAN")
        print("Hold your license plate clearly in front of the camera...")
        print("Detection will stop automatically when plate is found.\n")
        
        detection_count = 0
        required_detections = 2
        detected_plate = None
        
        while detection_count < required_detections:
            ret, frame = cap.read()
            if not ret:
                print("❌ Camera error")
                break
            
            # Detect license plate
            plates, processed_frame = self.system.plate_recognizer.detect_and_recognize(frame)
            
            # Draw instructions
            cv2.putText(processed_frame, f"License Plate Detection: {detection_count}/{required_detections}", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(processed_frame, "Hold license plate clearly in view", 
                       (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            if plates:
                plate = plates[0]
                detected_plate = plate
                detection_count += 1
                print(f"📋 Plate detected: {plate['text']} ({detection_count}/{required_detections})")
                
                # Visual confirmation
                cv2.putText(processed_frame, f"DETECTED: {plate['text']}", 
                           (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                
                # Pause to show detection
                cv2.imshow('🚗 Toll System - Plate Scan', processed_frame)
                cv2.waitKey(1000)  # Show for 1 second
            else:
                cv2.putText(processed_frame, "No plate detected", 
                           (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            cv2.imshow('🚗 Toll System - Plate Scan', processed_frame)
            
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                raise KeyboardInterrupt
        
        cv2.destroyAllWindows()
        
        # Final decision
        if detected_plate:
            self.step3_final_decision(detected_plate)
        else:
            print("❌ No license plate detected. Access denied.")
    
    def step3_final_decision(self, detected_plate):
        """Step 3: Make final access decision"""
        print(f"\n⚖️  STEP 3: FINAL DECISION")
        
        plate_text = detected_plate['text']
        is_authorized = self.system.plate_recognizer.verify_authorized_plate(plate_text)
        
        print(f"📋 License Plate: {plate_text}")
        print(f"🔐 Authorization: {'✅ AUTHORIZED' if is_authorized else '❌ UNAUTHORIZED'}")
        print(f"😊 Driver Safety: {'✅ SAFE' if self.driver_safe else '❌ UNSAFE'}")
        
        if is_authorized and self.driver_safe:
            print(f"\n🎉 ACCESS GRANTED!")
            print(f"✅ Welcome! Toll amount: ₹50")
            print(f"🚗 You may proceed. Have a safe journey!")
            
            self.show_success_screen(plate_text)
            
        elif not is_authorized:
            print(f"\n🚫 ACCESS DENIED!")
            print(f"❌ License plate not authorized")
            self.show_violation_screen(f"UNAUTHORIZED PLATE: {plate_text}")
            
        else:
            print(f"\n⚠️  SAFETY VIOLATION!")
            print(f"😴 Driver unsafe to proceed")
            self.show_violation_screen("UNSAFE DRIVER")
    
    def show_success_screen(self, plate_text):
        """Show success screen"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (0, 100, 0)  # Green background
        
        cv2.putText(img, "ACCESS GRANTED", (150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, f"Plate: {plate_text}", (200, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Toll: Rs. 50", (250, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Have a safe journey!", (180, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow('🚗 Toll System - Result', img)
        cv2.waitKey(3000)  # Show for 3 seconds
        cv2.destroyAllWindows()
    
    def show_violation_screen(self, message):
        """Show violation screen"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (0, 0, 100)  # Red background
        
        cv2.putText(img, "ACCESS DENIED", (150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, message, (50, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, "Contact Administration", (150, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow('🚗 Toll System - Result', img)
        cv2.waitKey(3000)  # Show for 3 seconds
        cv2.destroyAllWindows()

def main():
    try:
        print("🚗 Starting Smart Toll Booth System...")
        toll_system = SimpleTollSystem()
        toll_system.run_toll_booth(0)
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
