// WebSocketHandler.cpp
#include "esp32-hal.h"
#include <cmath>
#include <ArduinoJson.h>
#include "WebSocketHandler.h"

// Servo positions array
#define MAX_SERVOS 6
int servoPositions[MAX_SERVOS] = { 0, 0, 0, 0, 0, 0 };

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

void updateServoPositions() {
  lowerRight.write(servoPositions[0]);       // Servo 1 (base)
  lowerLeft.write(180 - servoPositions[0]);  // Servo 2 (lower arm)
  centerArm.write(servoPositions[1]);        // Servo 3 (center arm)
  upperArm.write(servoPositions[2]);         // Servo 4 (upper arm)
  neckGripper.write(servoPositions[3]);      // Servo 5 (neck gripper)
  gripper.write(servoPositions[4]);          // Servo 6 (gripper)

  Serial.println("Servos Updated!");
}

void updateStepperPosition(int targetPosition) {
  // Set target position berdasarkan data slider
  stepper.moveTo(targetPosition);
  Serial.print("Stepper target position set to: ");
  Serial.println(targetPosition);
}


void parseAndSetServoPositions(String message) {
  if (message[0] != '#') {
    Serial.println("Error: Data must start with '#'.");
    return;
  }

  // Parsing data based on delimiter #
  int servoIndex = 0;
  int startIndex = 1;  // Start after the first '#'

  while (servoIndex <= MAX_SERVOS) {
    int nextIndex = message.indexOf('#', startIndex);  // Find the next '#'
    String value = message.substring(startIndex, nextIndex);

    if (nextIndex == -1) break;  // No more '#' found

    if (servoIndex == MAX_SERVOS) {
      // Stepper motor kontrol
      int targetPosition = value.toInt();
      updateStepperPosition(targetPosition);
    } else {
      servoPositions[servoIndex] = value.toInt();
    }

    String servoValue = message.substring(startIndex, nextIndex);  // Extract value
    servoPositions[servoIndex] = servoValue.toInt();               // Convert to integer
    servoIndex++;
    startIndex = nextIndex + 1;  // Update the start index
  }

  // // Log received servo positions
  // Serial.println("Updating Positions:");
  // for (int i = 0; i < servoIndex; i++) {
  //   Serial.printf("Servo %d: %d\n", i + 1, servoPositions[i]);
  // }

  // Log received positions
  Serial.println("Updating Servos:");
  for (int i = 0; i < MAX_SERVOS; i++) {
    Serial.printf("Servo %d: %d\n", i + 1, servoPositions[i]);
  }

  // Update servos
  updateServoPositions();
}

void handleCommand(String command) {
  if (command == "record") {
    isRecording = true;
    Serial.println("Recording started.");
  } else if (command == "stopRecord") {
    isRecording = false;
    Serial.println("Recording stopped.");
  } else if (command == "play") {
    isPlaying = true;
    playIndex = 0;
    Serial.println("Playback started.");
  } else if (command == "stopPlay") {
    isPlaying = false;
    Serial.println("Playback stopped.");
  }
}

// Fungsi untuk menangani event WebSocket
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char*)payload);
    Serial.printf("[%u] Pesan diterima: %s\n", num, payload);

    // Jika pesan berbentuk JSON, parsing menggunakan ArduinoJson
    if (message.startsWith("#")) {
      parseAndSetServoPositions(message);
    } else if (message.startsWith("{")) {
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, message);
      if (!error) {
        //data dari json
        if (doc.containsKey("servo") && doc.containsKey("angle")) {
          int servoIndex = doc["servo"];
          int angle = doc["angle"];
          if (servoIndex >= 1 && servoIndex <= MAX_SERVOS) {
            servoPositions[servoIndex - 1] = angle;
            updateServoPositions();
          } else {
            Serial.println("Invalid Servo Index!");
          }

          // Kontrol servo sesuai dengan pesan JSON
          switch (servoIndex) {
            case 1:
              lowerRight.write(angle);
              lowerLeft.write(180 - angle);
              break;
            case 2:
              centerArm.write(angle);
              break;
            case 3:
              upperArm.write(angle);
              break;
            case 4:
              neckGripper.write(angle);
              break;
            case 5:
              gripper.write(angle);
              break;
            case 7:
              stepper.moveTo(angle);
              break;
          }
        } else if (doc.containsKey("command")) {
          String command = doc["command"];
          handleCommand(command);
        }
      } else {
        Serial.println("Failed to parse JSON!");
      }
    }
  }
}