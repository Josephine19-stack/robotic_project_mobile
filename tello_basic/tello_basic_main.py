from djitellopy import Tello
import cv2
import numpy as np
import time
import os

# Save videos in a dedicated folder
os.makedirs("output_videos", exist_ok=True)

tello = Tello()
tello.connect()

battery = tello.get_battery()
print(f"Battery: {battery}%")

if battery < 20:
    print("Battery too low. Aborting.")
    exit()

tello.streamon()
frame_reader = tello.get_frame_read()

# Timestamped output filename
timestamp = time.strftime("%Y%m%d_%H%M%S")
video_filename = f"output_videos/tello_tracking_{timestamp}.avi"

# Configure video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))

tello.takeoff()
time.sleep(2)

frame_center_x = 320
frame_center_y = 240
tolerance = 50
start_time = time.time()
max_duration = 180  # seconds
last_seen_time = time.time()

rotation_count = 0  # Count how many times we rotate without detection
max_rotations = 7   # After 7 rotations, we stop


def generate_frames():
    global last_seen_time, rotation_count
    try:
        while True:
            frame = frame_reader.frame
            if frame is None:
                print("Frame not received, skipping...")
                continue

            frame = cv2.resize(frame, (640, 480))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Green detection range
            lower_green = np.array([30, 40, 40])
            upper_green = np.array([90, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            valid_contour_found = False
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 1000:
                    valid_contour_found = True
                    rotation_count = 0  # Reset if we see green
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx = x + w // 2
                    cy = y + h // 2
                    last_seen_time = time.time()

                    # Draw bounding box and center point
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                    cv2.putText(frame, f"({cx}, {cy}) Area: {int(area)}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    print(f" Green object at: ({cx}, {cy}) | Area: {area:.1f}")

                    # Motion commands
                    if cx < frame_center_x - tolerance:
                        print("→ Move LEFT")
                        tello.move_left(20)
                    elif cx > frame_center_x + tolerance:
                        print("→ Move RIGHT")
                        tello.move_right(20)

                    if cy < frame_center_y - tolerance:
                        print("→ Move UP")
                        tello.move_up(20)
                    elif cy > frame_center_y + tolerance:
                        print("→ Move DOWN")
                        tello.move_down(20)

                    if area < 3000:
                        print("→ Move FORWARD")
                        tello.move_forward(20)
                    elif area > 25000:
                        print("→ Move BACKWARD")
                        tello.move_back(20)
                    else:
                        print("→ HOLD POSITION")
                    break

            # If no green detected for 5s
            if not valid_contour_found and time.time() - last_seen_time > 5:
                if rotation_count < max_rotations:
                    print(" No green detected, rotating...")
                    tello.rotate_clockwise(30)
                    time.sleep(1)
                    last_seen_time = time.time()
                    rotation_count += 1
                else:
                    print(" No object found after 4 rotations — landing.")
                    break

            # Overlay timestamp and center dot
            elapsed = int(time.time() - start_time)
            cv2.putText(frame, f"Time: {elapsed}s", (10, 470),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.circle(frame, (frame_center_x, frame_center_y),
                       5, (0, 0, 255), -1)

            # Write and stream frame
            video_out.write(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            # Timeout safety
            if time.time() - start_time > max_duration:
                print(" Max duration reached — landing.")
                break

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("KeyboardInterrupt — landing.")

    finally:
        tello.land()
        tello.streamoff()
        cv2.destroyAllWindows()
        video_out.release()
        print(f" Drone landed. Video saved to {video_filename}")
        print(
            f" Total duration recorded: {int(time.time() - start_time)} seconds")
