import cv2

# Ganti alamat IP di bawah ini sesuai dengan yang ditampilkan di Serial Monitor
url = 'http://192.168.212.147:81/stream'  # Pastikan Anda menggunakan alamat URL streaming yang benar

# Membuka koneksi ke stream video
cap = cv2.VideoCapture(url)

cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)

while True:
    ret, frame = cap.read()

    # Cek apakah frame berhasil diambil
    if not ret:
        print("Failed to grab frame")
        break

    # Menampilkan frame
    cv2.imshow("live transmission", frame)

    # Keluar dari loop jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Melepaskan resource
cap.release()
cv2.destroyAllWindows()
