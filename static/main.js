const socket = io();
const video = document.getElementById("video");

socket.on("video_update", (data) => {
    location.reload();  // Перезагружаем страницу при смене видео
});

socket.on("sync", (data) => {
    if (Math.abs(video.currentTime - data.time) > 0.5) {
        video.currentTime = data.time;
    }
    if (data.state === "play" && video.paused) {
        video.play();
    } else if (data.state === "pause" && !video.paused) {
        video.pause();
    }
});

video.addEventListener("play", () => {
    socket.emit("sync", { time: video.currentTime, state: "play" });
});

video.addEventListener("pause", () => {
    socket.emit("sync", { time: video.currentTime, state: "pause" });
});

video.addEventListener("seeked", () => {
    socket.emit("sync", { time: video.currentTime, state: video.paused ? "pause" : "play" });
});
