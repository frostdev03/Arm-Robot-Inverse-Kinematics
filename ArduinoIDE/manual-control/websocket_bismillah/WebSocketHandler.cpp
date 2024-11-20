// WebSocketHandler.cpp
#include "esp32-hal.h"
#include <cmath>
#include <ArduinoJson.h>
#include "WebSocketHandler.h"

// Recording variables
bool isRecording = false;
bool isPlaying = false;
int currentStep = 0;
int playIndex = 0;

unsigned long lastPlayTime = 0;

// Definisikan WebSocket pada port 81
WebSocketsServer webSocket = WebSocketsServer(81);

void initWebSocket() {
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

// Fungsi untuk menangani event WebSocket
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);
    Serial.printf("[%u] Received Text: %s\n", num, payload);

    // Jika pesan berbentuk JSON, parsing menggunakan ArduinoJson
    if (message.startsWith("{")) {
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, message);
      if (!error) {
        if (doc.containsKey("servo") && doc.containsKey("angle")) {
          int servoIndex = doc["servo"];
          int angle = doc["angle"];

          // Kontrol servo sesuai dengan pesan JSON
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
              stepper.moveTo(angle);
              break;
          }
        } else if (doc.containsKey("command")) {
          String command = doc["command"];
          if (command == "record") {
            isRecording = true;
          } else if (command == "stopRecord") {
            isRecording = false;
          } else if (command == "play") {
            isPlaying = true;
            playIndex = 0;
          } else if (command == "stopPlay") {
            isPlaying = false;
          }
        }
      } else {
        Serial.println("Failed to parse JSON!");
      }
    }
  }
}