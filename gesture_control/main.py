'''
import subprocess
import sys
import os

python_in_venv = sys.executable  # chemin du python actuellement en cours (venv inclus)
script_path = os.path.join("keyboardControl", "keyboardControl.py")

subprocess.run([python_in_venv, script_path])
'''
import cv2
from utils.utils_tello import init_tello_video, init_stream, close_stream, send_tello_command
from utils.imageCapture import get_frame
from gesture_control_manager import MediapipeController 
import time
import tensorflow as tf

import os
import sys

# Ajoute le dossier racine du projet au PYTHONPATH
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    cap = cv2.VideoCapture(0)
    
    last_print_time = 0
    print_interval = 5 #secondes
    
    # Charger le modèle de reconnaissance de gestes
    current_dir = os.path.dirname(__file__)
    model_save_path = os.path.join(current_dir, 'data', 'keypoint_classifier.keras')
    gesture_model = tf.keras.models.load_model(model_save_path)
    
    tello = init_tello_video()
    tello = init_stream(tello)
    mediapipeController = MediapipeController(tello, gesture_model)

    battery_var = tello.get_battery()
    print(f"Battery is: {battery_var}")
    
    if battery_var > 20:
        print("Drone connecté.")

        while True:
            frame = get_frame(tello)
            if not mediapipeController.detect_hand_landmarks_and_control_drone(frame):
                
                current_time = time.time()
                if current_time - last_print_time > print_interval:
                    print("The landmarks were not detected")
                    last_print_time = current_time
                                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if tello.get_battery() < 20:
                print(f'Tello battery is {tello.get_battery()}.')
                break
    
    if mediapipeController.command_manager.is_flying:
        print("Forçage de l'atterrissage...")
        send_tello_command(tello, "FIST")
        
    mediapipeController.clean()
    close_stream(tello)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# vérifier au debut qu'il n'y ait pas d'autres instances du meme code qui tourne SINON erreur 