#include <Arduino.h>
#if defined(ESP8266)
/* ESP8266 Dependencies */
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#elif defined(ESP32)
/* ESP32 Dependencies */
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#endif
#include <ESPDash.h>
#include <ESP32Servo.h>

// Define servo pins
#define SERVO1_PIN 3   // Servo 1 and 2 (lower arm)
#define SERVO2_PIN 10  // center arm
#define SERVO3_PIN 9   // upper arm
#define SERVO4_PIN 14  // neck gripper
#define SERVO5_PIN 26  // gripper
#define SERVO6_PIN 27  // base

// Create servo objects
Servo servo1, servo2, servo3, servo4, servo5, servo6;

// Initial positions for the servos
int servo1_pos = 0, servo2_pos = 0, servo3_pos = 0, servo4_pos = 0, servo5_pos = 0, servo6_pos = 0;

// Recording parameters
const int MAX_MOTION_STEPS = 500;
int recordedPositions1[MAX_MOTION_STEPS], recordedPositions2[MAX_MOTION_STEPS], recordedPositions3[MAX_MOTION_STEPS];
int recordedPositions4[MAX_MOTION_STEPS], recordedPositions5[MAX_MOTION_STEPS], recordedPositions6[MAX_MOTION_STEPS];

bool isRecording = false, isPlaying = false;
int currentStep = 0, playIndex = 0;
unsigned long lastPlayTime = 0;

unsigned long lastUpdateTime = 0;
const unsigned long updateInterval = 50;

/* WiFi Credentials */
const char* ssid = "meja makan";
const char* password = "satuduatiga";

/* Start Webserver */
AsyncWebServer server(80);

/* Attach ESP-DASH to AsyncWebServer */
ESPDash dashboard(&server);

// Create sliders for each part of the robot arm
Card sliderLowerArmRight(&dashboard, SLIDER_CARD, "Lower Arm Right", "", 0, 180);
Card sliderLowerArmLeft(&dashboard, SLIDER_CARD, "Lower Arm Left", "", 0, 180);
Card sliderCenterArm(&dashboard, SLIDER_CARD, "Center Arm", "", 0, 180);
Card sliderUpperArm(&dashboard, SLIDER_CARD, "Upper Arm", "", 0, 180);
Card sliderNeckGripper(&dashboard, SLIDER_CARD, "Neck Gripper", "", 0, 360);
Card sliderGripper(&dashboard, SLIDER_CARD, "Gripper", "", 0, 180);

// Buttons for recording and playing actions
Card buttonRecord(&dashboard, BUTTON_CARD, "Record");
Card buttonStopRecord(&dashboard, BUTTON_CARD, "Stop Record");
Card buttonPlay(&dashboard, BUTTON_CARD, "Play Recorded");
Card buttonStopPlay(&dashboard, BUTTON_CARD, "Stop Playing");

// Button for toggling the built-in LED
Card buttonToggleLED(&dashboard, BUTTON_CARD, "LED Toggle");

// Variable to track LED state
bool ledState = false;

void setup() {
  Serial.begin(115200);

  // Initialize the LED pin (built-in LED)
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);  // Ensure the LED is off initially

  // Attach servos to pins
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);
  servo4.attach(SERVO4_PIN);
  servo5.attach(SERVO5_PIN);
  servo6.attach(SERVO6_PIN);

  // Set initial positions
  moveAllServos();

  /* Connect WiFi */
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  if (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.printf("WiFi Failed!\n");
    return;
  }
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  /* Attach callbacks for sliders */
  sliderLowerArmRight.attachCallback([&](int value) {
    servo1_pos = value;
    servo2_pos = value;  // Combined movement
    moveAllServos();
    sliderLowerArmRight.update(value);
    dashboard.sendUpdates();
  });

  sliderLowerArmLeft.attachCallback([&](int value) {
    servo3_pos = value;
    moveAllServos();
    sliderLowerArmLeft.update(value);
    dashboard.sendUpdates();
  });

  sliderCenterArm.attachCallback([&](int value) {
    servo4_pos = value;
    moveAllServos();
    sliderCenterArm.update(value);
    dashboard.sendUpdates();
  });

  sliderUpperArm.attachCallback([&](int value) {
    servo5_pos = value;
    moveAllServos();
    sliderUpperArm.update(value);
    dashboard.sendUpdates();
  });

  sliderNeckGripper.attachCallback([&](int value) {
    servo6_pos = value;
    moveAllServos();
    sliderNeckGripper.update(value);
    dashboard.sendUpdates();
  });

  sliderGripper.attachCallback([&](int value) {
    servo4_pos = value;
    servo5_pos = value;
    moveAllServos();
    sliderGripper.update(value);
    sliderUpperArm.update(value);
    dashboard.sendUpdates();
  });

  /* Attach button callbacks for recording and playback */
  buttonRecord.attachCallback([&](int value) {
    if (value == 1) {
      Serial.println("Recording started...");
      isRecording = true;
      currentStep = 0;
    }
    buttonRecord.update(value);
    dashboard.sendUpdates();
  });

  buttonStopRecord.attachCallback([&](int value) {
    if (value == 1 && isRecording) {
      Serial.println("Recording stopped.");
      isRecording = false;
    }
    buttonStopRecord.update(value);
    dashboard.sendUpdates();
  });

  buttonPlay.attachCallback([&](int value) {
    if (value == 1 && currentStep > 0) {
      Serial.println("Playing recorded motion...");
      isPlaying = true;
      playIndex = 0;
      lastPlayTime = millis();
    }
    buttonPlay.update(value);
    dashboard.sendUpdates();
  });

  buttonStopPlay.attachCallback([&](int value) {
    if (value == 1 && isPlaying) {
      Serial.println("Playback stopped.");
      isPlaying = false;
    }
    buttonStopPlay.update(value);
    dashboard.sendUpdates();
  });

  // Attach callback for LED toggle button
  buttonToggleLED.attachCallback([&](int value) {
    if (value == 1) {
      ledState = !ledState;  // Toggle the LED staten
      digitalWrite(LED_BUILTIN, ledState ? HIGH : LOW);
      Serial.println(ledState ? "LED ON" : "LED OFF");
    }
    buttonToggleLED.update(value);
    dashboard.sendUpdates();
  });

  server.begin();
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
  if (millis() - lastPlayTime > 500) {
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
      isPlaying = false;
    }
  }
}

void loop() {
  // Update servos periodically without blocking
  if (millis() - lastUpdateTime >= updateInterval) {
    lastUpdateTime = millis();
    if (isRecording) {
      recordPosition();
    }

    if (isPlaying) {
      playRecordedMotion();
    }

    moveAllServos();  // Make sure to update servo positions in a non-blocking way
  }

}
