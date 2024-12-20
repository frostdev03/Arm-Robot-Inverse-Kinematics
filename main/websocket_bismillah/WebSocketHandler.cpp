// WebSocketHandler.cpp
#include "esp32-hal.h"
#include <cmath>
#include <ArduinoJson.h>
#include "WebSocketHandler.h"

// Servo positions array
#define MAX_SERVOS 6
int servoPositions[MAX_SERVOS] = { 0, 0, 0, 0, 0, 0};

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
  servo1.write(servoPositions[0]);       
  servo1b.write(180 - servoPositions[0]);  
  servo2.write(servoPositions[1]);        
  servo3.write(servoPositions[2]);         
  servo4.write(servoPositions[3]);      
  servo5.write(servoPositions[4]);          

  Serial.println("Servos Updated!");
}

void updateStepperPosition(int targetPosition) {
  // Set target position berdasarkan data slider
  stepper.moveTo(targetPosition);
  Serial.print("Stepper target position set to: ");
  Serial.println(targetPosition);
}

// void parseAndSetServoPositions(String message) {
//   if (message[0] != '#') {
//     Serial.println("Error: Data must start with '#'.");
//     return;
//   }

//   // Parsing data based on delimiter #
//   int servoIndex = 0;
//   int startIndex = 1;  // Start after the first '#'

//   while (servoIndex <= MAX_SERVOS) {
//     int nextIndex = message.indexOf('#', startIndex);  // Find the next '#'
//     String value = message.substring(startIndex, nextIndex);

//     if (nextIndex == -1) break;  // No more '#' found

//     if (servoIndex == MAX_SERVOS) {
//       // Stepper motor kontrol
//       int targetPosition = value.toInt();
//       updateStepperPosition(targetPosition);
//     } else {
//       servoPositions[servoIndex] = value.toInt();
//     }

//     String servoValue = message.substring(startIndex, nextIndex);  // Extract value
//     servoPositions[servoIndex] = servoValue.toInt();               // Convert to integer
//     servoIndex++;
//     startIndex = nextIndex + 1;  // Update the start index
//   }

//   // // Log received servo positions
//   // Serial.println("Updating Positions:");
//   // for (int i = 0; i < servoIndex; i++) {
//   //   Serial.printf("Servo %d: %d\n", i + 1, servoPositions[i]);
//   // }

//   // Log received positions
//   Serial.println("Updating Servos:");
//   for (int i = 0; i < MAX_SERVOS; i++) {
//     Serial.printf("Servo %d: %d\n", i + 1, servoPositions[i]);
//   }

//   // Update servos
//   updateServoPositions();
// }

void parseAndSetServoPositions(String message) {
  if (message[0] != '#') {
    Serial.println("Error: Data must start with '#'.");
    return;
  }

  int startIndex = 1;  // Start after the first '#'
  int nextIndex = message.indexOf('#', startIndex);  // Find the next '#'

  if (nextIndex == -1) {
    Serial.println("Error: Invalid message format.");
    return;
  }

  // Step 1: Parse Stepper Motor Position
  String stepperValue = message.substring(startIndex, nextIndex);
  int targetPosition = stepperValue.toInt();
  updateStepperPosition(targetPosition);

  // Step 2: Parse Servo Positions
  startIndex = nextIndex + 1;  // Update the start index
  int servoIndex = 0;

  while (servoIndex < MAX_SERVOS) {
    nextIndex = message.indexOf('#', startIndex);  // Find the next '#'
    if (nextIndex == -1) break;  // No more '#' found

    String servoValue = message.substring(startIndex, nextIndex);
    servoPositions[servoIndex] = servoValue.toInt();
    servoIndex++;
    startIndex = nextIndex + 1;  // Update the start index
  }

  // Log received positions
  Serial.printf("Stepper: %d\n", targetPosition);
  for (int i = 0; i < servoIndex; i++) {
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