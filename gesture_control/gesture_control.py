import mediapipe as mp
import cv2
import time 
from basic_gesture_control import recognize_gesture
from command_manager import CommandManager

class MediapipeController:
    def __init__(self, tello):
        self.is_flying = False # statut du vol
        self.tello = tello
        self.command_manager = CommandManager(self.tello)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw= mp.solutions.drawing_utils
        self.last_gesture = None
        self.last_exec_time = 0
        self.gesture_cooldown = 2.0  # en secondes
        
    def detect_hand_landmarks_and_control_drone(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(image_rgb)
        
        if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    gesture = recognize_gesture(hand_landmarks.landmark)
                    cv2.putText(frame, f'Gesture: {gesture}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # éviter de spammer avec des gestes
                    self.command_manager.try_send_command(gesture)
    
        return bool(result.multi_hand_landmarks)
    
    def clean(self):
        self.hands.close()