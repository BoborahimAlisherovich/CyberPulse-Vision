import cv2
import mediapipe as mp
import numpy as np
import time
import math
import os
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Fixed hand connections since mp.solutions is deprecated in python 3.13
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (5, 6), (6, 7), (7, 8),
    (9, 10), (10, 11), (11, 12),
    (13, 14), (14, 15), (15, 16),
    (17, 18), (18, 19), (19, 20),
    (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)
]

class HandTracker:
    def __init__(self, max_hands=2, detection_con=0.5, track_con=0.5):
        # 1. Download model file for MediaPipe Tasks API natively
        self.model_path = 'hand_landmarker.task'
        if not os.path.exists(self.model_path):
            print("Downloading AI Hand Landmarker Model. Please wait...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            urllib.request.urlretrieve(url, self.model_path)
            print("Download Complete!")

        # 2. Setup Options for real-time webcam inference
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO, # optimized for video
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=track_con,
            min_tracking_confidence=track_con
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.tip_ids = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky
        
    def find_hands(self, img, timestamp_ms):
        # Execute detection
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Must pass monotonically increasing timestamp for VIDEO mode
        self.results = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        all_hands = []
        if self.results.hand_landmarks:
            for hand_landmarks, handedness in zip(self.results.hand_landmarks, self.results.handedness):
                my_hand = {}
                mylm_list = []
                # MediaPipe tasks returns normalized landmarks
                for id, lm in enumerate(hand_landmarks):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    mylm_list.append([cx, cy])
                    
                my_hand["lmList"] = mylm_list
                # category_name typically returns "Left" or "Right"
                my_hand["type"] = handedness[0].category_name
                all_hands.append(my_hand)
        return all_hands

    def fingers_up(self, hand):
        lmList = hand["lmList"]
        hand_type = hand["type"]
        fingers = []
        
        # Thumb: left vs right logic logic is often inverted after cvFlip 
        if hand_type == "Right":
            if lmList[self.tip_ids[0]][0] > lmList[self.tip_ids[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if lmList[self.tip_ids[0]][0] < lmList[self.tip_ids[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        # 4 Fingers
        for id in range(1, 5):
            if lmList[self.tip_ids[id]][1] < lmList[self.tip_ids[id] - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers

def create_neon_effect(img, hands, connections, time_val):
    # 1. Create a black canvas for the neon bloom/glow
    glow_canvas = np.zeros_like(img)
    
    # 2. Generate dynamic colors using time
    hue1 = int((time_val * 80) % 180) # Primary color
    color1 = cv2.cvtColor(np.uint8([[[hue1, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
    color1 = (int(color1[0]), int(color1[1]), int(color1[2]))
    
    hue2 = int(((time_val * 80) + 90) % 180) # Secondary/Complementary color
    color2 = cv2.cvtColor(np.uint8([[[hue2, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
    color2 = (int(color2[0]), int(color2[1]), int(color2[2]))
    
    # 3. Draw connections (lines and dots) on the canvas with thick bright colors
    for i, hand in enumerate(hands):
        color = color1 if i == 0 else color2
        lmList = hand["lmList"]
        
        if connections:
            for connection in connections:
                idx1, idx2 = connection
                pt1, pt2 = tuple(lmList[idx1]), tuple(lmList[idx2])
                cv2.line(glow_canvas, pt1, pt2, color, thickness=12) # Thick line for glow
                    
        for pt in lmList:
            cv2.circle(glow_canvas, tuple(pt), 14, color, -1)
            
    # 4. Connect both hands if two are detected (AR visual effect)
    if len(hands) == 2:
        lmList1 = hands[0]["lmList"]
        lmList2 = hands[1]["lmList"]
        
        tip_ids = [4, 8, 12, 16, 20]
        for tip in tip_ids:
            pt1 = tuple(lmList1[tip])
            pt2 = tuple(lmList2[tip])
            
            # Glowing pulsating line between corresponding fingers
            pulse = (math.sin(time_val * 6) + 1) / 2 # range 0 to 1
            dynamic_thickness = int(4 + 10 * pulse)
            
            # Create a third color for links
            hue_link = int(((time_val * 100) + 45) % 180)
            color_link = cv2.cvtColor(np.uint8([[[hue_link, 200, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
            color_link = (int(color_link[0]), int(color_link[1]), int(color_link[2]))
            
            cv2.line(glow_canvas, pt1, pt2, color_link, thickness=dynamic_thickness)

    # 5. Apply severe Gaussian blur to create the bloom effect
    glow_canvas = cv2.GaussianBlur(glow_canvas, (35, 35), 0)
    
    # 6. Blend the glow canvas onto the original webcam frame
    result = cv2.addWeighted(img, 1.0, glow_canvas, 0.9, 0)
    
    # 7. Draw the inner bright core on top for the realistic neon tube look
    for i, hand in enumerate(hands):
        lmList = hand["lmList"]
        if connections:
            for connection in connections:
                idx1, idx2 = connection
                pt1, pt2 = tuple(lmList[idx1]), tuple(lmList[idx2])
                cv2.line(result, pt1, pt2, (255, 255, 255), thickness=2)
                
        for pt in lmList:
            cv2.circle(result, tuple(pt), 4, (255, 255, 255), -1)
            
    if len(hands) == 2:
        for tip in [4, 8, 12, 16, 20]:
            pt1, pt2 = tuple(hands[0]["lmList"][tip]), tuple(hands[1]["lmList"][tip])
            cv2.line(result, pt1, pt2, (255, 255, 255), thickness=1)

    return result

def main():
    print("Starting AR Neon Hand Tracker...")
    print("Press 'q' in the window to exit.")
    
    cap = cv2.VideoCapture(0)
    
    # Setting up high resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    tracker = HandTracker(max_hands=2)
    
    pTime = 0
    start_time = time.time()
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image or camera disconnected.")
            break
            
        # Selfie view
        img = cv2.flip(img, 1)
        
        current_time = time.time() - start_time
        timestamp_ms = int(current_time * 1000)
        
        # We need to skip frame 0 if timestamp=0 because it errors sometimes
        if timestamp_ms == 0:
            timestamp_ms = 1
            
        hands = tracker.find_hands(img, timestamp_ms)
        
        if hands:
            # Add neon drawing over hands
            img = create_neon_effect(img, hands, HAND_CONNECTIONS, current_time)
            
            # Gesture text positioning logic
            for i, hand in enumerate(hands):
                fingers = tracker.fingers_up(hand)
                open_fingers = sum(fingers)
                
                gesture = f"[{hand['type']}] "
                if open_fingers == 0:
                    gesture += "FIST"
                elif open_fingers == 5:
                    gesture += "OPEN HAND"
                elif open_fingers == 2 and fingers[1] == 1 and fingers[2] == 1:
                    gesture += "PEACE"
                else:
                    gesture += f"FINGERS: {open_fingers}"
                
                # Get the wrist coordinate to float the text near hand
                wrist_x, wrist_y = hand["lmList"][0]
                text_y = max(50, wrist_y - 50)
                
                # Double draw for a beautiful outlined text effect
                cv2.putText(img, gesture, (wrist_x, text_y), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 3)
                cv2.putText(img, gesture, (wrist_x, text_y), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 1)

        # UI Overlay (Dark translucent background for metrics)
        overlay = img.copy()
        cv2.rectangle(overlay, (10, 10), (320, 100), (0, 0, 0), -1)
        img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)
        
        # Calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        
        # Text Overlay
        cv2.putText(img, f"FPS: {int(fps)}", (25, 45), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 1)
        cv2.putText(img, f"HANDS: {len(hands)}", (25, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 1)
        
        cv2.imshow("AR Neon Hand Tracker", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
