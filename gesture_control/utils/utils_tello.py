from djitellopy import tello

MOVE_DIST = 30  # cm
ROTATION_DEGREE = 45

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
    """Sends a movement command to the Tello drone based on a recognized gesture label. """
    if command == "OPEN_PALM":
        print("Command detected: Drone takeoff")
        # me.takeoff()
        return True
    elif command == "FIST":
        print("Command detected: Drone landing")
        # me.land()
        return False
    elif command == "MOVE_UP":
        print(f"Command detected: Ascend by {MOVE_DIST} cm")
        # me.move_up(MOVE_DIST)
    elif command == "MOVE_DOWN":
        print(f"Command detected: Descend by {MOVE_DIST} cm")
        # me.move_down(MOVE_DIST)
    elif command == "LEFT":
        print(f"Command detected: Move left by {MOVE_DIST} cm")
        # me.move_left(MOVE_DIST)
    elif command == "RIGHT":
        print(f"Command detected: Move right by {MOVE_DIST} cm")
        # me.move_right(MOVE_DIST)
    elif command == "INDEX_FRONT":
        print(f"Command detected: Move forward by {MOVE_DIST} cm")
        # me.move_forward(MOVE_DIST)
    elif command == "PINKY_BACK":
        print(f"Command detected: Move backward by {MOVE_DIST} cm")
        # me.move_back(MOVE_DIST)
    elif command == "OK_SIGN":
        print(f"Command detected: Rotate clockwise {ROTATION_DEGREE}")
        # me.rotate_clockwise(ROTATION_DEGREE)
    elif command == "BACK":
        print(f"Command detected: Rotate counter-clockwise {ROTATION_DEGREE}")
        # me.rotate_counter_clockwise(ROTATION_DEGREE)
    else:
        print(f"Unknown command: {command}")
    return None