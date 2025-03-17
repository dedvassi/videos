from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
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
@app.route('/videos/<path:filename>')
def video(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_size = os.path.getsize(video_path)
    range_header = request.headers.get('Range', None)

    if range_header:
        # Поддержка частичной загрузки (для потоковой передачи)
        start, end = get_range(range_header, file_size)
        with open(video_path, 'rb') as f:
            f.seek(start)
            data = f.read(end - start + 1)
        response = Response(
            data,
            206,  # Partial Content
            mimetype='video/mp4',
            content_type='video/mp4',
            direct_passthrough=True
        )
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        return response
    else:
        # Полная загрузка видео
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Обработка WebSocket событий
@socketio.on('playbackAction')
def handle_playback_action(data):
    emit('syncPlayback', data, broadcast=True, include_self=False)

# Функция для обработки Range-заголовка
def get_range(range_header, file_size):
    start, end = range_header.replace('bytes=', '').split('-')
    start = int(start)
    end = int(end) if end else file_size - 1
    return start, end

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0')