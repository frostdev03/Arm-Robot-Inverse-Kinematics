import cv2
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Nilai HSV
hsv_colors = {
    'Green': ([0, 36, 155], [78, 255, 255]),
    'Yellow': ([0, 27, 168], [72, 255, 255]),
    'Blue': ([37, 68, 49], [160, 255, 255]),
    'Cyan': ([0, 52, 140], [255, 255, 255]),
    'Red': ([0, 59, 101], [195, 255, 255]),
    'Red': ([0, 0, 180], [197, 255, 255])
}

# Inisialisasi kamera laptop
cap = cv2.VideoCapture(0)

# Kernel untuk morfologi
kernel = np.ones((5,5), np.uint8)

# Frame dimension
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2

# Fuzzy control system
error = ctrl.Antecedent(np.arange(-frame_width, frame_width + 1, 1), 'error')
velocity = ctrl.Consequent(np.arange(-1, 1.1, 0.1), 'velocity')

# Membership functions
error['left'] = fuzz.trimf(error.universe, [-frame_width, -frame_width, 0])
error['center'] = fuzz.trimf(error.universe, [-frame_width/2, 0, frame_width/2])
error['right'] = fuzz.trimf(error.universe, [0, frame_width, frame_width])

velocity['negative'] = fuzz.trimf(velocity.universe, [-1, -1, 0])
velocity['zero'] = fuzz.trimf(velocity.universe, [-0.5, 0, 0.5])
velocity['positive'] = fuzz.trimf(velocity.universe, [0, 1, 1])

# Fuzzy rules
rule1 = ctrl.Rule(error['left'], velocity['positive'])
rule2 = ctrl.Rule(error['center'], velocity['zero'])
rule3 = ctrl.Rule(error['right'], velocity['negative'])

velocity_control = ctrl.ControlSystem([rule1, rule2, rule3])
velocity_simulation = ctrl.ControlSystemSimulation(velocity_control)

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
    cube_position_x = None

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
                    cube_position_x = x + w / 2 - frame_width
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
        print(f"Detected {cube_color} Cube at position: {cube_position_x}")
        cv2.putText(frame, f"{cube_color} Cube Detected at position: {cube_position_x}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Fuzzy logic to determine the movement
        velocity_simulation.input['error'] = cube_position_x
        velocity_simulation.compute()
        movement_speed = velocity_simulation.output['velocity']
        print(f"Movement Speed: {movement_speed}")

    # Menampilkan frame dengan deteksi warna dan kubus
    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
