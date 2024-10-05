#include <Servo.h>

// Define servo pins
#define SERVO1_PIN 3  // Servo 1 and 2 (bottom arm, above base)
#define SERVO2_PIN 13  // Same as SERVO1_PIN for combined movement
#define SERVO3_PIN 9  // Middle arm
#define SERVO4_PIN 14  // Lower neck
#define SERVO5_PIN 26  // Neck gripper (special range)
#define SERVO6_PIN 27  // Gripper/claw

// Create servo objects
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

// Initial positions for the servos
int servo1_pos = 0;
int servo2_pos = 0;
int servo3_pos = 0;
int servo4_pos = 0;
int servo5_pos = 0;
int servo6_pos = 0;

// Constants for recording
const int MAX_MOTION_STEPS = 100;  // Maximum number of steps that can be recorded

// Arrays to store recorded positions
int recordedPositions1[MAX_MOTION_STEPS];
int recordedPositions2[MAX_MOTION_STEPS];
int recordedPositions3[MAX_MOTION_STEPS];
int recordedPositions4[MAX_MOTION_STEPS];
int recordedPositions5[MAX_MOTION_STEPS];
int recordedPositions6[MAX_MOTION_STEPS];

// Recording variables
bool isRecording = false;
bool isPlaying = false;
int currentStep = 0;
int playIndex = 0;

unsigned long lastPlayTime = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Attach servos to pins
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);
  servo4.attach(SERVO4_PIN);
  servo5.attach(SERVO5_PIN);
  servo6.attach(SERVO6_PIN);

  // Set initial positions
  moveAllServos();
}

void moveAllServos() {
  servo1.write(servo1_pos);
  servo2.write(servo2_pos);
  servo3.write(servo3_pos);
  servo4.write(servo4_pos);
  servo5.write(servo5_pos);
  servo6.write(servo6_pos);
}

void recordPosition() {
  if (currentStep < MAX_MOTION_STEPS) {
    recordedPositions1[currentStep] = servo1_pos;
    recordedPositions2[currentStep] = servo2_pos;
    recordedPositions3[currentStep] = servo3_pos;
    recordedPositions4[currentStep] = servo4_pos;
    recordedPositions5[currentStep] = servo5_pos;
    recordedPositions6[currentStep] = servo6_pos;
    currentStep++;
  } else {
    Serial.println("Recording buffer full.");
  }
}

void playRecordedMotion() {
  if (millis() - lastPlayTime > 500) {  // Play motion every 500 ms
    if (playIndex < currentStep) {
      servo1.write(recordedPositions1[playIndex]);
      servo2.write(recordedPositions2[playIndex]);
      servo3.write(recordedPositions3[playIndex]);
      servo4.write(recordedPositions4[playIndex]);
      servo5.write(recordedPositions5[playIndex]);
      servo6.write(recordedPositions6[playIndex]);
      playIndex++;
      lastPlayTime = millis();
    } else {
      isPlaying = false;  // Stop playing when done
    }
  }
}

void loop() {
  // Check for input from the serial monitor
  if (Serial.available()) {
    char command = Serial.read();  // Read the command

    switch (command) {
      case 'r':  // Start recording
        isRecording = true;
        isPlaying = false;
        currentStep = 0;  // Reset step counter
        Serial.println("Recording started");
        break;

      case 's':  // Stop recording
        isRecording = false;
        Serial.println("Recording stopped");
        break;

      case 'p':  // Play recorded motion
        if (currentStep > 0) {
          isPlaying = true;
          playIndex = 0;
          lastPlayTime = millis();
          Serial.println("Playing recorded motion");
        } else {
          Serial.println("No motion recorded");
        }
        break;

      case 'o':  // Stop playing
        isPlaying = false;
        Serial.println("Playing stopped");
        break;

      case '1':  // Move servo 1 and 2 together
        servo1_pos = min(servo1_pos + 20, 180);
        servo2_pos = min(servo2_pos + 20, 180);
        moveAllServos();
        Serial.print("Servo 1 & 2 Position: ");
        Serial.println(servo1_pos);
        break;

      case '2':  // Move servo 3 (middle arm)
        servo3_pos = min(servo3_pos + 20, 180);
        moveAllServos();
        Serial.print("Servo 3 Posi2tion: ");
        Serial.println(servo3_pos);
        break;

      case '3':  // Move servo 3 (middle arm)
        servo3_pos = min(servo3_pos - 20, 180);
        moveAllServos();
        Serial.print("Servo 3 Posi2tion: ");
        Serial.println(servo3_pos);
        break;

      case '0':
        servo3_pos = 0;
        moveAllServos();
        Serial.print("Servo 3 Posi2tion: ");
        Serial.println(servo3_pos);
        break;

      // Add more servo controls as needed

      default:
        Serial.println("Invalid input!");
        break;
    }
  }

  // Record motion while recording is active
  if (isRecording) {
    recordPosition();
    delay(100);  // Add a delay to record at intervals
  }

  // Play recorded motion if play is active
  if (isPlaying) {
    playRecordedMotion();
  }

  delay(100);  // Small delay to make sure serial input is read properly
}
