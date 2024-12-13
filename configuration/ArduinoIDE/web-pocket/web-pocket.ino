#include <WiFi.h>
#include <ESP32Servo.h>  // Library untuk Servo
#include <WebSocketsServer.h>  // Library untuk WebSocket

// Deklarasi pin untuk Servo
#define SERVO_PIN1 22
#define SERVO_PIN2 23

Servo servo1;
Servo servo2;

// Inisialisasi variabel Wi-Fi
const char* ssid = "Kipas Angin";  // Ganti dengan SSID WiFi kamu
const char* password = "11223344";  // Ganti dengan password WiFi kamu

// Inisialisasi WebSocket server
WebSocketsServer webSocket = WebSocketsServer(81);

void setup() {
  Serial.begin(115200);

  // Setup Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Inisialisasi WebSocket
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  // Setup Servo
  servo1.attach(SERVO_PIN1);
  servo2.attach(SERVO_PIN2);

  // Set posisi awal servo
  servo1.write(90);  // Sudut awal 90 derajat
  servo2.write(90);
}

void loop() {
  // Mendengarkan pesan WebSocket
  webSocket.loop();
}

// Fungsi ini menangani event WebSocket
void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*) payload);

    if (message.startsWith("servo1:")) {
      int angle = message.substring(7).toInt();  // Mengambil nilai setelah "servo1:"
      servo1.write(angle);  // Atur sudut servo 1
      Serial.println("Servo 1: " + String(angle));
    } else if (message.startsWith("servo2:")) {
      int angle = message.substring(7).toInt();  // Mengambil nilai setelah "servo2:"
      servo2.write(angle);  // Atur sudut servo 2
      Serial.println("Servo 2: " + String(angle));
    }
  }
}

