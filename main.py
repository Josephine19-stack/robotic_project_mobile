'''
import subprocess
import sys
import os

python_in_venv = sys.executable  # chemin du python actuellement en cours (venv inclus)
script_path = os.path.join("keyboardControl", "keyboardControl.py")

subprocess.run([python_in_venv, script_path])
'''
import cv2
from utils import init_tello_video, init_stream, close_stream
from imageCapture import get_frame
from gesture_control import MediapipeController
from basic_gesture_control import send_tello_command
import time


def main():
    last_print_time = 0
    print_interval = 5 #secondes

    tello = init_tello_video()
    tello = init_stream(tello)
    mediapipeController = MediapipeController(tello)

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
                        
            cv2.imshow("Drone Feed", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    if mediapipeController.command_manager.is_flying:
        print("Forçage de l'atterrissage...")
        send_tello_command(tello, "FIST")
        
    mediapipeController.clean()
    close_stream(tello)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# vérifier au debut qu'il n'y ait pas d'autres instances du meme code qui tourne SINON erreur 