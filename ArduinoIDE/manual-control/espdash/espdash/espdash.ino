#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ESPDash.h>
#include <ESP32Servo.h>

// Define Wi-Fi credentials
const char* ssid = "ceragem";       // Ganti dengan nama Wi-Fi kamu
const char* password = "batugiok";  // Ganti dengan password Wi-Fi kamu

// Initialize the server and dashboard
AsyncWebServer server(80);
ESPDash dashboard(&server);

// Define servos
Servo servo1;  // Servo untuk Pin 23
Servo servo2;  // Servo untuk Pin 22

// Define the pins for the servos
#define SERVO1_PIN 23
#define SERVO2_PIN 22

// **Declare Card instead of Slider**
Card* servo1Card;
Card* servo2Card;

// Function to initialize Wi-Fi
void initWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected! IP Address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  // Start serial communication
  Serial.begin(115200);

  // Attach servos to respective pins
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  // Initialize Wi-Fi
  initWiFi();

  // **Create card widgets**
  // Replace the Card instantiation with the correct arguments
  servo1Card = new Card(&dashboard, 1, "Servo 1 Position", "°", 0, 180, 1);
  servo2Card = new Card(&dashboard, 1, "Servo 2 Position", "°", 0, 180, 1);

  // Add the cards to the dashboard
  dashboard.addCard(servo1Card);
  dashboard.addCard(servo2Card);


  // Set card callback functions to update servos when slider values change
  servo1Card->attach([&](int value) {
    servo1.write(value);
    Serial.print("Servo 1 position: ");
    Serial.println(value);
  });

  servo2Card->attach([&](int value) {
    servo2.write(value);
    Serial.print("Servo 2 position: ");
    Serial.println(value);
  });

  // Start the server
  server.begin();
}

void loop() {
  // No code needed in the loop
}
