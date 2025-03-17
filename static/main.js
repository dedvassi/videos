const socket = io(); // Подключение к WebSocket
const videoPlayer = document.getElementById('videoPlayer');
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');

// Загрузка видео
uploadForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (file) {
    const formData = new FormData();
    formData.append('file', file);
    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
      .then(() => {
        videoPlayer.src = '/video_feed';
        videoPlayer.play();
      })
      .catch((err) => console.error('Ошибка загрузки:', err));
  }
});

// Синхронизация воспроизведения
socket.on('syncPlayback', (data) => {
  if (data.action === 'play') {
    videoPlayer.currentTime = data.time;
    videoPlayer.play();
  } else if (data.action === 'pause') {
    videoPlayer.pause();
  } else if (data.action === 'seek') {
    videoPlayer.currentTime = data.time;
  }
});

// Отправка событий воспроизведения на сервер
videoPlayer.addEventListener('play', () => {
  socket.emit('playbackAction', { action: 'play', time: videoPlayer.currentTime });
});

videoPlayer.addEventListener('pause', () => {
  socket.emit('playbackAction', { action: 'pause', time: videoPlayer.currentTime });
});

videoPlayer.addEventListener('seeked', () => {
  socket.emit('playbackAction', { action: 'seek', time: videoPlayer.currentTime });
});