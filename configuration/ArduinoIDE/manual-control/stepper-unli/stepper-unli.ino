#include <AccelStepper.h>

// Define pin connections for ESP32
const int dirPin = 25;   // You can choose any suitable GPIO pin
const int stepPin = 26;  // You can choose any suitable GPIO pin

// Define motor interface type
#define motorInterfaceType 1

// Creates an instance
AccelStepper myStepper(motorInterfaceType, stepPin, dirPin);

// Konstanta untuk jumlah langkah per derajat
const int stepsPerRevolution = 200; // Misalnya, 200 langkah per putaran penuh (sesuaikan dengan stepper Anda)
const int degreesPerRevolution = 360;
const float stepsPerDegree = (float)stepsPerRevolution / degreesPerRevolution; // Langkah per derajat

void setup() {
  // Mulai komunikasi serial untuk menerima input dari keyboard
  Serial.begin(115200);
  
  // Set motor parameters for smooth movement
  myStepper.setMaxSpeed(700);      // Adjust maximum speed (steps per second)
  myStepper.setAcceleration(300);  // Adjust acceleration (steps per second squared)

  Serial.println("Input degree to move the stepper motor (0-360):");
}

void loop() {
  // Cek apakah ada input dari Serial Monitor
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Membaca input sampai 'Enter'
    int degree = input.toInt();  // Konversi input menjadi integer
    
    if (degree >= 0 && degree <= 360) {
      // Hitung langkah target berdasarkan input derajat
      int targetSteps = degree * stepsPerDegree;
      Serial.print("Moving to position: ");
      Serial.print(degree);
      Serial.println(" degrees");
      
      // Gerakkan stepper ke posisi target
      myStepper.moveTo(targetSteps);
    } else {
      Serial.println("Please input a value between 0 and 360.");
    }
  }

  // Move the motor to the target position
  myStepper.run();
}
