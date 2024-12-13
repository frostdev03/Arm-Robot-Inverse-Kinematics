#include <Servo.h>  // Library untuk mengontrol servo

Servo myServo;  // Membuat objek servo
int angle = 0;  // Posisi awal servo
int increment = 5;  // Besar perubahan sudut

void setup() {
  // Inisialisasi Serial Monitor untuk debugging
  Serial.begin(115200);

  // Menghubungkan servo ke pin GPIO 12
  myServo.attach(9);  

  // Menggerakkan servo ke posisi awal (0 derajat)
  myServo.write(angle);
}

void loop() {
  // Menggerakkan servo ke sudut saat ini
  myServo.write(angle);

  // Menunggu 100 ms agar gerakan lebih halus
  delay(100);

  // Update sudut servo
  angle += increment;

  // Jika sudut mencapai 180 atau 0, ubah arah
  if (angle >= 180 || angle <= 0) {
    increment = -increment;  // Ubah arah gerakan
  }

  // Debug: Cetak posisi sudut servo di Serial Monitor
  Serial.println("Sudut Servo: " + String(angle));
}
