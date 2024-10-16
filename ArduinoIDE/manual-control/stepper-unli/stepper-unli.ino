#include <AccelStepper.h>

// Define stepper motor connections and motor interface type.
// Motor interface type:
// 1 - Driver (step and direction pins)
// 4 - Half-step method (4 pins controlling the coils directly)
#define motorInterfaceType 1

// Define motor pin connections
#define dirPin 26    // Pin for direction
#define stepPin 13  // Pin for step

// Create a new instance of the AccelStepper class:
AccelStepper stepper(motorInterfaceType, stepPin, dirPin);

void setup() {
  // Set the maximum speed and acceleration:
  stepper.setMaxSpeed(1000);     // Set maximum speed (steps per second)
  stepper.setAcceleration(500);  // Set acceleration rate (steps per second^2)
  
  // Optional: Set initial speed (if you want to set a constant speed)
  stepper.setSpeed(600);  // Set a constant speed (steps per second)
}

void loop() {
  // Move the motor continuously at the constant speed set in setup()
  stepper.runSpeed();  // Run motor at constant speed indefinitely
}
