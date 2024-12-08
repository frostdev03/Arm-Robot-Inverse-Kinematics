// WebSocketHandler.h
#ifndef WEBSOCKETHANDLER_H
#define WEBSOCKETHANDLER_H

#include <WebSocketsServer.h>
#include <ESP32Servo.h>
#include <AccelStepper.h>

// Deklarasi WebSocket server pada port 81
extern WebSocketsServer webSocket;

// Deklarasi untuk objek servo dan stepper
extern Servo servo1, servo1b, servo2, servo3, servo4, servo5, servo6;
extern AccelStepper stepper;

extern bool isRecording;
extern bool isPlaying;
extern int currentStep;
extern int playIndex;

extern unsigned long lastPlayTime;

// Deklarasi fungsi WebSocket
void initWebSocket();
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length);

#endif
