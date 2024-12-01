// WebSocketHandler.cpp
#include "esp32-hal.h"
#include <ArduinoJson.h>
#include "ws-handler.h"

#define dirPin 26
#define stepPin 32

// AccelStepper stepper;  // Gunakan instance yang sama dari file utama
// Servo lowerRight, lowerLeft, centerArm, upperArm, neckGripper, gripper;

// Servo positions array
// #define MAX_SERVOS 6
int servoPositions[MAX_SERVOS] = { 0, 0, 0, 0, 0, 0 };

// Recording variables
bool isRecording = false;
bool isPlaying = false;
int currentStep = 0;
int playIndex = 0;
unsigned long lastPlayTime = 0;

int stepsToMove = 200;  // Total langkah yang diinginkan
int stepDelay = 1000;

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


// void updateStepperPosition(int targetPosition) {
//   // Set target position berdasarkan data slider
//   stepper.moveTo(targetPosition);
//   Serial.print("Stepper target position set to: ");
//   Serial.println(targetPosition);
// }
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
//       setStepperPosition(targetPosition);
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
//   // Serial.println("Updating Servos:");
//   // for (int i = 0; i < MAX_SERVOS; i++) {
//   //   Serial.printf("Servo %d: %d\n", i + 1, servoPositions[i]);
//   // }

//   Serial.print("Parsed values: ");
//   for (int i = 0; i < 6; i++) {
//     Serial.print(values[i]);
//     Serial.print(" ");
//   }
//   Serial.println();


//   // Update servos
//   updateServoPositions();
// }

// void parseAndSetServoPositions(String message) {
//   if (message[0] != '#') {
//     Serial.println("Error: Data must start with '#'.");
//     return;
//   }

//   // Array untuk menyimpan nilai parsing
//   int values[MAX_SERVOS] = {0}; // Deklarasikan dan inisialisasi array
//   int servoIndex = 0;
//   int startIndex = 1; // Mulai setelah '#' pertama

//   while (servoIndex < MAX_SERVOS) {
//     int nextIndex = message.indexOf('#', startIndex); // Cari '#' berikutnya
//     if (nextIndex == -1) break; // Jika tidak ada '#' lagi

//     String value = message.substring(startIndex, nextIndex); // Ambil substring nilai
//     values[servoIndex] = value.toInt(); // Konversi nilai ke integer
//     servoIndex++;
//     startIndex = nextIndex + 1; // Update start index
//   }

//   // Log nilai yang diterima
//   Serial.print("Parsed values: ");
//   for (int i = 0; i < MAX_SERVOS; i++) {
//     Serial.print(values[i]);
//     Serial.print(" ");
//   }
//   Serial.println();

//   // Update posisi servos menggunakan nilai dari array
//   for (int i = 0; i < MAX_SERVOS; i++) {
//     servoPositions[i] = values[i];
//   }
//   updateServoPositions();
// }

void parseAndSetServoPositions(String message) {
  if (message[0] != '#') {
    Serial.println("Error: Data must start with '#'!");
    return;
  }

  // Parsing data based on delimiter #
  int servoIndex = 0;
  int startIndex = 1;  // Start after the first '#'

  while (true) {
    int nextIndex = message.indexOf('#', startIndex);  // Find the next '#'
    String value = (nextIndex == -1) 
                     ? message.substring(startIndex)  // Get the remaining value if no more '#'
                     : message.substring(startIndex, nextIndex); // Get value between delimiters

    if (servoIndex < MAX_SERVOS) {
      // Parsing for servos
      servoPositions[servoIndex] = value.toInt();
      Serial.printf("Servo %d set to %d\n", servoIndex + 1, servoPositions[servoIndex]);
    } else if (servoIndex == MAX_SERVOS) {
      // Parsing for stepper motor
      int targetPosition = value.toInt();
      setStepperPosition(targetPosition);
      Serial.printf("Stepper target position set to %d\n", targetPosition);
    } else {
      // Extra data beyond the expected number of servos and stepper
      Serial.println("Warning: Extra data received. Ignored.");
      break;
    }

    // If no more '#' found, exit the loop
    if (nextIndex == -1) break;

    // Move to the next value
    servoIndex++;
    startIndex = nextIndex + 1;
  }

  // Update servos with parsed positions
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
// void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
//   if (type == WStype_TEXT) {
//     String message = String((char*)payload);
//     Serial.printf("[%u] Pesan diterima: %s\n", num, payload);
//     int position = message.toInt();
//     setStepperPosition(position);

//     // Jika pesan berbentuk JSON, parsing menggunakan ArduinoJson
//     if (message.startsWith("#")) {
//       parseAndSetServoPositions(message);
//     } else if (message.startsWith("{")) {
//       StaticJsonDocument<200> doc;
//       DeserializationError error = deserializeJson(doc, message);
//       if (!error) {
//         //data dari json
//         if (doc.containsKey("servo") && doc.containsKey("angle")) {
//           int servoIndex = doc["servo"];
//           int angle = doc["angle"];
//           if (servoIndex >= 1 && servoIndex <= MAX_SERVOS) {
//             servoPositions[servoIndex - 1] = angle;
//             updateServoPositions();
//           } else {
//             Serial.println("Invalid Servo Index!");
//           }
//           // Kontrol servo sesuai dengan pesan JSON
//           switch (servoIndex) {
//             case 1: lowerRight.write(angle); lowerLeft.write(180 - angle); break;
//             case 2: centerArm.write(angle); break;
//             case 3: upperArm.write(angle); break;
//             case 4: neckGripper.write(angle); break;
//             case 5: gripper.write(angle); break;
//             case 7: stepper.moveTo(angle * 2); break;
//           }
//         } else if (doc.containsKey("command")) {
//           String command = doc["command"];
//           handleCommand(command);
//         }
//       } else {
//         Serial.println("Failed to parse JSON!");
//       }
//     }
//   }
// }

void webSocketEvent(uint8_t num, WStype_t type, uint8_t *payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char *)payload);

    // Parsing input dengan format #val#val#val#
    if (message.startsWith("#")) {
      message.remove(0, 1);       // Hilangkan tanda #
      message.replace("#", ",");  // Ganti '#' dengan ','
      int values[6];
      int index = 0;

      while (message.length() > 0 && index < 6) {
        int separatorIndex = message.indexOf(',');
        if (separatorIndex == -1) separatorIndex = message.length();

        String valueStr = message.substring(0, separatorIndex);
        values[index++] = valueStr.toInt();
        message.remove(0, separatorIndex + 1);
      }

      // Sesuaikan nilai ke perangkat keras
      stepper.moveTo(values[0]);     // Stepper
      lowerRight.write(values[1]);   // Lower Right
      lowerLeft.write(values[2]);    // Lower Left
      centerArm.write(values[3]);    // Center Arm
      upperArm.write(values[4]);     // Upper Arm
      neckGripper.write(values[5]);  // Neck Gripper
    }
  }
}
