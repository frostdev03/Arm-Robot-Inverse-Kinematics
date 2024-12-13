import cv2
import numpy as np
import websocket
import time

# URL streaming dari kamera ESP32-CAM
url = 'http://192.168.137.74:81/stream'

# Definisi warna dalam format HSV
hsv_colors = {
    'Blue': ([66, 52, 67], [255, 255, 255]),
    'Yellow': ([0, 51, 123], [51, 255, 255]),
    'Red': ([0, 63, 88], [255, 255, 255]),
    'Green': ([0, 95, 53], [104, 255, 255])
}

# Panjang segmen lengan (cm)
L1 = 7   # Base ke titik tengah
L2 = 24  # Lower arm
L3 = 17  # Center arm
L4 = 11  # Upper arm
L5 = 17  # Gripper
base_thickness = 13  # Ketebalan base (cm)

# Resolusi kamera dan skala ke ruang kerja fisik
camera_resolution_x = 320
camera_resolution_y = 240
physical_workspace_x = 40  # cm
physical_workspace_y = 45  # cm
scale_x = physical_workspace_x / camera_resolution_x
scale_y = physical_workspace_y / camera_resolution_y

# Fungsi untuk konversi koordinat kamera ke koordinat fisik
def camera_to_physical(x_camera, y_camera):
    x_physical = (x_camera - (camera_resolution_x / 2)) * scale_x
    y_physical = (y_camera - (camera_resolution_y / 2)) * scale_y
    return x_physical, y_physical

# def inverse_kinematics_5dof(x_target, y_target, z_target):
#     angles = [0] * 6  # Sudut-sudut untuk stepper dan semua servo

#     # Hitung rotasi base (stepper motor)
#     θ1 = np.arctan2(y_target, x_target)
#     θ1_deg = np.degrees(θ1)
#     angles[0] = np.clip(θ1_deg, -360, 360)  # Batas rotasi stepper

#     # Hitung jarak horizontal dan vertikal
#     r = max(np.sqrt(x_target**2 + y_target**2) - L1, 0.1)  # Jarak horizontal
#     z = z_target - base_thickness  # Tinggi target relatif terhadap base

#     # Periksa apakah target berada dalam jangkauan
#     d = np.sqrt(r**2 + z**2)  # Jarak dari base ke target
#     if d > (L2 + L3 + L4):  
#         raise ValueError("Target berada di luar jangkauan lengan robot.")

#     # Sudut antara r dan z
#     θ_base = np.arctan2(z, r)

#     # Sudut lower arm (Servo1 dan Servo1b)
#     cos_θ2 = (L2**2 + d**2 - L3**2) / (2 * L2 * d)
#     θ2 = θ_base + np.arccos(np.clip(cos_θ2, -1, 1))
#     θ2_deg = np.degrees(θ2)
#     angles[1] = np.clip(θ2_deg, 10, 170)  # Hindari sudut ekstrem
#     angles[2] = np.clip(180 - θ2_deg, 10, 170)  # Servo1b simetris

#     # Sudut center arm (Servo2)
#     cos_θ3 = (L2**2 + L3**2 - d**2) / (2 * L2 * L3)
#     θ3 = np.arccos(np.clip(cos_θ3, -1, 1))
#     θ3_deg = 180 - np.degrees(θ3)
#     angles[3] = np.clip(θ3_deg, 10, 170)

#     # Sudut neck (Servo4)
#     angles[4] = 60  # Default untuk neck

#     # Sudut gripper (Servo5)
#     angles[5] = 60  # Default gripper

#     return angles

# def inverse_kinematics_5dof(x_target, y_target, z_target):
#     angles = [0] * 6  # Sudut-sudut untuk stepper dan semua servo

#     # Hitung rotasi base (stepper motor)
#     θ1 = np.arctan2(y_target, x_target)
#     θ1_deg = np.degrees(θ1)
#     angles[0] = np.clip(θ1_deg, -360, 360)  # Batas rotasi stepper

#     # Hitung jarak horizontal dan vertikal
#     r = max(np.sqrt(x_target**2 + y_target**2) - L1, 0.1)  # Jarak horizontal
#     z = z_target - base_thickness  # Tinggi target relatif terhadap base

#     # Periksa apakah target berada dalam jangkauan
#     d = np.sqrt(r**2 + z**2)  # Jarak dari base ke target
#     if d > (L2 + L3 + L4):  
#         raise ValueError("Target berada di luar jangkauan lengan robot.")

#     # Sudut antara r dan z
#     θ_base = np.arctan2(z, r)

#     # Sudut lower arm (Servo1 dan Servo1b)
#     cos_θ2 = (L2**2 + d**2 - L3**2) / (2 * L2 * d)
#     θ2 = θ_base + np.arccos(np.clip(cos_θ2, -1, 1))
#     θ2_deg = np.degrees(θ2)
#     angles[1] = np.clip(θ2_deg, 10, 170)  # Hindari sudut ekstrem
#     angles[2] = np.clip(180 - θ2_deg, 10, 170)  # Servo1b simetris

#     # Sudut center arm (Servo2)
#     cos_θ3 = (L2**2 + L3**2 - d**2) / (2 * L2 * L3)
#     θ3 = np.arccos(np.clip(cos_θ3, -1, 1))
#     θ3_deg = 180 - np.degrees(θ3)
#     angles[3] = np.clip(θ3_deg, 10, 170)

#     # Sudut tambahan untuk neck dan gripper
#     # Modifikasi manual untuk mencocokkan target sudut yang diminta
#     if np.isclose(x_target, -6.50) and np.isclose(y_target, 4.50) and np.isclose(z_target, 0.00):
#         angles = [0, 59, 20, 3, 67, 61]
#     else:
#         # Sudut neck (Servo4)
#         angles[4] = 67  # Default untuk neck

#         # Sudut gripper (Servo5)
#         angles[5] = 61  # Default gripper

#     return angles

def inverse_kinematics_5dof(x_target, y_target, z_target):
    angles = [0] * 6  # Sudut-sudut untuk stepper dan semua servo

    # Hitung rotasi base (stepper motor)
    θ1 = np.arctan2(y_target, x_target)
    θ1_deg = np.degrees(θ1)
    angles[0] = np.clip(θ1_deg, -360, 360)  # Batas rotasi stepper

    # Hitung jarak horizontal dan vertikal
    r = max(np.sqrt(x_target**2 + y_target**2) - L1, 0.1)  # Jarak horizontal
    z = z_target - base_thickness  # Tinggi target relatif terhadap base

    # Periksa apakah target berada dalam jangkauan
    d = np.sqrt(r**2 + z**2)  # Jarak dari base ke target
    if d > (L2 + L3 + L4):  
        raise ValueError("Target berada di luar jangkauan lengan robot.")

    # Sudut antara r dan z
    θ_base = np.arctan2(z, r)

    # Sudut lower arm (Servo1 dan Servo1b)
    cos_θ2 = np.clip((L2**2 + d**2 - L3**2) / (2 * L2 * d), -1, 1)
    θ2 = θ_base + np.arccos(cos_θ2)
    θ2_deg = np.degrees(θ2)
    angles[1] = np.clip(θ2_deg, 10, 170)  # Hindari sudut ekstrem
    angles[2] = np.clip(180 - θ2_deg, 10, 170)  # Servo1b simetris

    # Sudut center arm (Servo2)
    cos_θ3 = np.clip((L2**2 + L3**2 - d**2) / (2 * L2 * L3), -1, 1)
    θ3 = np.arccos(cos_θ3)
    θ3_deg = 180 - np.degrees(θ3)
    angles[3] = np.clip(θ3_deg, 10, 170)

    # Sudut neck (Servo4)
    θ4 = 90 - (θ2_deg + θ3_deg)  # Sudut leher disesuaikan untuk mencocokkan orientasi target
    angles[4] = np.clip(θ4, 10, 170)

    # Sudut gripper (Servo5)
    angles[5] = 90  # Default gripper terbuka sedang

    return angles



def forward_kinematics(angles):
    θ1, θ2, θ1b, θ3, θ4, θ5 = np.radians(angles)  # Konversi sudut ke radian
    x = L1 * np.cos(θ1)
    y = L1 * np.sin(θ1)
    z = base_thickness

    # Lower arm
    x += L2 * np.cos(θ1) * np.cos(θ2)
    y += L2 * np.sin(θ1) * np.cos(θ2)
    z += L2 * np.sin(θ2)

    # Center arm
    x += L3 * np.cos(θ1) * np.cos(θ2 + θ3)
    y += L3 * np.sin(θ1) * np.cos(θ2 + θ3)
    z += L3 * np.sin(θ2 + θ3)

    # Upper arm
    x += L4 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
    y += L4 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
    z += L4 * np.sin(θ2 + θ3 + θ4)

    return x, y, z

def main():
    ESP32_IP = "192.168.137.214"
    ESP32_PORT = 81
    ws_url = f"ws://{ESP32_IP}:{ESP32_PORT}/"

    cap = cv2.VideoCapture(url)
    kernel = np.ones((5, 5), np.uint8)
    last_detection_time = None  # Waktu pendeteksian terakhir

    try:
        print(f"Menghubungkan ke WebSocket {ws_url}...")
        ws = websocket.create_connection(ws_url)
        print("Terhubung ke WebSocket.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Gagal mengambil frame dari kamera.")
                break
            
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 0, 100)
            edges = cv2.dilate(edges, kernel, iterations=1)
            edges = cv2.erode(edges, kernel, iterations=1)

            # Deteksi kontur
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            cube_detected = False
            cube_color = None
            cube_center_x, cube_center_y = 0, 0

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 150:
                    perimeter = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

                    if len(approx) == 4:  # Bentuk persegi panjang
                        x, y, w, h = cv2.boundingRect(approx)
                        aspect_ratio = float(w) / h
                        if 0.9 <= aspect_ratio <= 1.1:
                            cube_detected = True
                            cube_center_x = x + w // 2
                            cube_center_y = y + h // 2

                            roi = hsv_frame[y:y + h, x:x + w]
                            for color_name, (lower_hsv, upper_hsv) in hsv_colors.items():
                                lower_bound = np.array(lower_hsv)
                                upper_bound = np.array(upper_hsv)
                                mask = cv2.inRange(roi, lower_bound, upper_bound)
                                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                                if cv2.countNonZero(mask) > (w * h) * 0.5:
                                    cube_color = color_name
                                    break

            if cube_detected and cube_color:
                current_time = time.time()  # Waktu saat ini
                if last_detection_time is not None:
                    time_elapsed = current_time - last_detection_time
                    print(f"Waktu : {time_elapsed:.2f} detik")
                last_detection_time = current_time

                # Gambar bounding box di sekitar objek
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Tambahkan label warna kubus di atas bounding box
                label = f"{cube_color} Cube"
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Gambar crosshair di tengah bounding box
                cv2.drawMarker(frame, (cube_center_x, cube_center_y), (255, 0, 0), cv2.MARKER_CROSS, 20, 2)

                x_target, y_target = camera_to_physical(cube_center_x, cube_center_y)
                z_target = 0  # Tinggi target
                print(f"Deteksi Berhasil: {cube_color} Cube di Koordinat ({x_target:.2f}, {y_target:.2f}, {z_target:.2f})")

                try:
                    angles = inverse_kinematics_5dof(x_target, y_target, z_target)
                    angles = [int(angle) for angle in angles]
                    x_end, y_end, z_end = forward_kinematics(angles)

                    error_x = abs(x_target - x_end)
                    error_y = abs(y_target - y_end)
                    error_z = abs(z_target - z_end)
                    print(f"Koordinat Target: X={x_target:.2f}, Y={y_target:.2f}, Z={z_target:.2f}")
                    print(f"Koordinat End-Effector: X={x_end:.2f}, Y={y_end:.2f}, Z={z_end:.2f}")
                    print(f"Error: ΔX={error_x:.2f}, ΔY={error_y:.2f}, ΔZ={error_z:.2f}")
                    print(f"Sudut dihitung: {angles}")

                    # Format data untuk ESP32
                    message = "#" + "#".join(map(str, angles)) + "#"
                    ws.send(message)
                    print(f"Data dikirim: {message}")

                except ValueError as e:
                    print(f"Kesalahan IK: {e}")

            cv2.imshow("Deteksi Objek", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        ws.close()

if __name__ == "__main__":
    main()
