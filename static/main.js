const socket = io();
const video = document.getElementById("videoPlayer");

socket.on("video_changed", (data) => {
    const timestamp = new Date().getTime();
    video.src = data.video_url + "?t=" + timestamp;
    video.load();
    video.play().catch(err => console.log("Автовоспроизведение заблокировано:", err));
});

// Отправка данных о состоянии видео
function sendSyncEvent(event) {
    socket.emit("sync_video", {
        action: event.type,
        currentTime: video.currentTime,
        playing: !video.paused
    });
}

// Обработка изменений у других пользователей
socket.on("sync_video", (data) => {
    if (data.action === "play") {
        video.currentTime = data.currentTime;
        video.play();
    } else if (data.action === "pause") {
        video.pause();
    } else if (data.action === "seeked") {
        video.currentTime = data.currentTime;
    }
});

// Подключение обработчиков событий
video.addEventListener("play", sendSyncEvent);
video.addEventListener("pause", sendSyncEvent);
video.addEventListener("seeked", sendSyncEvent);
