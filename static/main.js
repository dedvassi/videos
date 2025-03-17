const socket = io();
const video = document.getElementById("videoPlayer");

// Время для синхронизации (например, 1 секунда)
const syncInterval = 1000;
let lastSyncTime = 0;

// Отправка данных о состоянии видео
function sendSyncEvent(event) {
    // Проверка, что прошло достаточно времени для следующей синхронизации
    if (new Date().getTime() - lastSyncTime >= syncInterval) {
        socket.emit("sync_video", {
            action: event.type,
            currentTime: video.currentTime,
            playing: !video.paused
        });
        lastSyncTime = new Date().getTime();
    }
}

// Обработка изменений у других пользователей
socket.on("sync_video", (data) => {
    if (data.action === "play") {
        // Если видео не на паузе, не делаем ничего
        if (video.paused) {
            video.play();
        }
        video.currentTime = data.currentTime;
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
