//websocket_bismillah.ino
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <AccelStepper.h>
#include "ws-handler.h"  

const char* ssid = "Kipas Angin";
const char* password = "11223344";

#define motorInterfaceType 1
#define dirPin 26  
#define stepPin 32

AccelStepper stepper(motorInterfaceType, stepPin, dirPin);

WebServer server(80);  // HTTP server pada port 80

// Objek servo
Servo lowerRight, lowerLeft, centerArm, upperArm, neckGripper, gripper;

// Initial positions for the servos
int lowerRight_pos = 0;
int lowerLeft_pos = 0;
int centerArm_pos = 0;
int upperArm_pos = 0;
int neckGripper_pos = 0;
int gripper_pos = 0;

// Constants for recording
const int MAX_MOTION_STEPS = 200;  // Maximum number of steps that can be recorded

// Arrays to store recorded positions
int recordedPositions1[MAX_MOTION_STEPS];
int recordedPositions1b[MAX_MOTION_STEPS];
int recordedPositions2[MAX_MOTION_STEPS];
int recordedPositions3[MAX_MOTION_STEPS];
int recordedPositions4[MAX_MOTION_STEPS];
int recordedPositions5[MAX_MOTION_STEPS];
int recordedPositions6[MAX_MOTION_STEPS];

// // Recording variables
// bool isRecording = false;
// bool isPlaying = false;
// int currentStep = 0;
// int playIndex = 0;

// unsigned long lastPlayTime = 0;

// Halaman HTML
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

    <div id="objectInfo">
      <h2>Object Position and Color</h2>
      <p id="objectPosition">Position: -</p>
      <p id="objectColor">Color: -</p>
    </div>

    <div>
      <label for="lowerRight">Lower Arm: <span id="lowerRightDegree">0</span>°</label>
      <input
        type="range"
        id="lowerRight"
        min="0"
        max="180"
        value="0"
        oninput="updateSlider(1, this.value)"
      />
    </div>

    <div>
      <label for="centerArm">Center Arm: <span id="centerArmDegree">0</span>°</label>
      <input
        type="range"
        id="centerArm"
        min="0"
        max="180"
        value="0"
        oninput="updateSlider(2, this.value)"
      />
    </div>

    <div>
      <label for="upperArm">Upper Arm: <span id="upperArmDegree">0</span>°</label>
      <input
        type="range"
        id="upperArm"
        min="0"
        max="180"
        value="0"
        oninput="updateSlider(3, this.value)"
      />
    </div>

    <div>
      <label for="neckGripper">Neck Gripper: <span id="neckGripperDegree">0</span>°</label>
      <input
        type="range"
        id="neckGripper"
        min="0"
        max="360"
        value="0"
        oninput="updateSlider(4, this.value)"
      />
    </div>

    <div>
      <label for="gripper">Gripper: <span id="gripperDegree">0</span>°</label>
      <input
        type="range"
        id="gripper"
        min="0"
        max="180"
        value="0"
        oninput="updateSlider(5, this.value)"
      />
    </div>

    <div>
      <label for="stepper">Stepper Position: <span id="stepperDegree">0</span>°</label>
      <input
        type="range"
        id="stepper"
        min="0"
        max="360"
        value="0"
        oninput="updateSlider(6, this.value)"
      />
    </div>

    <!-- Button Section -->
    <div class="button-container">
      <button id="recordBtn" onclick="sendCommand('record')">Record</button>
      <button id="stopRecordBtn" onclick="sendCommand('stopRecord')">Stop Record</button>
      <button id="playRecordBtn" onclick="sendCommand('play')">Play Record</button>
      <button id="stopPlayBtn" onclick="sendCommand('stopPlay')">Stop Play</button>
    </div>

    <script>
      var webSocket = new WebSocket("ws://" + window.location.hostname + ":81/");

      // function updateSlider(servo, angle) {
      //   document.getElementById(`servo${servo}Degree`).innerText = angle;
      //   // Kirim data ke WebSocket
      //   webSocket.send(JSON.stringify({ servo: servo, angle: parseInt(angle) }));
      // }

      function updateSlider(servo, angle) {
        if (servo === 6) {
          document.getElementById("stepperDegree").innerText = angle;
        } else {
          document.getElementById(`servo${servo}Degree`).innerText = angle;
        }
        // Kirim data ke WebSocket
        webSocket.send(JSON.stringify({ servo: servo, angle: parseInt(angle) }));
      }


      function sendServoPosition(servo, angle) {
        webSocket.send(servo + ":" + angle);
      }

      function sendServoPosition(servo, angle) {
        webSocket.send(servo + ":" + angle);
      }

      function sendCommand(command) {
        webSocket.send("cmd:" + command);
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

void moveAllServos() {
  lowerRight.write(lowerRight_pos);
  lowerLeft.write(lowerLeft_pos);
  centerArm.write(centerArm_pos);
  upperArm.write(upperArm_pos);
  neckGripper.write(neckGripper_pos);
  gripper.write(gripper_pos);
}

void setup() {
  Serial.begin(115200);

  // Koneksi ke WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Menghubungkan ke WiFi...");
  }
  Serial.println("Terhubung ke WiFi!");
  Serial.println(WiFi.localIP());

  // Setup servo
  lowerRight.attach(13);   // Lower arm 
  lowerLeft.attach(27);  // Lower arm servo 2 (terbalik)
  centerArm.attach(12);   // Center arm
  upperArm.attach(14);   // Upper arm
  neckGripper.attach(33);   // Neck gripper
  gripper.attach(25);   // Gripper

  moveAllServos();
  
  // Stepper setup
  stepper.setCurrentPosition(0);
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(500);
  
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  // digitalWrite(dirPin, HIGH);
  // stepper.setMaxSpeed(1000);
  // stepper.setAcceleration(500);

  // Inisialisasi WebSocket
  initWebSocket();

  // String jsonData = "{\"x\": 100, \"y\": 150, \"color\": \"Blue\"}";
  // webSocket.broadcastTXT(jsonData);  // Kirim data ke semua client yang terhubung

  // Setup server
  server.on("/", handleRoot);
  server.begin();
}

void recordPosition() {
  if (currentStep < MAX_MOTION_STEPS) {
    recordedPositions1[currentStep] = lowerRight_pos;
    recordedPositions1b[currentStep] = lowerLeft_pos;
    recordedPositions2[currentStep] = centerArm_pos;
    recordedPositions3[currentStep] = upperArm_pos;
    recordedPositions4[currentStep] = neckGripper_pos;
    recordedPositions5[currentStep] = gripper_pos;
    currentStep++;
  } else {
    Serial.println("Recording buffer full.");
  }
}

void playRecordedMotion() {
  if (millis() - lastPlayTime > 0) {  // Play motion every 500 ms
    if (playIndex < currentStep) {
      lowerRight.write(recordedPositions1[playIndex]);
      lowerLeft.write(recordedPositions1b[playIndex]);
      centerArm.write(recordedPositions2[playIndex]);
      upperArm.write(recordedPositions3[playIndex]);
      neckGripper.write(recordedPositions4[playIndex]);
      gripper.write(recordedPositions5[playIndex]);
      playIndex++;
      lastPlayTime = millis();
    } else {
      isPlaying = false;  // Stop playing when done
    }
  }
}

void loop() {
  webSocket.loop();  // WebSocket loop
  server.handleClient();
  stepper.run();  

  if (isRecording) recordPosition();
  if (isPlaying) playRecordedMotion();
}