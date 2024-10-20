#define BLYNK_TEMPLATE_ID "TMPL6-ZUIJ36d"
#define BLYNK_TEMPLATE_NAME "ESPRobotika"
#define BLYNK_AUTH_TOKEN "tRa7f0ZfRPZ-vbEq6YU199iv3tddeYJV"

#define BLYNK_PRINT Serial
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <ESP32Servo.h>

// Auth Token dari Blynk
// char auth[] = "Auth_Token_dari_Email";

// Credentials WiFi
char ssid[] = "RM.TERAPI";
char pass[] = "12345678";

// Inisialisasi Servo
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

// Virtual Pin dari Blynk untuk kontrol slider
BLYNK_WRITE(V0) {
  int pos = param.asInt();  // Membaca nilai slider
  servo1.write(pos);        // Menggerakkan Servo 1
}

BLYNK_WRITE(V1) {
  int pos = param.asInt();
  servo2.write(pos);        // Menggerakkan Servo 2
}

BLYNK_WRITE(V2) {
  int pos = param.asInt();
  servo3.write(pos);        // Menggerakkan Servo 3
}

BLYNK_WRITE(V3) {
  int pos = param.asInt();
  servo4.write(pos);        // Menggerakkan Servo 4
}

BLYNK_WRITE(V4) {
  int pos = param.asInt();
  servo5.write(pos);        // Menggerakkan Servo 5
}

BLYNK_WRITE(V6) {
  int pos = param.asInt();
  servo6.write(pos);        // Menggerakkan Servo 6
}

void setup() {
  // Menghubungkan ke Serial Monitor
  Serial.begin(115200);

  // Menghubungkan ke Blynk dan WiFi
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Menghubungkan Servo ke pin ESP32
  servo1.attach(3);  // Pin untuk Servo 1
  servo2.attach(10);  // Pin untuk Servo 2
  servo3.attach(9);  // Pin untuk Servo 3
  servo4.attach(14);  // Pin untuk Servo 4
  servo5.attach(26);  // Pin untuk Servo 5
  servo6.attach(27);  // Pin untuk Servo 6
}

void loop() {
  Blynk.run();  // Menjalankan Blynk
}
