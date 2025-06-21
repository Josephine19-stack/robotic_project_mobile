from djitellopy import tello
MOVE_DIST = 30  # cm #attention

def init_tello_video():
    me = tello.Tello()
    me.connect()
    return me

def init_stream(me):
    me.streamon()
    return me

def close_stream(me):
    me.streamoff()
    
def send_tello_command(me, command):
    if command == "OPEN_PALM":
        print("Commande détectée : Décollage du drone")
        #me.takeoff()
        return True
    elif command == "FIST":
        print("Commande détectée : Atterrissage du drone")
        #me.land()
        return False
    elif command == "UP":
        print(f"Commande détectée : Monter de {MOVE_DIST} cm")
        #me.move_up(MOVE_DIST)
    elif command == "DOWN":
        print(f"Commande détectée : Descendre de {MOVE_DIST} cm")
        #me.move_down(MOVE_DIST)
    elif command == "LEFT":
        print(f"Commande détectée : Aller à gauche de {MOVE_DIST} cm")
        #me.move_left(MOVE_DIST)
    elif command == "RIGHT":
        print(f"Commande détectée : Aller à droite de {MOVE_DIST} cm")
        #me.move_right(MOVE_DIST)
    elif command == "INDEX_FRONT":
        print(f"Commande détectée : Aller vers l'avant de {MOVE_DIST} cm")
        #me.move_forward(MOVE_DIST)
    elif command == "PINKY_BACK":
        print(f"Commande détectée : Aller vers l'arrière de {MOVE_DIST} cm")
        #me.move_back(MOVE_DIST)
    else:
        print(f"Commande inconnue : {command}")
    return None