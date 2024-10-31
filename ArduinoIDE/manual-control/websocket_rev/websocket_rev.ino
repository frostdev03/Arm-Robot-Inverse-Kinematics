#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <ESP32Servo.h>
#include <AccelStepper.h>

const char* ssid = "Kipas Angin";
const char* password = "11223344";

#define motorInterfaceType 1
#define dirPin 26  // Pin for direction
#define stepPin 35

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
      <label for="stepper">Stepper Motor Speed: <span id="stepperDegree">0</span>°</label>
      <input
        type="range"
        id="stepper"
        min="0"
        max="360"
        value="0"
        oninput="updateSlider(7, this.value)"
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

      function updateSlider(servo, angle) {
        document.getElementById(`servo${servo}Degree`).innerText = angle;
        sendServoPosition(servo, angle);

        if (servo === 7) {
          document.getElementById(`stepperDegree`).innerText = angle;  // Update Stepper angle display
        }
        sendServoPosition(servo, angle);
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
    </script>
  </body>
</html>
)rawliteral";

// Fungsi untuk menangani permintaan root
void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);

    // Parsing pesan dari WebSocket (contoh: "1:90" berarti Servo 1, sudut 90 derajat)
    int servoIndex = message.substring(0, message.indexOf(':')).toInt();
    int angle = message.substring(message.indexOf(':') + 1).toInt();

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
        if (angle != stepper.currentPosition()) {
          stepper.moveTo(angle * (stepper.maxSpeed() / 360));  // Hanya bergerak jika ada perubahan posisi
        }
        break;
    }
  }
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
  servo1.attach(13);   // Lower arm servo 1
  servo1b.attach(27);  // Lower arm servo 2 (terbalik)
  servo2.attach(12);   // Center arm
  servo3.attach(14);   // Upper arm
  servo4.attach(33);   // Neck gripper
  servo5.attach(25);   // Gripper

  stepper.setCurrentPosition(0);  // Set posisi awal ke 0
  stepper.setMaxSpeed(500);       // Set kecepatan maksimum motor stepper
  stepper.setAcceleration(500);   // Set acceleration rate (steps per second^2)


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

  stepper.run();  // Memastikan stepper bergerak ke posisi yang diinginkan
}
