#include <Servo.h>

//Define servo pins
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
int servo5_pos = 0; // Different range if needed
int servo6_pos = 0;

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
  servo1.write(servo1_pos);
  servo2.write(servo2_pos);
  servo3.write(servo3_pos);
  servo4.write(servo4_pos);
  servo5.write(servo5_pos);
  servo6.write(servo6_pos);
}

void loop() {
  // Check for input from the serial monitor
  if (Serial.available()) {
    char command = Serial.read();  // Read the command

    switch (command) {
      // case '1':  // Move servo 1 and 2 together by 20 degrees
      //   servo1_pos = min(servo1_pos + 20, 180);  // Ensure it doesn't go over 180
      //   servo2_pos = min(servo2_pos + 20, 180);
      //   servo1.write(servo1_pos);
      //   servo2.write(servo2_pos);
      //   Serial.print("Servo 1 & 2 Position: ");
      //   Serial.println(servo1_pos);
      //   break;
      
      // case '2':  // Move servo 1 and 2 together by 20 degrees
      //   servo1_pos = min(servo1_pos - 20, 180);  // Ensure it doesn't go over 180
      //   servo2_pos = min(servo2_pos - 20, 180);
      //   servo1.write(servo1_pos);
      //   servo2.write(servo2_pos);
      //   Serial.print("Servo 1 & 2 Position: ");
      //   Serial.println(servo1_pos);
      // break;

      case '2':  // Move servo 3 (middle arm)
        servo3_pos = min(servo3_pos + 20, 360);
        servo3.write(servo3_pos);
        Serial.print("Servo 3 Position: ");
        Serial.println(servo3_pos);
        break;

      case '3':  // Move servo 3 (middle arm)
        servo3_pos = min(servo3_pos - 20, 3600);
        servo3.write(servo3_pos);
        Serial.print("Servo 3 Position: ");
        Serial.println(servo3_pos);
        break;
      

      // case '3':  // Move servo 4 (lower neck)
      //   servo4_pos = min(servo4_pos + 20, 180);
      //   servo4.write(servo4_pos);
      //   Serial.print("Servo 4 Position: ");
      //   Serial.println(servo4_pos);
      //   break;

      // case '4':  // Move servo 5 (neck gripper, special range)
      //   servo5_pos = min(servo5_pos + 20, 180);  // Change this if the servo has a smaller range
      //   servo5.write(servo5_pos);
      //   Serial.print("Servo 5 Position: ");
      //   Serial.println(servo5_pos);
      //   break;

      // case '5':  // Move servo 6 (gripper/claw)
      //   servo6_pos = min(servo6_pos + 20, 180);
      //   servo6.write(servo6_pos);
      //   Serial.print("Servo 6 Position: ");
      //   Serial.println(servo6_pos);
        // break;

      // default:
      //   Serial.println("Invalid input! Use 1-5 for servos.");
      //   break;
    }
  }

  delay(100);  // Small delay to make sure serial input is read properly
}
