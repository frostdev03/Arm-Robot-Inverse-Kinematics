import cv2
import numpy as np

# Nilai HSV untuk warna-warna yang ingin dideteksi
hsv_colors = {
    'Blue': ([56, 40, 102], [118, 192, 255]),
    'Yellow': ([10, 20, 187], [255, 255, 255]),
    'Red': ([111, 37, 81], [255, 255, 255])
}

# Membuka kamera laptop
cap = cv2.VideoCapture(0)

# Kernel untuk morfologi
kernel = np.ones((5,5), np.uint8)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    edges = cv2.Canny(gray, 50, 150)
    
    # Tambahkan dilasi dan erosi untuk memperbaiki tepi
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cube_detected = False
    cube_color = None

    # Deteksi kubus berdasarkan kontur
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4:  # Bentuk persegi panjang
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h

                # Jika aspek rasio mendekati 1, tandai sebagai kubus
                if 0.9 <= aspect_ratio <= 1.1:
                    cube_detected = True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                    # Deteksi warna di dalam area kotak yang terdeteksi
                    roi = hsv_frame[y:y+h, x:x+w]

                    for color_name, (lower_hsv, upper_hsv) in hsv_colors.items():
                        lower_bound = np.array(lower_hsv)
                        upper_bound = np.array(upper_hsv)

                        mask = cv2.inRange(roi, lower_bound, upper_bound)
                        mask_area = cv2.countNonZero(mask)

                        # Jika area warna yang terdeteksi cukup besar, anggap itu adalah warna kubus
                        if mask_area > (w * h) * 0.5:  # jika lebih dari 50% dari area kotak
                            cube_color = color_name
                            break

                    # Tampilkan label warna kubus di atas kubus yang terdeteksi
                    if cube_color:
                        label = f"Kubus {cube_color}"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Jika kubus dan warnanya terdeteksi, tampilkan teks deteksi
    if cube_detected and cube_color:
        cv2.putText(frame, f"{cube_color} Cube Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Menampilkan frame dengan deteksi warna dan kubus
    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
