#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <AccelStepper.h>

const char* ssid = "Kipas Angin";
const char* password = "11223344";

int stepperPosition = 0;  // Total langkah yang diinginkan

#define motorInterfaceType 1
#define dirPin 26
#define stepPin 23

AccelStepper stepper(motorInterfaceType, stepPin, dirPin);

WebServer server(80);
WebSocketsServer webSocket(81);

int stepsToMove = 200;  // Total langkah yang diinginkan
int stepDelay = 1000;

const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robot Arm Control</title>
</head>
<body>
    <h1>Robot Arm Control</h1>
    <div>
        <label for="stepperPosition">Target Position (steps):</label>
        <input type="number" id="stepperPosition" placeholder="Enter target position" />
        <button id="send" onclick="sendStepperPosition()">Move Stepper</button>
    </div>

    <!-- Pindahkan JavaScript ke bagian bawah -->
    <script>
        var webSocket = new WebSocket("ws://" + window.location.hostname + ":81/");
        
        function sendStepperPosition() {
            let position = parseInt(document.getElementById("stepperPosition").value);
            if (!isNaN(position)) {
                webSocket.send(position.toString());
                console.log("Sent position: " + position);
            } else {
                alert("Please enter a valid number.");
            }
        }
    </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void setStepperPosition(int position) {
  stepperPosition = position;
  if (stepper.distanceToGo() != stepperPosition) {
    for (int i = 0; i < stepperPosition; i++) {
      digitalWrite(stepPin, HIGH);   // Step HIGH untuk mulai langkah
      delayMicroseconds(stepDelay);  // Tunda untuk kecepatan
      digitalWrite(stepPin, LOW);    // Step LOW untuk mengakhiri langkah
      delayMicroseconds(stepDelay);  // Tunda lagi untuk stabilitas
    }
    stepper.moveTo(stepperPosition);
  } else {
    stepper.stop();
  }
  Serial.println("Stepper moving to target position: " + String(stepperPosition));
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);
    int position = message.toInt();
    setStepperPosition(position);
    Serial.println("Received position from WebSocket: " + String(position));
  }
}

void setup() {
  Serial.begin(115200);


  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  digitalWrite(dirPin, HIGH);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  Serial.println(WiFi.localIP());

  // stepper.moveTo(0);
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(500);

  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  webSocket.loop();
  server.handleClient();
  stepper.run();
}
