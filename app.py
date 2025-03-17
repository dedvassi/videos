from flask import Flask, render_template, request, redirect, url_for, Response
from flask_socketio import SocketIO, emit
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'webm', 'ogg'}
socketio = SocketIO(app)

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Загрузка видео
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
    return redirect(url_for('index'))

# Потоковая передача видео
@app.route('/video_feed')
def video_feed():
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video.mp4')  # Используем загруженное видео
    return Response(
        generate_video(video_path),
        content_type='video/mp4',
        headers={'Accept-Ranges': 'bytes'}
    )

# Генератор для потоковой передачи видео
def generate_video(video_path):
    with open(video_path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)  # Читаем по 1 МБ
            if not chunk:
                break
            yield chunk

# Обработка WebSocket событий
@socketio.on('playbackAction')
def handle_playback_action(data):
    emit('syncPlayback', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0')