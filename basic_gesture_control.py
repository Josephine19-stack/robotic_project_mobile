import math
MOVE_DIST = 20  # cm #attention


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
            return "THUMB_RIGHT"
        elif fingers_up == [0, 0, 0, 0] and thumb_dir == "LEFT":
            return "THUMB_LEFT"
        elif fingers_up == [0, 0, 0, 0] and landmarks[4].y < palm_center_y - 0.02:
            return "THUMB_UP"
        elif fingers_up == [0, 0, 0, 0] and landmarks[4].y > palm_center_y + 0.02:
            return "THUMB_DOWN"
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

def send_tello_command(tello, command):
    if command == "OPEN_PALM":
        print("Commande détectée : Décollage du drone")
        #tello.takeoff()
        return True
    elif command == "FIST":
        print("Commande détectée : Atterrissage du drone")
        #tello.land()
        return False
    elif command == "THUMB_UP":
        print(f"Commande détectée : Monter de {MOVE_DIST} cm")
        #tello.move_up(MOVE_DIST)
    elif command == "THUMB_DOWN":
        print(f"Commande détectée : Descendre de {MOVE_DIST} cm")
        #tello.move_down(MOVE_DIST)
    elif command == "THUMB_LEFT":
        print(f"Commande détectée : Aller à gauche de {MOVE_DIST} cm")
        #tello.move_left(MOVE_DIST)
    elif command == "THUMB_RIGHT":
        print(f"Commande détectée : Aller à droite de {MOVE_DIST} cm")
        #tello.move_right(MOVE_DIST)
    elif command == "INDEX_FRONT":
        print(f"Commande détectée : Aller vers l'avant de {MOVE_DIST} cm")
        #tello.move_forward(MOVE_DIST)
    elif command == "PINKY_BACK":
        print(f"Commande détectée : Aller vers l'arrière de {MOVE_DIST} cm")
        #tello.move_back(MOVE_DIST)
    else:
        print(f"Commande inconnue : {command}")
    return None


    

'''
hearcascade_frontalface_dfaul : detect the face with a rectangular and point in the middle

the image capture.py: where  i capture frames  i want to reize it to 360, 240 and add a waitkey . 
gesture.py : to define how the gesture are interpreted 
gestureControl.py: check the kind of gesture is done. a fonction to interpreted the gesture input => how you go up or down, left, right, land and take_off. + i want an if regarding taking an image and saving it in a folder (don't forget to put a small sleep time so that only  one image is taken )) and return the list of we give to send_rc_control.
main.py file : to start our prgram: control the drone + while true for the camera + 
mapping.py: i need to declare my speed(do manual testing) for forward ans angle speed should maybe have a map of th place so that i could know where the drone is in the room.
'''