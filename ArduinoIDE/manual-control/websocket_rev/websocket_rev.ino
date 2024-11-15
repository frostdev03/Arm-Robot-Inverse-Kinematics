#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <ESP32Servo.h>
#include <AccelStepper.h>

const char* ssid = "Kipas Angin";
const char* password = "11223344";

#define motorInterfaceType 1
#define dirPin 26  // Pin for direction
#define stepPin 23

unsigned long lastPlayTime = 0;

AccelStepper stepper(motorInterfaceType, stepPin, dirPin);

WebServer server(80);            // HTTP server pada port 80
WebSocketsServer webSocket(81);  // WebSocket server pada port 81

Servo servo1;   // Lower arm servo 1
Servo servo1b;  // Lower arm servo 2 (tambahan)
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

// Initial positions for the servos
int servo1_pos = 0;
int servo1b_pos = 0;
int servo2_pos = 0;
int servo3_pos = 0;
int servo4_pos = 0;
int servo5_pos = 0;
int servo6_pos = 0;

const int MAX_MOTION_STEPS = 100;  // Maximum number of steps that can be recorded

// Arrays to store recorded positions
int recordedPositions1[MAX_MOTION_STEPS];
int recordedPositions2[MAX_MOTION_STEPS];
int recordedPositions3[MAX_MOTION_STEPS];
int recordedPositions4[MAX_MOTION_STEPS];
int recordedPositions5[MAX_MOTION_STEPS];
int recordedPositions6[MAX_MOTION_STEPS];
int recordedPositions7[MAX_MOTION_STEPS];

// Recording variables
bool isRecording = false;
bool isPlaying = false;
int currentStep = 0;
int playIndex = 0;
unsigned long recordInterval = 500;  // Record interval in ms

int stepsToMove = 200;  // Total langkah yang diinginkan
int stepDelay = 1000;

int stepperPositionCW = 0;
int stepperPositionCCW = 0;

int recordedPositions[6][100];  // Array to store up to 100 servo positions for each servo
int playbackIndex = 0;

// Halaman HTML di-embed langsung di dalam kode
const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Robot Arm Control</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        color: #333;
        margin: 0;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
      }

      h1 {
        color: #333;
        margin-bottom: 20px;
      }

      div {
        margin-bottom: 15px;
        width: 100%;
        max-width: 400px;
      }

      label {
        font-size: 1.2em;
        display: block;
        margin-bottom: 5px;
      }

      input[type="range"] {
        width: 100%;
        height: 5px;
        -webkit-appearance: none;
        appearance: none;
        background: #ddd;
        border-radius: 5px;
        outline: none;
      }

      input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 20px;
        height: 20px;
        background: #333;
        cursor: pointer;
        border-radius: 50%;
      }

      input[type="range"]::-moz-range-thumb {
        width: 20px;
        height: 20px;
        background: #333;
        cursor: pointer;
        border-radius: 50%;
      }

      .degree-display {
        font-size: 1.2em;
        margin-top: 10px;
        text-align: center;
        color: #555;
      }

      .button-container {
        display: flex;
        gap: 10px;
        margin-top: 20px;
        flex-wrap: wrap;
      }

      button {
        padding: 10px 20px;
        font-size: 1em;
        background-color: #333;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s ease;
      }

      button:hover {
        background-color: #555;
      }

      /* Responsive styling */
      @media (max-width: 600px) {
        h1 {
          font-size: 1.5em;
        }

        label {
          font-size: 1em;
        }

        button {
          padding: 8px 15px;
          font-size: 0.9em;
        }
      }
    </style>
  </head>
  <body>
    <h1>Robot Arm Control</h1>

    <div>
      <label for="servo1">Lower Arm: <span id="servo1Degree">0</span>°</label>
      <input
        type="range"
        id="servo1"
        min="0"
        max="180"
        value="0"
        oninput="updateSlider(1, this.value)"
      />
    </div>

    <div>
      <label for="servo2">Center Arm: <span id="servo2Degree">0</span>°</label>
      <input
        type="range"
        id="servo2"
        min="0"
        max="170"
        value="0"
        oninput="updateSlider(2, this.value)"
      />
    </div>

    <div>
      <label for="servo3">Upper Arm: <span id="servo3Degree">0</span>°</label>
      <input
        type="range"
        id="servo3"
        min="0"
        max="170"
        value="0"
        oninput="updateSlider(3, this.value)"
      />
    </div>

    <div>
      <label for="servo4">Neck Gripper: <span id="servo4Degree">0</span>°</label>
      <input
        type="range"
        id="servo4"
        min="0"
        max="360"
        value="0"
        oninput="updateSlider(4, this.value)"
      />
    </div>

    <div>
      <label for="servo5">Gripper: <span id="servo5Degree">0</span>°</label>
      <input
        type="range"
        id="servo5"
        min="0"
        max="180"
        value="0"
        oninput="updateSlider(5, this.value)"
      />
    </div>

    <div>
      <label for="servo7">Stepper Motor Position: <span id="servo7Degree">0</span>°</label>
      <input
        type="range"
        id="servo7"
        min="0"
        max="200"
        value="0"
        oninput="updateSlider(7, this.value)"
      />
    </div>

    <div>
        <label for="stepperCW">Target Position (steps):</label>
        <input type="number" id="stepperCW" placeholder="Enter target position" />
        <button id="send" onclick="sendStepperPositionCW()">Move Stepper</button>
    </div>

    <div>
        <label for="stepperCCW">Target Position (steps):</label>
        <input type="number" id="stepperCCW" placeholder="Enter target position" />
        <button id="send" onclick="sendStepperPositionCCW()">Move Stepper</button>
    </div>

    <!-- Button Section -->
    <div class="button-container">
      <button id="recordBtn" onclick="sendCommand('record'); updateButtonState('record')">Record</button>
      <button id="stopRecordBtn" onclick="sendCommand('stopRecord')">Stop Record</button>
      <button id="playRecordBtn" onclick="sendCommand('play')">Play Record</button>
      <button id="stopPlayBtn" onclick="sendCommand('stopPlay')">Stop Play</button>
    </div>

    <script>
      var webSocket = new WebSocket("ws://" + window.location.hostname + ":81/");

      function updateSlider(servo, angle) {
        document.getElementById(`servo${servo}Degree`).innerText = angle;
        sendServoPosition(servo, angle);
      }

      function sendServoPosition(servo, angle) {
        webSocket.send(servo + ":" + angle);
      }

      function sendServoPosition(servo, angle) {
        webSocket.send(servo + ":" + angle);
      }

      function sendStepperPositionCW() {
      let position = parseInt(document.getElementById("stepperCW").value);
        if (!isNaN(position)) {
          webSocket.send(position.toString());
          console.log("Sent position: " + position);
          } else {
            alert("Please enter a valid number.");
          }
      }

      function sendStepperPositionCCW() {
      let position = parseInt(document.getElementById("stepperCCW").value);
        if (!isNaN(position)) {
          webSocket.send(position.toString());
          console.log("Sent position: " + position);
          } else {
            alert("Please enter a valid number.");
          }
      }

      function sendCommand(command) {
        webSocket.send("cmd:" + command);
      }

      function updateButtonState(command) {
        const recordBtn = document.getElementById("recordBtn");
        const stopRecordBtn = document.getElementById("stopRecordBtn");
        const playRecordBtn = document.getElementById("playRecordBtn");
        const stopPlayBtn = document.getElementById("stopPlayBtn");

        if (command === "record") {
          recordBtn.style.backgroundColor = "grey";
          stopRecordBtn.style.backgroundColor = "#333";
        } else if (command === "stopRecord") {
          recordBtn.style.backgroundColor = "#333";
          stopRecordBtn.style.backgroundColor = "grey";
        } else if (command === "play") {
          playRecordBtn.style.backgroundColor = "grey";
          stopPlayBtn.style.backgroundColor = "#333";
        } else if (command === "stopPlay") {
          playRecordBtn.style.backgroundColor = "#333";
          stopPlayBtn.style.backgroundColor = "grey";
        }
      }

      webSocket.onmessage = function(event) {
        // Data posisi dan warna diterima melalui WebSocket
        const data = event.data.split(",");
        const x = data[0];
        const y = data[1];
        const color = data[2];

        // Perbarui teks di halaman
        document.getElementById("objectPosition").innerText = `Position: X = ${x}, Y = ${y}`;
        document.getElementById("objectColor").innerText = `Color: ${color}`;
      };
    </script>
  </body>
</html>
)rawliteral";

// Fungsi untuk menangani permintaan root
void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void resetMotors() {
  servo1.write(0);
  servo1b.write(180);
  servo2.write(0);
  servo3.write(0);
  servo4.write(0);
  servo5.write(0);
  servo6.write(0);
  stepper.setCurrentPosition(0);
}

void setServoPosition(int servoIndex, int angle) {
  switch (servoIndex) {
    case 1:
      servo1.write(angle);
      servo1b.write(180 - angle);
      break;
    case 2: servo2.write(angle); break;
    case 3: servo3.write(angle); break;
    case 4: servo4.write(angle); break;
    case 5: servo5.write(angle); break;
    case 6: servo6.write(angle); break;
    case 7: break;
  }

  stepperPositionCW = angle;
  if (stepper.distanceToGo() != stepperPositionCW) {
    for (int i = 0; i < stepperPositionCW; i++) {
      digitalWrite(stepPin, HIGH);   // Step HIGH untuk mulai langkah
      delayMicroseconds(stepDelay);  // Tunda untuk kecepatan
      digitalWrite(stepPin, LOW);    // Step LOW untuk mengakhiri langkah
      delayMicroseconds(stepDelay);  // Tunda lagi untuk stabilitas
    }
    stepper.moveTo(stepperPositionCW);
  } else {
    stepper.stop();
  }
  Serial.println("Stepper moving to target position: " + String(stepperPositionCW));

  stepperPositionCCW = angle;
  if (stepper.distanceToGo() != stepperPositionCCW) {
    for (int i = 0; i < stepperPositionCCW; i--) {
      digitalWrite(stepPin, HIGH);   // Step HIGH untuk mulai langkah
      delayMicroseconds(stepDelay);  // Tunda untuk kecepatan
      digitalWrite(stepPin, LOW);    // Step LOW untuk mengakhiri langkah
      delayMicroseconds(stepDelay);  // Tunda lagi untuk stabilitas
    }
    stepper.moveTo(stepperPositionCCW);
  } else {
    stepper.stop();
  }
  Serial.println("Stepper moving to target position: " + String(stepperPositionCCW));
}

void recordPosition() {
  if (currentStep < MAX_MOTION_STEPS) {
    recordedPositions1[currentStep] = servo1_pos;
    recordedPositions2[currentStep] = servo1b_pos;
    recordedPositions3[currentStep] = servo2_pos;
    recordedPositions4[currentStep] = servo3_pos;
    recordedPositions5[currentStep] = servo4_pos;
    recordedPositions6[currentStep] = servo5_pos;
    recordedPositions7[currentStep] = servo6_pos;
    currentStep++;
  } else {
    Serial.println("Recording buffer full.");
  }
}

void playRecordedMotion() {
  if (millis() - lastPlayTime > 0) {
    if (playIndex < currentStep) {
      servo1.write(recordedPositions1[playIndex]);
      servo1b.write(recordedPositions2[playIndex]);
      servo2.write(recordedPositions3[playIndex]);
      servo3.write(recordedPositions4[playIndex]);
      servo4.write(recordedPositions5[playIndex]);
      servo5.write(recordedPositions6[playIndex]);
      servo6.write(recordedPositions7[playIndex]);
      playIndex++;
      lastPlayTime = millis();
    } else {
      isPlaying = false;
    }
  }
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);

    // Parsing pesan dari WebSocket (contoh: "1:90" berarti Servo 1, sudut 90 derajat)
    int servoIndex = message.substring(0, message.indexOf(':')).toInt();
    int angle = message.substring(message.indexOf(':') + 1).toInt();

    setServoPosition(servoIndex, angle);

    // Kontrol servo sesuai dengan pesan yang diterima
    switch (servoIndex) {
      case 1:
        servo1.write(angle);
        servo1b.write(180 - angle);
        break;
      case 2:
        servo2.write(angle);
        break;
      case 3:
        servo3.write(angle);
        break;
      case 4:
        servo4.write(angle);
        break;
      case 5:
        servo5.write(angle);
        break;
      case 6:
        servo6.write(angle);
        break;
      case 7:
        break;

        if (message.startsWith("cmd:")) {
          String command = message.substring(4);
          if (command == "record") {
            isRecording = true;
            isPlaying = false;  // Stop playback if recording starts
            currentStep = 0;
            Serial.println("Recording started.");
          } else if (command == "stopRecord") {
            isRecording = false;
            Serial.println("Recording stopped.");
          } else if (command == "play") {
            isPlaying = true;
            playIndex = 0;
            lastPlayTime = millis();
            Serial.println("Playing recording.");
          } else if (command == "stopPlay") {
            isPlaying = false;
            resetMotors();
            Serial.println("Playback stopped.");
          }
        }
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  digitalWrite(dirPin, HIGH);  // HIGH untuk satu arah, LOW untuk arah sebaliknya
  // Koneksi ke WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Menghubungkan ke WiFi...");
  }


  Serial.println("Terhubung ke WiFi!");
  Serial.println(WiFi.localIP());

  // Setup servo
  servo1.attach(13);   // Lower arm servo 1
  servo1b.attach(27);  // Lower arm servo 2 (terbalik)
  servo2.attach(12);   // Center arm
  servo3.attach(14);   // Upper arm
  servo4.attach(33);   // Neck gripper
  servo5.attach(25);   // Gripper

  stepper.setMaxSpeed(1000);     // Misalnya 1000 step per detik
  stepper.setAcceleration(500);  // Misalnya 500 step per detik kuadrat

  // WebSocket
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  // Setup server
  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  webSocket.loop();
  server.handleClient();

  if (isRecording) {
    recordPosition();
  }

  if (isPlaying) {
    playRecordedMotion();
  }

  stepper.run();

  delay(1000);  // Tunda 1 detik setelah selesai bergerak untuk pengujian
}
