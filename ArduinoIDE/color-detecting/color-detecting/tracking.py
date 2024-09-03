import cv2
import urllib.request
import numpy as np

def nothing(x):
    pass

# Ganti alamat IP di bawah ini sesuai dengan yang ditampilkan di Serial Monitor
url = 'http://192.168.226.201/cam-lo.jpg'

# Membuat jendela untuk menampilkan video dan trackbar
cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)

cv2.namedWindow("Tracking")
cv2.createTrackbar("LH", "Tracking", 0, 255, nothing)
cv2.createTrackbar("LS", "Tracking", 0, 255, nothing)
cv2.createTrackbar("LV", "Tracking", 0, 255, nothing)
cv2.createTrackbar("UH", "Tracking", 255, 255, nothing)
cv2.createTrackbar("US", "Tracking", 255, 255, nothing)
cv2.createTrackbar("UV", "Tracking", 255, 255, nothing)

# Membuat header HTTP untuk menyamar sebagai web browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Referer": "http://192.168.226.201/"  # Ganti dengan IP ESP32-CAM Anda
}

while True:
    try:
        # Mengirim request dengan header khusus
        req = urllib.request.Request(url, headers=headers)
        img_resp = urllib.request.urlopen(req)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)

        # Jika gambar tidak bisa di-decode, print pesan error
        if frame is None:
            print("Failed to decode image")
            continue
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Mendapatkan nilai dari trackbar untuk deteksi warna
        l_h = cv2.getTrackbarPos("LH", "Tracking")
        l_s = cv2.getTrackbarPos("LS", "Tracking")
        l_v = cv2.getTrackbarPos("LV", "Tracking")

        u_h = cv2.getTrackbarPos("UH", "Tracking")
        u_s = cv2.getTrackbarPos("US", "Tracking")
        u_v = cv2.getTrackbarPos("UV", "Tracking")

        l_b = np.array([l_h, l_s, l_v])
        u_b = np.array([u_h, u_s, u_v])

        # Membuat mask untuk deteksi warna
        mask = cv2.inRange(hsv, l_b, u_b)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        # Menampilkan hasil
        cv2.imshow("live transmission", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("res", res)
        
        # Keluar dari loop jika tombol 'q' ditekan
        key = cv2.waitKey(5)
        if key == ord('q'):
            break
    
    except Exception as e:
        print(f"Error: {e}")
        break

cv2.destroyAllWindows()
