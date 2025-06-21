'''
import subprocess
import sys
import os

python_in_venv = sys.executable  # chemin du python actuellement en cours (venv inclus)
script_path = os.path.join("keyboardControl", "keyboardControl.py")

subprocess.run([python_in_venv, script_path])
'''
import cv2
from gesture_control.utils.utils_tello import init_tello_video, init_stream, close_stream, send_tello_command
from gesture_control.gesture_control_manager import MediapipeController 
import time
import tensorflow as tf


import threading
import signal
import atexit

import os
import sys

VIDEO_FOLDER = "output_videos"

# # Définir codec et créer l’objet VideoWriter
os.makedirs(VIDEO_FOLDER, exist_ok=True)
timestamp = time.strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(VIDEO_FOLDER, f"tello_gesture_{timestamp}.avi")

fourcc = cv2.VideoWriter_fourcc(*'XVID')  # ou 'MJPG', 'X264'
fps = 20
frame_width = 640
frame_height = 480
video_out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))   

# init
tello = init_tello_video()
tello = init_stream(tello)
frame_reader = tello.get_frame_read()

def update_frames():
    while True:
        frame_reader.frame  # force update 'ajouter une sécurité sur frame_reader.frame avant de l’utiliser, car le flux peut parfois être vide au démarrage.
        time.sleep(0.01)
        
threading.Thread(target=update_frames, daemon=True).start()

def emergency_land(*args):
    try:
        print("Emergency landing...")
        tello.land()
        tello.streamoff()
    except Exception as e:
        print(f"Error during emergency landing: {e}")
    finally:
        cv2.destroyAllWindows()
        video_out.release()
        sys.exit(0)
        
#signal.signal(signal.SIGINT, emergency_land)
#signal.signal(signal.SIGTERM, emergency_land)
#atexit.register(emergency_land)
        
def generate_frames():

    # Charger le modèle de reconnaissance de gestes
    current_dir = os.path.dirname(__file__)
    model_save_path = os.path.join(current_dir, 'data', 'keypoint_classifier.keras')
    gesture_model = tf.keras.models.load_model(model_save_path)

    mediapipeController = MediapipeController(tello, gesture_model)

    last_print_time = 0
    print_interval = 5 #secondes
    
    battery_var = tello.get_battery()
    print(f"Battery is: {battery_var}")
    
    if battery_var > 20:
        print("Drone connecté.")

        while True:
            frame = frame_reader.frame
            frame = cv2.resize(frame, (640, 480))

            frame, booleen = mediapipeController.detect_hand_landmarks_and_control_drone(frame)
            
            if not booleen:
                current_time = time.time()
                if current_time - last_print_time > print_interval:
                    print("The landmarks were not detected")
                    last_print_time = current_time
            
            if tello.get_battery() < 20:
                print(f'Tello battery is {tello.get_battery()}. Atterrissage forcé.')
                send_tello_command(tello, "FIST")
                break
            
            video_out.write(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()

            # Envoi au flux Flask
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
           
    if mediapipeController.command_manager.is_flying:
        print("Forçage de l'atterrissage...")
        send_tello_command(tello, "FIST")
        
    mediapipeController.clean()
    close_stream(tello)
    video_out.release()
    cv2.destroyAllWindows()
    sys.exit(0)
# vérifier au debut qu'il n'y ait pas d'autres instances du meme code qui tourne SINON erreur 