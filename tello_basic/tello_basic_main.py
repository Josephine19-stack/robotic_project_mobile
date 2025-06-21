from djitellopy import Tello
import cv2
import numpy as np
import time
import signal
import sys
import atexit
import threading
import os

# === Config ===
VIDEO_FOLDER = "output_videos"
FRAME_WIDTH, FRAME_HEIGHT = 640, 480
TOLERANCE = 50
AREA_MIN = 1000
AREA_TOO_CLOSE = 25000
AREA_TOO_FAR = 3000
MAX_ROTATIONS = 7
MAX_DURATION = 180  # seconds

# === Init Directories ===
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# === Init Tello ===
tello = Tello()
tello.connect()
battery = tello.get_battery()
print(f"Battery: {battery}%")
if battery < 20:
    print("Battery too low. Aborting.")
    exit()

tello.streamon()
frame_reader = tello.get_frame_read()

# === Video Recorder ===
timestamp = time.strftime("%Y%m%d_%H%M%S")
video_filename = os.path.join(VIDEO_FOLDER, f"tello_tracking_{timestamp}.avi")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_out = cv2.VideoWriter(video_filename, fourcc,
                            20.0, (FRAME_WIDTH, FRAME_HEIGHT))

# === Emergency Land ===


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


signal.signal(signal.SIGINT, emergency_land)
signal.signal(signal.SIGTERM, emergency_land)
atexit.register(emergency_land)

# === Takeoff ===
tello.takeoff()
time.sleep(2)

# === Frame Updater Thread ===


def update_frames():
    while True:
        frame_reader.frame  # force update
        time.sleep(0.01)


threading.Thread(target=update_frames, daemon=True).start()

# === Main Generator ===


def generate_frames():
    frame_center = (FRAME_WIDTH // 2, FRAME_HEIGHT // 2)
    start_time = time.time()
    last_seen_time = time.time()
    rotation_count = 0

    last_position = None
    last_command = None

    try:
        while True:
            frame = frame_reader.frame
            if frame is None:
                continue

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_green = np.array([30, 40, 40])
            upper_green = np.array([90, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            valid_contour = False
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > AREA_MIN:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx, cy = x + w // 2, y + h // 2
                    current_position = (cx, cy, int(area))

                    if current_position != last_position:
                        print(
                            f"Green object at: ({cx}, {cy}) | Area: {area:.1f}")
                        last_position = current_position

                    last_seen_time = time.time()
                    valid_contour = True
                    rotation_count = 0

                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                    cv2.putText(frame, f"({cx}, {cy}) Area: {int(area)}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    command = "HOLD"

                    if cx < frame_center[0] - TOLERANCE:
                        tello.move_left(20)
                        command = "MOVE LEFT"
                    elif cx > frame_center[0] + TOLERANCE:
                        tello.move_right(20)
                        command = "MOVE RIGHT"

                    if cy < frame_center[1] - TOLERANCE:
                        tello.move_up(20)
                        command = "MOVE UP"
                    elif cy > frame_center[1] + TOLERANCE:
                        tello.move_down(20)
                        command = "MOVE DOWN"

                    if area < AREA_TOO_FAR:
                        tello.move_forward(20)
                        command = "MOVE FORWARD"
                    elif area > AREA_TOO_CLOSE:
                        tello.move_back(20)
                        command = "MOVE BACKWARD"

                    if command != last_command:
                        print(f"→ {command}")
                        last_command = command

                    break  # process only one contour

            if not valid_contour and time.time() - last_seen_time > 5:
                if rotation_count < MAX_ROTATIONS:
                    print("No green detected, rotating...")
                    tello.rotate_clockwise(30)
                    time.sleep(1)
                    last_seen_time = time.time()
                    rotation_count += 1
                else:
                    print("Max rotations reached — landing.")
                    break

            # Time overlay
            elapsed = int(time.time() - start_time)
            cv2.putText(frame, f"Time: {elapsed}s", (10, FRAME_HEIGHT - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.circle(frame, frame_center, 5, (0, 0, 255), -1)

            # Save + Stream
            video_out.write(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            if time.time() - start_time > MAX_DURATION:
                print("Max duration reached — landing.")
                break

            time.sleep(1 / 15.0)  # limit to 15 FPS

    except KeyboardInterrupt:
        print("KeyboardInterrupt — landing.")
    finally:
        emergency_land()
