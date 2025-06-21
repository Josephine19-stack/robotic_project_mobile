import time

import cv2
import mediapipe as mp

from gesture_control.utils.basic_gesture_control import recognize_gesture, recognize_gesture2
from gesture_control.command_manager import CommandManager

class MediapipeController:
    """
    This class detects hand gestures using MediaPipe and controls the Tello drone accordingly.  
    It supports both hardcoded rules and model-based gesture recognition, and manages gesture cooldowns to avoid command spamming.
    """
    def __init__(self, tello, model, hardcode=False):
        self.is_flying = False # flying status
        self.tello = tello
        self.command_manager = CommandManager(self.tello)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw= mp.solutions.drawing_utils
        self.last_gesture = None
        self.last_exec_time = 0
        self.gesture_cooldown = 2.0  #secondes
        self.model = model
        self.hardcode = hardcode # by default we do not use the hardcoded version
        
    def detect_hand_landmarks_and_control_drone(self, frame):
        frame = cv2.flip(frame, 1) # for mirror effect
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        
        gesture = None
        
        if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # === Recognition with model or hardcoded === 
                    if self.hardcode:
                        gesture = recognize_gesture(hand_landmarks.landmark)
                    else:
                        h, w = frame.shape[:2]
                        gesture = recognize_gesture2(self.model, hand_landmarks, h, w)
                    
                    cv2.putText(frame, f'Gesture: {gesture}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    # To make sure we do not spam the tello drone with too many gestures
                    self.command_manager.try_send_command(gesture)
                    
        return frame, bool(results.multi_hand_landmarks)
    
    def clean(self):
        self.hands.close()