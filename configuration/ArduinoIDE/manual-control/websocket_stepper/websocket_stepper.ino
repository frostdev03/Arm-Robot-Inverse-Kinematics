#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <AccelStepper.h>

const char* ssid = "ceragem";     // WiFi SSID
const char* password = "batugiok";  // WiFi Password

#define DIR_PIN 26    // Direction pin
#define STEP_PIN 35   // Step pin

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

WebServer server(80);            // HTTP server on port 80
WebSocketsServer webSocket(81);  // WebSocket server on port 81

void handleRoot() {
  String htmlPage = R"rawliteral(
  <!DOCTYPE html>
  <html>
  <head>
      <title>Stepper Motor Control</title>
      <style>
          body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
          h1 { color: #333; }
          input[type="range"] { width: 80%; }
          label { display: block; margin-top: 20px; font-size: 1.2em; }
      </style>
  </head>
  <body>
      <h1>Stepper Motor Control</h1>
      <label for="positionSlider">Position (Steps)</label>
      <input type="range" id="positionSlider" min="-1000" max="1000" value="0" oninput="sendPosition(this.value)">
      <div id="positionValue">0</div>

      <script>
          var webSocket = new WebSocket("ws://" + window.location.hostname + ":81/");
          
          webSocket.onmessage = function(event) {
              document.getElementById("positionValue").innerText = event.data;
          };

          function sendPosition(position) {
              webSocket.send(position);
          }
      </script>
  </body>
  </html>
  )rawliteral";

  server.send(200, "text/html", htmlPage);
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);
    int position = message.toInt();  // Convert message to integer position
    stepper.moveTo(position);        // Set target position
    // webSocket.broadcastTXT(String(position));  // Send back the position for display
  }
}

void setup() {
  Serial.begin(115200);

  // WiFi setup
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  Serial.println(WiFi.localIP());

  // Set up server routes
  server.on("/", handleRoot);
  server.begin();
  Serial.println("HTTP server started!");

  // WebSocket setup
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  
  // Initialize the stepper motor
  stepper.setMaxSpeed(1000);   // Set max speed
  stepper.setAcceleration(500); // Set acceleration for smoother movement
}

void loop() {
  server.handleClient();
  webSocket.loop();
  stepper.run();  // Run the stepper to reach the target position
}
