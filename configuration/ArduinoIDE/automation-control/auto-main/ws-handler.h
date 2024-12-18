// WebSocketHandler.h
#ifndef WEBSOCKETHANDLER_H
#define WEBSOCKETHANDLER_H

#include <WebSocketsServer.h>
#include <ESP32Servo.h>
#include <AccelStepper.h>

// Recording variables
extern bool isRecording;
extern bool isPlaying;
extern int currentStep;
extern int playIndex;

extern unsigned long lastPlayTime;

// Deklarasi WebSocket server pada port 81
extern WebSocketsServer webSocket;

// Deklarasi untuk objek servo dan stepper
extern Servo lowerRight, lowerLeft, centerArm, upperArm, neckGripper, gripper;
extern AccelStepper stepper;

extern int stepperPosition;  // Total langkah yang diinginkan

// Deklarasi fungsi WebSocket
void initWebSocket();
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length);

#endif