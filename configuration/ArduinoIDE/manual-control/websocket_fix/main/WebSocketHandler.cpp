#include "esp32-hal.h"
#include <cmath>
// WebSocketHandler.cpp
#include "WebSocketHandler.h"

// Recording variables
// bool isRecording = false;
// bool isPlaying = false;
// int currentStep = 0;
// int playIndex = 0;

// unsigned long lastPlayTime = 0;

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

    // if(message.startsWith("cmd:")){
    //   String c = message.substring(4);
    //   if (c == "record") {
    //     isRecording = true;
    //     isPlaying = false;
    //     currentStep = 0;
    //     Serial.println("Recording started");
    //   } else if (c == "stopRecord"){
    //     isRecording = false;
    //     Serial.printf("Recording stopped");
    //   } else if (c == "play"){
    //     isPlaying = true;
    //     isRecording = false;
    //     lastPlayTime = millis();
    //     Serial.println("Playing recorded");
    //   } else {
    //     isPlaying = false;
    //     Serial.println("Playback stopped");
    //   }
  }
}

