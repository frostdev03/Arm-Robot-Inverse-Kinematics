import cv2
import numpy as np

# Membuka kamera laptop
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Cek apakah frame berhasil diambil
    if not ret:
        print("Failed to grab frame")
        break

    # Ubah gambar ke grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Gunakan Canny edge detection untuk mendeteksi tepi objek
    edges = cv2.Canny(gray, 50, 150)

    # Cari kontur dari gambar dengan tepi yang terdeteksi
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Variable untuk menyimpan status apakah kubus terdeteksi atau tidak
    cube_detected = False

    for contour in contours:
        # Menghitung area kontur untuk mengabaikan objek kecil
        area = cv2.contourArea(contour)
        if area > 1000:  # Filter area kecil
            # Menerapkan aproksimasi poligon pada kontur
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            # Jika aproksimasi memiliki 4 titik, itu mungkin sebuah persegi (kubus dalam 2D)
            if len(approx) == 4:
                # Tandai bahwa kubus telah terdeteksi
                cube_detected = True

                # Gambar kotak di sekitar objek yang terdeteksi
                x, y, w, h = cv2.boundingRect(approx)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frame, "Cube", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Jika ada kubus yang terdeteksi, tampilkan teks "Cube Detected"
    if cube_detected:
        cv2.putText(frame, "Cube Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Tampilkan frame asli dan tepi yang terdeteksi
    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edges)

    # Keluar dari loop jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Lepaskan resource
cap.release()
cv2.destroyAllWindows()
