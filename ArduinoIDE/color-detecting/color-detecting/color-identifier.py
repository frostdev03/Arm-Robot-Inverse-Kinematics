import cv2
import numpy as np

# Ganti alamat IP di bawah ini sesuai dengan yang ditampilkan di Serial Monitor
url = 'http://192.168.3.201:81/stream'  # Pastikan Anda menggunakan alamat URL streaming yang benar

# Membuka koneksi ke stream video
cap = cv2.VideoCapture(url)

cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("HSV transmission", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Mask", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Result", cv2.WINDOW_AUTOSIZE)

# Trackbar untuk menyesuaikan nilai HSV
cv2.createTrackbar("LH", "HSV transmission", 0, 255, lambda x: None)
cv2.createTrackbar("LS", "HSV transmission", 0, 255, lambda x: None)
cv2.createTrackbar("LV", "HSV transmission", 0, 255, lambda x: None)
cv2.createTrackbar("UH", "HSV transmission", 255, 255, lambda x: None)
cv2.createTrackbar("US", "HSV transmission", 255, 255, lambda x: None)
cv2.createTrackbar("UV", "HSV transmission", 255, 255, lambda x: None)

while True:
    ret, frame = cap.read()

    # Cek apakah frame berhasil diambil
    if not ret:
        print("Failed to grab frame")
        break

    # Konversi frame dari BGR ke HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Membaca nilai dari trackbar
    l_h = cv2.getTrackbarPos("LH", "HSV transmission")
    l_s = cv2.getTrackbarPos("LS", "HSV transmission")
    l_v = cv2.getTrackbarPos("LV", "HSV transmission")
    u_h = cv2.getTrackbarPos("UH", "HSV transmission")
    u_s = cv2.getTrackbarPos("US", "HSV transmission")
    u_v = cv2.getTrackbarPos("UV", "HSV transmission")

    # Membuat batasan nilai HSV
    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    # Membuat mask untuk deteksi warna
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Menampilkan frame asli, frame dalam format HSV, mask, dan hasil deteksi warna
    cv2.imshow("live transmission", frame)
    cv2.imshow("HSV transmission", hsv_frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    # Keluar dari loop jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Melepaskan resource
cap.release()
cv2.destroyAllWindows()
