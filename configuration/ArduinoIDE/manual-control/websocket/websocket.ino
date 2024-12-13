#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <ESP32Servo.h>

const char* ssid = "Kipas Angin";
const char* password = "11223344";

WebServer server(80);            // HTTP server pada port 80
WebSocketsServer webSocket(81);  // WebSocket server pada port 81

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

// Halaman HTML di-embed langsung di dalam kode
const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
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
      <label for="servo1">Lower Arm:</label>
      <input
        type="range"
        id="servo1"
        min="0"
        max="180"
        oninput="sendServoPosition(1, this.value)"
      />
    </div>
    <div>
      <label for="servo2">Center Arm:</label>
      <input
        type="range"
        id="servo2"
        min="0"
        max="180"
        oninput="sendServoPosition(2, this.value)"
      />
    </div>
    <div>
      <label for="servo3">Upper Arm:</label>
      <input
        type="range"
        id="servo3"
        min="0"
        max="180"
        oninput="sendServoPosition(3, this.value)"
      />
    </div>
    <div>
      <label for="servo4">Neck Gripper:</label>
      <input
        type="range"
        id="servo4"
        min="0"
        max="180"
        oninput="sendServoPosition(4, this.value)"
      />
    </div>
    <div>
      <label for="servo5">Gripper:</label>
      <input
        type="range"
        id="servo5"
        min="0"
        max="180"
        oninput="sendServoPosition(5, this.value)"
      />
    </div>

    <!-- Button Section -->
    <div class="button-container">
      <button id="recordBtn" onclick="sendCommand('record')">Record</button>
      <button id="stopRecordBtn" onclick="sendCommand('stopRecord')">Stop Record</button>
      <button id="playRecordBtn" onclick="sendCommand('play')">Play Record</button>
      <button id="stopPlayBtn" onclick="sendCommand('stopPlay')">Stop Play</button>
      <button id="blinkBtn" onclick="sendCommand('blink')">Blink</button>
    </div>

    <script>
      var webSocket = new WebSocket("ws://" + window.location.hostname + ":81/");

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

// PID
float Kp = 0.5, Ki = 0.1, Kd = 0.05;
float prevError = 0, integral = 0;

void moveRobot(int currentPosX, int targetPosX) {
  float error = targetPosX - currentPosX;  // Menghitung error (selisih posisi)
  integral += error;                       // Akumulasi error untuk komponen integral
  float derivative = error - prevError;    // Menghitung kecepatan perubahan error (komponen derivatif)
  prevError = error;

  float output = Kp * error + Ki * integral + Kd * derivative;

  if (output > 0) {
  } else if (output < 0) {
  }
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
    }

    //input x & y menerima dari pytong
    int delimiter = message.indexOf(',');
    int x = message.substring(0, delimiter).toInt();
    int y = message.substring(delimiter + 1).toInt();

    moveRobot(x, y);
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
  servo1.attach(13);  //left lower
  servo2.attach(12);  //center
  servo3.attach(14);  //upper
  servo4.attach(27);  //neck
  servo5.attach(26);  //gripper
  servo6.attach(25);  //right lower

  // Atur handler untuk URL root "/"
  server.on("/", handleRoot);

  // Mulai server HTTP dan WebSocket
  server.begin();
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  server.handleClient();  // Menangani request HTTP
  webSocket.loop();       // Menangani komunikasi WebSocket
}

// Fuzzy
// Fuzzy* fuzzy = new Fuzzy();

// // Membuat FuzzySet untuk posisi objek (misalnya, Left, Center, Right)
// FuzzySet* left = new FuzzySet(-30, -15, -15, 0);
// FuzzySet* center = new FuzzySet(-10, 0, 0, 10);
// FuzzySet* right = new FuzzySet(0, 15, 15, 30);

// // Menentukan output (kecepatan robot)
// FuzzySet* slow = new FuzzySet(-10, 0, 0, 10);
// FuzzySet* fast = new FuzzySet(10, 20, 20, 30);

// // Membuat aturan fuzzy
// fuzzy->addFuzzyRule(new FuzzyRule(1, fuzzy->createFuzzyRuleCondition("Position", FuzzyRuleCondition::LEFT), fuzzy->createFuzzyRuleAction("Speed", FuzzyRuleAction::FAST)));
// fuzzy->addFuzzyRule(new FuzzyRule(2, fuzzy->createFuzzyRuleCondition("Position", FuzzyRuleCondition::RIGHT), fuzzy->createFuzzyRuleAction("Speed", FuzzyRuleAction::FAST)));
// fuzzy->addFuzzyRule(new FuzzyRule(3, fuzzy->createFuzzyRuleCondition("Position", FuzzyRuleCondition::CENTER), fuzzy->createFuzzyRuleAction("Speed", FuzzyRuleAction::SLOW)));
