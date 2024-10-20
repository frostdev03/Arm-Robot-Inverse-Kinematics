#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <ESP32Servo.h>

const char* ssid = "RM.TERAPI";
const char* password = "12345678";

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
<html>
  <head>
    <title>Robot Arm Control</title>
  </head>
  <body>
    <h1>Robot Arm Control</h1>
    <div>
      <label for="servo1">Lower Arm:</label>
      <input type="range" id="servo1" min="0" max="180" oninput="sendServoPosition(1, this.value)">
    </div>
    <div>
      <label for="servo2">Center Arm:</label>
      <input type="range" id="servo2" min="0" max="180" oninput="sendServoPosition(2, this.value)">
    </div>
    <div>
      <label for="servo3">Upper Arm:</label>
      <input type="range" id="servo3" min="0" max="180" oninput="sendServoPosition(3, this.value)">
    </div>
    <div>
      <label for="servo4">Neck Gripper:</label>
      <input type="range" id="servo4" min="0" max="180" oninput="sendServoPosition(4, this.value)">
    </div>
    <div>
      <label for="servo5">Gripper:</label>
      <input type="range" id="servo5" min="0" max="180" oninput="sendServoPosition(5, this.value)">
    </div>
    <script>
      var webSocket = new WebSocket('ws://' + window.location.hostname + ':81/');
      function sendServoPosition(servo, angle) {
        webSocket.send(servo + ':' + angle);
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
