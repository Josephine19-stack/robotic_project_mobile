import os
from flask import Flask, Response
import webbrowser
import threading
import time
import sys

mode_name = sys.argv[1] if len(sys.argv) > 1 else "basic"

app = Flask(__name__)

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Tello Drone Live</title>
    <style>
        body {{
            background-color: #121212;
            color: #00ff99;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            margin-top: 30px;
            font-size: 2.5em;
        }}
        p {{
            color: #888;
            font-size: 1em;
        }}
        .video-container {{
            margin-top: 40px;
        }}
        img {{
            border: 5px solid #00ff99;
            border-radius: 15px;
            max-width: 90%;
            height: auto;
            box-shadow: 0 0 30px #00ff99;
        }}
        footer {{
            margin-top: 40px;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>📡 Tello Live Stream</h1>
    <p>Tracking mode: <strong>{"Basic"}</strong></p>
    <div class="video-container">
        <img src="/video_feed" alt="Live Drone Stream">
    </div>
    <footer>
        <p>Drone stream powered by Flask + djitellopy</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/video_feed')
def video_feed():
    if mode_name == "gesture":
        print("We are running with the gesture mode.")
        from gesture_control.main import generate_frames_gesture
        return Response(generate_frames_gesture(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        print("We are running with the basic mode.")
        from tello_basic.tello_basic_main import generate_frames
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def open_browser():
    time.sleep(1)
    webbrowser.open_new("http://localhost:5000")

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000)