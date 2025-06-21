import math
from gesture_control.utils.image_treatment import preprocess_mediapipe_landmarks
import numpy as np

# manque deux commandes => move forward and backward
GESTURE_LABELS = {
    0: 'OPEN_PALM', # decollage
    1: 'FIST', # land
    2: 'UP', # go up
    3: 'LEFT', # ok sign
    4: 'DOWN', # go down
    5: 'RIGHT', # fist tourné
    6: '', # move left
    7: '' # move right
}

def get_angle(a, b, c):
    """Retourne l'angle en degrés entre les vecteurs ab et bc"""
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


def recognize_gesture(landmarks):
        """
        Reconnaît des gestes simples à partir des positions relatives des doigts.
        Requiert la liste de 21 landmarks MediaPipe.
        """
        ## THUMBS UP AND DOWN IS NOT WORKING !!!!!

        fingers_up = []

        # Index, majeur, annulaire, auriculaire
        for tip_id in [8, 12, 16, 20]:
            if landmarks[tip_id].y < landmarks[tip_id - 2].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)

        ### Gestion du pouce: abvec angle et s'il est tendu ou pas, vers le gauche ou droite###
        # ATTENTION: trouver une meilleure manière de gérer le pouce
        palm_ids = [0, 1, 2, 5, 9, 13, 17]
        palm_center_y = sum(landmarks[i].y for i in palm_ids) / len(palm_ids)
        
        thumb_angle = get_angle(landmarks[2], landmarks[3], landmarks[4])
        score_right = 0
        score_left = 0

        # Angle (tendu ou pas)
        if thumb_angle > 150:
            score_right += 1
            score_left += 1

        # Position latérale (plus discriminante)
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
            
        #print(f"Score right: {score_right}, Score left: {score_left}")
            
        # Regles
        if fingers_up == [0, 0, 0, 0] and thumb_dir == "RIGHT":
            return "RIGHT"
        elif fingers_up == [0, 0, 0, 0] and thumb_dir == "LEFT":
            return "LEFT"
        elif fingers_up == [1, 1, 1, 1] and thumb_dir in ["RIGHT", "LEFT"]:
            return "OPEN_PALM"
        elif fingers_up == [0, 0, 0, 0] and thumb_dir == "FOLDED":
            return "FIST"
        elif fingers_up == [1, 0, 0, 0]:
            return "INDEX_FRONT"
        elif fingers_up == [0, 0, 0, 1]:
            return "PINKY_BACK"
        else:
            return "UNKNOWN"    

def recognize_gesture2(gesture_model, landmarks, image_width=640, image_height=480):
    # Convertit les landmarks MediaPipe en vecteur normalisé (42,) et prédit le label de geste à l'aide du modèle entraîné.
    input_vector = preprocess_mediapipe_landmarks(landmarks, image_width, image_height)
    input_vector = np.expand_dims(input_vector, axis=0)  # shape (1, 42)
    prediction = gesture_model.predict(input_vector)
    pred_index = int(np.argmax(prediction))
    
    return GESTURE_LABELS.get(pred_index, str(pred_index))