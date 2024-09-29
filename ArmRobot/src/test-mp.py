import machine
import time

led = machine.Pin(4, machine.Pin.OUT)  # Sesuaikan dengan pin LED pada ESP32-CAM

while True:
    led.value(not led.value())  # Toggle LED
    time.sleep(1)  # Delay 1 detik
