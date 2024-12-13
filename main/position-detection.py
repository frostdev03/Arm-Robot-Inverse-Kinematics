import cv2
import numpy as np

# URL streaming dari kamera ESP32-CAM
url = 'http://192.168.137.74:81/stream'

# Definisi warna dalam format HSV
hsv_colors = {
    'Blue': ([66, 52, 67], [255, 255, 255]),
    'Yellow': ([0, 51, 123], [51, 255, 255]),
    'Red': ([0, 63, 88], [255, 255, 255]),
    'Green': ([0, 95, 53], [104, 255, 255])
}

# Membuka kamera
cap = cv2.VideoCapture(url)

# Kernel untuk morfologi
kernel = np.ones((5, 5), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Ubah ke grayscale dan tambahkan Gaussian Blur untuk mengurangi noise (filtering)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Ubah ke HSV untuk deteksi warna
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Deteksi tepi dengan Canny
    edges = cv2.Canny(blurred, 0, 100)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel, iterations=1)

    # Mencari kontur pada tepi
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cube_detected = False
    cube_color = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 200:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4:  # Bentuk persegi
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h

                if 0.9 <= aspect_ratio <= 1.1:  # Aspek rasio mendekati 1
                    cube_detected = True
                    cube_center_x = x + w // 2
                    cube_center_y = y + h // 2

                    # Ambil ROI untuk deteksi warna
                    roi = hsv_frame[y:y + h, x:x + w]
                    for color_name, (lower_hsv, upper_hsv) in hsv_colors.items():
                        lower_bound = np.array(lower_hsv)
                        upper_bound = np.array(upper_hsv)

                        # Masking warna dan operasi morfologi tambahan
                        mask = cv2.inRange(roi, lower_bound, upper_bound)
                        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                        mask_area = cv2.countNonZero(mask)

                        # Jika area warna >50%, anggap sebagai warna kubus
                        if mask_area >= (w * h) * 0.5:
                            cube_color = color_name
                            break

                    # Tampilkan label warna dan koordinat di atas kubus
                    if cube_color:
                        label = f"{cube_color} Cube"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Gambarkan crosshair di pusat kubus dan tampilkan koordinat
                        cv2.drawMarker(frame, (cube_center_x, cube_center_y), (255, 0, 0), cv2.MARKER_CROSS, 20, 2)
                        cv2.putText(frame, f"X: {cube_center_x}, Y: {cube_center_y}", (cube_center_x + 10, cube_center_y - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Gambarkan garis bantu sumbu X dan Y
                    cv2.line(frame, (cube_center_x, 0), (cube_center_x, frame.shape[0]), (255, 255, 0), 1)
                    cv2.line(frame, (0, cube_center_y), (frame.shape[1], cube_center_y), (255, 255, 0), 1)

    # Jika kubus dan warnanya terdeteksi, tampilkan teks deteksi
    if cube_detected and cube_color:
        cv2.putText(frame, f"{cube_color} Cube Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Tampilkan hasil
    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
