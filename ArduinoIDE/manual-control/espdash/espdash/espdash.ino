#include <WiFi.h>
// #include <ESPAsyncWebServer.h>
// #include <AsyncTCP.h>
#include <ESP32Servo.h>
#include <ESPDash.h>  // Library untuk dashboard

const char* ssid = "Kipas Angin";          // Ganti dengan SSID Wi-Fi Anda
const char* password = "11223344"; 

// Servo pins
const int servoPin1 = 23;
const int servoPin2 = 22;

// Create Servo objects
Servo servo1;
Servo servo2;

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

// Create ESP-DASH Dashboard
ESPDash dashboard(&server);

// Create two slider cards
Card slider1(&dashboard, "Servo 1", "", "slider", 0, 180); // Slider untuk Servo 1
Card slider2(&dashboard, "Servo 2", "", "slider", 0, 180); // Slider untuk Servo 2

void setup() {
  // Start serial communication
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Attach servos to pins
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);

  // Set up callbacks for sliders
  slider1.attachCallback([&](int value) {
    servo1.write(value);  // Move Servo 1 based on slider value
    Serial.print("Servo 1 position: ");
    Serial.println(value);
  });

  slider2.attachCallback([&](int value) {
    servo2.write(value);  // Move Servo 2 based on slider value
    Serial.print("Servo 2 position: ");
    Serial.println(value);
  });

  // Start server
  server.begin();
}

void loop() {
  // No need for loop code, ESP-Dash handles everything
}
