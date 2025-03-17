import os
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

current_video = None  # Переменная для текущего видео
video_state = {"time": 0, "paused": False}  # Храним состояние видео

@app.route("/")
def index():
    return render_template("index.html", video=current_video)

@app.route("/upload", methods=["POST"])
def upload():
    global current_video, video_state

    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    if file:
        filename = os.path.join(app.config["UPLOAD_FOLDER"], "video.mp4")
        file.save(filename)
        current_video = f"/{filename}"
        video_state = {"time": 0, "paused": False}

        # Сообщаем всем клиентам о новом видео
        socketio.emit("video_changed", {"src": current_video})

    return redirect(url_for("index"))

@socketio.on("sync_video")
def sync_video(data):
    global video_state
    video_state = data
    emit("sync_video", video_state, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
