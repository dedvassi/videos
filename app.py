from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

current_video = None
video_time = 0  # Текущее время воспроизведения
video_state = "play"  # play / pause

@app.route("/")
def index():
    return render_template("index.html", video=current_video)

@app.route("/upload", methods=["POST"])
def upload():
    global current_video, video_time, video_state
    if "video" in request.files:
        file = request.files["video"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        current_video = file.filename
        video_time = 0
        video_state = "play"
        socketio.emit("video_update", {"video": current_video, "time": video_time, "state": video_state})
    return redirect(url_for("index"))

@socketio.on("sync")
def sync(data):
    global video_time, video_state
    video_time = data["time"]
    video_state = data["state"]
    emit("sync", data, broadcast=True, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)  # Render требует открытый порт
