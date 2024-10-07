let isRecording = false;
let isPlaying = false;
let timerInterval;
let timer = 0;

function toggleRecord() {
    const recordButton = document.getElementById("recordButton");
    const timerDisplay = document.getElementById("timer");

    if (!isRecording) {
        isRecording = true;
        recordButton.textContent = "Stop";
        timerDisplay.style.display = "inline";
        startTimer();
    } else {
        isRecording = false;
        recordButton.textContent = "Record";
        stopTimer();
    }
}

function togglePlay() {
    const playButton = document.getElementById("playButton");

    if (!isPlaying) {
        isPlaying = true;
        playButton.textContent = "Stop";
        // Jalankan aksi play di sini
    } else {
        isPlaying = false;
        playButton.textContent = "Play";
        // Hentikan aksi play di sini
    }
}

function startTimer() {
    timer = 0;
    timerInterval = setInterval(() => {
        timer++;
        const minutes = String(Math.floor(timer / 60)).padStart(2, '0');
        const seconds = String(timer % 60).padStart(2, '0');
        document.getElementById("timer").textContent = `${minutes}:${seconds}`;
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
    document.getElementById("timer").textContent = "00:00";
}
