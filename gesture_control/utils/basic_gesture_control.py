"""
This module provides two gesture recognition methods for controlling a Tello drone:
 - A hardcoded method using MediaPipe landmark geometry
 - A model-based method using a trained gesture classification neural network
"""

import math
import numpy as np

#from gesture_control.utils.image_treatment import preprocess_mediapipe_landmarks
from utils.image_treatment import preprocess_mediapipe_landmarks

GESTURE_LABELS = {
    0: 'OPEN_PALM',   # Take off
    1: 'FIST',        # Land
    2: 'UP',          # Move up
    3: 'LEFT',        # OK sign => left
    4: 'DOWN',        # Move down
    5: 'RIGHT',       # Fist rotated => right
    6: '',            # Move forward
    7: ''             # Move backward
}

def get_angle(a, b, c):
    """Returns the angle in degrees between vectors ab and bc"""
    ab = [b.x - a.x, b.y - a.y]
    bc = [c.x - b.x, c.y - b.y]
    dot = ab[0]*bc[0] + ab[1]*bc[1]
    norm_ab = math.hypot(*ab)
    norm_bc = math.hypot(*bc)
    if norm_ab * norm_bc == 0:
        return 0
    cos_angle = dot / (norm_ab * norm_bc)
    angle = math.acos(max(min(cos_angle, 1), -1))
    return math.degrees(angle)

def is_finger_up(tip_id, landmarks):
    return landmarks[tip_id].y < landmarks[tip_id - 2].y

def is_finger_down(tip_id, landmarks):
    return landmarks[tip_id].y > landmarks[tip_id - 2].y

def is_finger_down_and_under(tip_id, landmarks):
    wrist_y = landmarks[0].y
    thumb_tip_y = landmarks[4].y
    index_tip_y = landmarks[tip_id].y
    return (index_tip_y > wrist_y + 0.04) and (index_tip_y > thumb_tip_y + 0.02) and is_finger_down(tip_id, landmarks)
    
def define_orientation_hand(landmarks):
    y_tips = [landmarks[i].y for i in [8, 12, 16, 20]]
    return max(y_tips) - min(y_tips)
            
def recognize_gesture(landmarks):
        """
        Recognizes simple gestures based on relative finger positions.
        Takes as input a list of 21 MediaPipe hand landmarks.
        """
        # FIXME: THUMBS UP AND DOWN IS NOT WORKING !!!!!
            
        fingers_up = [is_finger_up(i, landmarks) for i in [8, 12, 16, 20]]

        # Thumb logic: using angle + lateral position      
        thumb_angle = get_angle(landmarks[2], landmarks[3], landmarks[4])
        score_right = 0
        score_left = 0

        # Extension
        if thumb_angle > 150:
            score_right += 1
            score_left += 1
            
        # Lateral position
        if landmarks[4].x > landmarks[3].x + 0.02:
            score_right += 2
        elif landmarks[4].x < landmarks[3].x - 0.02:
            score_left += 2

        if max(score_right, score_left) == 0 :
            thumb_dir = "FOLDED"
        elif score_right > score_left:
            thumb_dir = "RIGHT"
        elif score_left > score_right:
            thumb_dir = "LEFT"            
        else:
            thumb_dir = "CENTER"
            
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]
        dist_index_thumb = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
        
        other_fingers_folded = fingers_up[1:] == [0, 0, 0]
        other_fingers_upright = fingers_up[1:] == [1, 1, 1]
        
        # Hardcoded rules based on finger and thumb states
        if fingers_up == [0, 0, 0, 0] and thumb_angle > 160:
            return "BACK"
        elif fingers_up == [0, 1, 1, 1] and dist_index_thumb < 0.05:
            return "OK_SIGN"
        elif fingers_up == [0, 0, 0, 0] and thumb_dir == "FOLDED":
            return "FIST"
        elif is_finger_up(8, landmarks) and other_fingers_folded and thumb_dir == "LEFT":
            return "MOVE_UP"
        elif is_finger_down_and_under(8, landmarks) and other_fingers_upright and thumb_dir == "LEFT":
            return "MOVE_DOWN"
        elif fingers_up == [0, 0, 0, 0] and thumb_dir == "RIGHT":
            return "RIGHT"
        elif fingers_up == [0, 0, 0, 0] and thumb_dir == "LEFT":
            return "LEFT"
        elif fingers_up == [1, 1, 1, 1] and thumb_dir in ["RIGHT", "LEFT"]:
            return "OPEN_PALM"
        elif fingers_up == [1, 0, 0, 0]:
            return "INDEX_FRONT"
        elif fingers_up == [0, 0, 0, 1]:
            return "PINKY_BACK"
        else:
            return "UNKNOWN"    

def recognize_gesture2(gesture_model, landmarks, image_width=640, image_height=480):
    """
    Uses a trained neural network to classify gestures based on normalized hand landmarks.
    Converts the landmarks into a (42,) vector, predicts the class, and returns the label.
    """
    input_vector = preprocess_mediapipe_landmarks(landmarks, image_width, image_height)
    input_vector = np.expand_dims(input_vector, axis=0)  # shape (1, 42)
    prediction = gesture_model.predict(input_vector)
    pred_index = int(np.argmax(prediction))
    
    return GESTURE_LABELS.get(pred_index, str(pred_index))