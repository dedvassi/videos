from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

current_video = None  # Глобальная переменная для хранения текущего видео


@app.route('/')
def index():
    return render_template('index.html', video=current_video)


@app.route('/upload', methods=['POST'])
def upload_video():
    global current_video
    if 'video' not in request.files:
        return "No file uploaded", 400

    file = request.files['video']
    if file.filename == '':
        return "No selected file", 400

    filename = os.path.join(UPLOAD_FOLDER, 'current_video.mp4')
    file.save(filename)
    current_video = 'uploads/current_video.mp4'

    # Сообщаем всем клиентам, что загружено новое видео
    socketio.emit('video_changed', {'video_url': current_video})
    return "File uploaded", 200


@socketio.on('video_control')
def handle_video_control(data):
    """ Отправляем всем пользователям команду синхронизации видео """
    emit('sync_video', data, broadcast=True, include_self=False)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
