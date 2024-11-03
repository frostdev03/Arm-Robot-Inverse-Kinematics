import cv2
import numpy as np

# Nilai HSV untuk warna-warna yang ingin dideteksi
hsv_colors = {
    'Biru': ([56, 40, 102], [118, 192, 255]),
    'Kuning': ([10, 20, 187], [255, 255, 255]),
    'Merah': ([111, 37, 81], [255, 255, 255])
}

# Membuka koneksi ke webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Konversi frame dari BGR ke HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Loop untuk setiap warna dan mendeteksi sesuai nilai HSV
    for color_name, (lower_hsv, upper_hsv) in hsv_colors.items():
        lower_bound = np.array(lower_hsv)
        upper_bound = np.array(upper_hsv)

        # Membuat mask untuk warna yang sesuai
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Temukan kontur (bentuk) dari area yang terdeteksi
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Hanya menampilkan kotak untuk objek dengan area lebih besar dari threshold tertentu
            area = cv2.contourArea(contour)
            if area > 1000:
                # Gambar kotak di sekitar area yang terdeteksi
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # Tambahkan label warna di atas kotak
                cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Menampilkan frame asli dengan kotak dan label
    cv2.imshow("Deteksi Warna", frame)

    # Keluar dari loop jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Melepaskan resource
cap.release()
cv2.destroyAllWindows()
