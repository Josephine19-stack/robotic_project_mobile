import os
import sys
import signal
import atexit
import time
import threading

import cv2
import tensorflow as tf

from gesture_control.utils.utils_tello import init_tello_video, init_stream, close_stream, send_tello_command
from gesture_control.gesture_control_manager import MediapipeController

# === Config ===
VIDEO_FOLDER = "output_videos"
MAX_DURATION = 180  # seconds
FPS = 20
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
PRINT_INTERVAL = 5 #secondes

# ===  Load the gesture recognition model ===
current_dir = os.path.dirname(__file__)
model_save_path = os.path.join(current_dir, 'data', 'keypoint_classifier_merge.keras')
gesture_model = tf.keras.models.load_model(model_save_path)

# === Init Directories ===
os.makedirs(VIDEO_FOLDER, exist_ok=True)

#  === Video Recorder ===
timestamp = time.strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(VIDEO_FOLDER, f"tello_gesture_{timestamp}.avi")

fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_out = cv2.VideoWriter(output_path, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))   

# === Init Tello ===
tello = init_tello_video()

battery = tello.get_battery()
print(f"Battery: {battery}%")
if battery < 20:
    print("Battery too low. Aborting.")
    exit()

tello = init_stream(tello)  
frame_reader = tello.get_frame_read()

# === Init MediaPipe handling  ===
mediapipeController = MediapipeController(tello, gesture_model)

# === Emergency Land ===
def emergency_land(*args):
    try:
        if mediapipeController.command_manager.is_flying:
            print("The Tello drone is still flying;", end='')
        print("we’re forcing it to land...")
        send_tello_command(tello, "FIST")
        mediapipeController.clean()
        close_stream(tello)
    except Exception as e:
        print(f"Error during emergency landing: {e}")
    finally:
        cv2.destroyAllWindows()
        video_out.release()
        sys.exit(0)
        
signal.signal(signal.SIGINT, emergency_land)
signal.signal(signal.SIGTERM, emergency_land)
atexit.register(emergency_land)

def update_frames():
    while True:
        frame_reader.frame  # force update 'ajouter une sécurité sur frame_reader.frame avant de l’utiliser, car le flux peut parfois être vide au démarrage.
        time.sleep(0.01)
        
threading.Thread(target=update_frames, daemon=True).start()

# === Main Generator ===
def generate_frames_gesture():
    last_print_time = 0    
    start_time = time.time()
    
    try: 
        while True:
            frame = frame_reader.frame
            if frame is None:
                continue
            frame = cv2.resize(frame, (640, 480))
            
            frame, booleen = mediapipeController.detect_hand_landmarks_and_control_drone(frame)
            
            if not booleen:
                current_time = time.time()
                if current_time - last_print_time > PRINT_INTERVAL:
                    print("The landmarks were not detected")
                    last_print_time = current_time
            
            video_out.write(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # === Conditions that stops the while loop ===
            if tello.get_battery() < 20:
                print(f'Tello battery is {tello.get_battery()}. Forced landing.')
                break
            
            if time.time() - start_time > MAX_DURATION:
                print("Max duration reached — landing.")
                break

            time.sleep(1 / 15.0)
                
    except KeyboardInterrupt:
        print("KeyboardInterrupt — landing.")
    finally:
        emergency_land()
        
# vérifier au debut qu'il n'y ait pas d'autres instances du meme code qui tourne SINON erreur 