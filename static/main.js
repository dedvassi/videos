const socket = io();
const video = document.getElementById("videoPlayer");

socket.on("video_changed", (data) => {
    video.src = data.src;
    video.load();
    video.play();
});

// Обновляем состояние видео при изменении
video.addEventListener("play", () => {
    socket.emit("sync_video", { time: video.currentTime, paused: false });
});

video.addEventListener("pause", () => {
    socket.emit("sync_video", { time: video.currentTime, paused: true });
});

video.addEventListener("seeked", () => {
    socket.emit("sync_video", { time: video.currentTime, paused: video.paused });
});

// Синхронизируем видео у всех
socket.on("sync_video", (data) => {
    if (Math.abs(video.currentTime - data.time) > 0.5) {
        video.currentTime = data.time;
    }
    if (data.paused) {
        video.pause();
    } else {
        video.play();
    }
});
