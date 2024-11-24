#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ESP32Servo.h>

// Konfigurasi WiFi
const char* ssid = "Kipas Angin";
const char* password = "11223344";

// WebSocket server
WebSocketsServer webSocket = WebSocketsServer(81);

// Servo untuk neck gripper
Servo neckGripper;
const int neckGripperPin = 26; // Ganti dengan pin servo Anda

void setup() {
  Serial.begin(115200);

  // Menghubungkan ke WiFi
  WiFi.begin(ssid, password);
  Serial.print("Menghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi terhubung!");
  Serial.print("Alamat IP ESP32: ");
  Serial.println(WiFi.localIP());

  // Inisialisasi WebSocket
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  Serial.println("WebSocket server berjalan pada port 81");

  // Inisialisasi servo neck gripper
  neckGripper.attach(neckGripperPin);
  neckGripper.write(90); // Posisi awal
}

void loop() {
  webSocket.loop();
}

// Fungsi callback untuk menangani event WebSocket
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);
    Serial.print("Pesan diterima: ");
    Serial.println(message);

    // Memeriksa pesan untuk mengontrol neck gripper
    if (message.startsWith("neck_gripper:")) {
      int angle = message.substring(13).toInt(); // Mengambil sudut dari pesan
      if (angle >= 0 && angle <= 180) {
        neckGripper.write(angle);
        Serial.print("Sudut gripper diatur ke: ");
        Serial.println(angle);
      } else {
        Serial.println("Sudut tidak valid. Harus antara 0-180.");
      }
    }
  }
}
