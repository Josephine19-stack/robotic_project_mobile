import mediapipe as mp
import cv2
import time 
from gesture_control.utils.basic_gesture_control import recognize_gesture, recognize_gesture2
from gesture_control.command_manager import CommandManager

class MediapipeController:
    def __init__(self, tello, model):
        self.is_flying = False # statut du vol
        self.tello = tello
        self.command_manager = CommandManager(self.tello)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw= mp.solutions.drawing_utils
        self.last_gesture = None
        self.last_exec_time = 0
        self.gesture_cooldown = 2.0  # en secondes
        self.model = model
        
    def detect_hand_landmarks_and_control_drone(self, frame):
        frame = cv2.flip(frame, 1) # pour effet miroir
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    #gesture = recognize_gesture(hand_landmarks.landmark)
                    h, w = frame.shape[:2]
                    gesture = recognize_gesture2(self.model, hand_landmarks, h, w)
                    
                    cv2.putText(frame, f'Gesture: {gesture}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    # éviter de spammer avec des gestes
                    self.command_manager.try_send_command(gesture)
                    
        #cv2.imshow('Hand Gesture Recognition', frame)  ### plus utile depuis qu'on utilise flask
        return frame, bool(results.multi_hand_landmarks)
    def clean(self):
        self.hands.close()