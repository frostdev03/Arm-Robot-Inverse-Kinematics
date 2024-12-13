#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

const char* ssid = "Kipas Angin";
const char* password = "11223344";

WebServer server(80);
Servo servo1, servo2, servo3, servo4, servo5; // 5 Servo untuk lengan robot

void setup() {
  Serial.begin(115200);
  
  // Koneksi ke Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Menampilkan alamat IP ESP32
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Setup servo
  servo1.attach(13); // Pin untuk servo 1
  servo2.attach(12); // Pin untuk servo 2
  servo3.attach(14); // Pin untuk servo 3
  servo4.attach(27); // Pin untuk servo 4
  servo5.attach(26); // Pin untuk servo 5

  // Atur handler untuk request HTTP
  server.on("/", handleRoot);
  server.on("/slider", handleSlider);
  server.begin();
  Serial.println("Web server started");
}

void handleRoot() {
  // Kirim halaman web dengan 5 slider
  String html = "<h1>Kontrol 5 DOF Robot Arm</h1>";
  html += "<label>Servo 1: </label><input type='range' min='0' max='180' value='90' id='servo1' onchange='sendServo(1, this.value)'><br>";
  html += "<label>Servo 2: </label><input type='range' min='0' max='180' value='90' id='servo2' onchange='sendServo(2, this.value)'><br>";
  html += "<label>Servo 3: </label><input type='range' min='0' max='180' value='90' id='servo3' onchange='sendServo(3, this.value)'><br>";
  html += "<label>Servo 4: </label><input type='range' min='0' max='180' value='90' id='servo4' onchange='sendServo(4, this.value)'><br>";
  html += "<label>Servo 5: </label><input type='range' min='0' max='180' value='90' id='servo5' onchange='sendServo(5, this.value)'><br>";
  
  html += "<script>";
  html += "function sendServo(servo, value) {";
  html += "  var xhttp = new XMLHttpRequest();";
  html += "  xhttp.open('GET', '/slider?servo=' + servo + '&value=' + value, true);";
  html += "  xhttp.send();";
  html += "}";
  html += "</script>";
  
  server.send(200, "text/html", html);
}

void handleSlider() {
  if (server.hasArg("servo") && server.hasArg("value")) {
    int servo = server.arg("servo").toInt();
    int value = server.arg("value").toInt();
    
    // Tampilkan nilai slider di Serial Monitor
    Serial.print("Servo ");
    Serial.print(servo);
    Serial.print(": ");
    Serial.println(value);

    // Gerakkan servo sesuai dengan slider
    switch (servo) {
      case 1:
        servo1.write(value);
        break;
      case 2:
        servo2.write(value);
        break;
      case 3:
        servo3.write(value);
        break;
      case 4:
        servo4.write(value);
        break;
      case 5:
        servo5.write(value);
        break;
    }
    
    // Kirim respon
    server.send(200, "text/html", "Moved Servo " + String(servo) + " to " + String(value) + " degrees");
  } else {
    server.send(400, "text/html", "Invalid Request");
  }
}

void loop() {
  server.handleClient(); // Tangani request HTTP
}
