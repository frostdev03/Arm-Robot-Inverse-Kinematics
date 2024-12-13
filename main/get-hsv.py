import cv2
import numpy as np

url = 'http://192.168.137.134:81/stream'  # Pastikan Anda menggunakan URL streaming yang benar

cap = cv2.VideoCapture(url)

cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("HSV transmission", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Mask", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Result", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("LH", "HSV transmission", 0, 255, lambda x: None)
cv2.createTrackbar("LS", "HSV transmission", 0, 255, lambda x: None)
cv2.createTrackbar("LV", "HSV transmission", 0, 255, lambda x: None)
cv2.createTrackbar("UH", "HSV transmission", 255, 255, lambda x: None)
cv2.createTrackbar("US", "HSV transmission", 255, 255, lambda x: None)
cv2.createTrackbar("UV", "HSV transmission", 255, 255, lambda x: None)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    l_h = cv2.getTrackbarPos("LH", "HSV transmission")
    l_s = cv2.getTrackbarPos("LS", "HSV transmission")
    l_v = cv2.getTrackbarPos("LV", "HSV transmission")
    u_h = cv2.getTrackbarPos("UH", "HSV transmission")
    u_s = cv2.getTrackbarPos("US", "HSV transmission")
    u_v = cv2.getTrackbarPos("UV", "HSV transmission")

    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("live transmission", frame)
    cv2.imshow("HSV transmission", hsv_frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
