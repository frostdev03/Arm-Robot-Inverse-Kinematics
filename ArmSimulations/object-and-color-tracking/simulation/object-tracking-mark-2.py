import cv2
import numpy as np

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
    edges = cv2.Canny(gray, 50, 150)
    
    # Tambahkan dilasi dan erosi untuk memperbaiki tepi
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cube_detected = False

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
                    cv2.putText(frame, "Cube", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if cube_detected:
        cv2.putText(frame, "Cube Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
