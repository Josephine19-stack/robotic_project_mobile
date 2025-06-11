from flask import Flask, Response
import webbrowser
import threading
import time

USE_PID = False  # ← Switch to False to use basic tracking

# === Import the appropriate drone stream generator ===
if USE_PID:
    from tello_pid.tello_pid_main import generate_frames
else:
    from tello_basic.tello_basic_main import generate_frames

app = Flask(__name__)


@app.route('/')
def index():
    return """
    <h2>📡 Live Tello Stream</h2>
    <p>Streaming {mode} drone logic</p>
    <img src='/video_feed'>
    """.format(mode="PID-based" if USE_PID else "Basic")


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def open_browser():
    time.sleep(1)
    webbrowser.open_new("http://localhost:5000")


if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000)
