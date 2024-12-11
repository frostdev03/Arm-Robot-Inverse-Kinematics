import cv2
import numpy as np
from scipy.optimize import minimize
import websocket
import time

# URL streaming dari kamera ESP32-CAM
url = 'http://192.168.129.201:81/stream'

# Definisi warna dalam format HSV
hsv_colors = {
    'Green': ([40, 50, 50], [80, 255, 255]),
    'Blue': ([0, 102, 97], [255, 255, 255]),
    # 'Yellow': ([0, 51, 123], [51, 255, 255]),
    'Red': ([0, 34, 114], [255, 97, 197])
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

# Fungsi Inverse Kinematics untuk 5 DOF
def inverse_kinematics_5dof(x_target, y_target, z_target):
    def objective_function(angles):
        end_effector_position = forward_kinematics(angles)[-1]
        x, y, z = end_effector_position

        # Penalty jarak ke target
        distance_penalty = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)

        # Penalty untuk perubahan sudut yang terlalu besar
        angle_change_penalty = np.sum(np.abs(np.diff(angles))) * 0.05

        # Penalty untuk posisi sendi yang tidak natural
        joint_position_penalty = np.sum(np.abs(np.sin(angles))) * 0.1

        return distance_penalty + angle_change_penalty + joint_position_penalty

    def workspace_constraints(angles):
        # Pastikan semua z koordinat tidak negatif
        positions = forward_kinematics(angles)
        return min(pos[2] for pos in positions)

    # Inisialisasi awal untuk sudut
    # def generate_initial_guess():
    #     return [
    #         np.random.uniform(0, 2 * np.pi),   # Base
    #         np.random.uniform(0, np.pi),       # Lower arm
    #         np.random.uniform(0, np.pi),       # Center arm
    #         np.random.uniform(0, np.pi),       # Upper arm
    #         np.random.uniform(0, L5)           # Gripper (linear)
    #     ]
    
    # def generate_initial_guess():
    #     return [np.pi / 2, np.pi / 4, np.pi / 4, np.pi / 4, L5 / 2]  # Contoh nilai tetap
    
    # def generate_initial_guess():
    #     return [0, np.pi/4, np.pi/4, np.pi/4, 0]  # Sudut awal dalam radian

    # def generate_initial_guess():
    #     return [np.pi / 4] * 4 + [L5 / 2]
    
    def generate_initial_guess():
        θ1 = np.pi / 6 + np.random.uniform(-np.pi/12, np.pi/12)
        θ2 = np.pi / 6 + np.random.uniform(-np.pi/12, np.pi/12)
        θ3 = np.pi / 8 + np.random.uniform(-np.pi/16, np.pi/16)
        θ4 = np.pi / 8 + np.random.uniform(-np.pi/16, np.pi/16)
        θ5 = L5 / 2 + np.random.uniform(-1, 1)
        return [θ1, θ2, θ3, θ4, θ5]



    # bounds = [
    #     (0, 2 * np.pi),  # Base
    #     (0, np.pi),      # Lower arm
    #     (0, np.pi),      # Center arm
    #     (0, np.pi),      # Upper arm
    #     (0, L5)          # Gripper
    # ]
    
    bounds = [
        (-np.pi, np.pi),  # Base
        (0, np.pi),       # Lower arm
        (0, np.pi),       # Center arm
        (0, np.pi),       # Upper arm
        (0, L5)           # Gripper
    ]


    # Optimasi untuk mendapatkan sudut terbaik
    best_result = None
    best_distance = float('inf')

    for _ in range(10):  # Coba 10 kali dengan initial guess berbeda
        initial_guess = generate_initial_guess()

        try:
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints={'type': 'ineq', 'fun': workspace_constraints}
            )

            if result.success:
                end_pos = forward_kinematics(result.x)[-1]
                distance = np.sqrt(
                    (end_pos[0] - x_target)**2 +
                    (end_pos[1] - y_target)**2 +
                    (end_pos[2] - z_target)**2
                )

                if distance < best_distance:
                    best_result = result
                    best_distance = distance

        except Exception as e:
            print(f"Optimasi gagal: {e}")

    if best_result and best_result.success:
        return best_result.x
    else:
        raise ValueError("Tidak dapat menemukan solusi inverse kinematics")

# Fungsi Forward Kinematics
def forward_kinematics(angles):
    θ1, θ2, θ3, θ4, θ5 = angles
    x, y, z = -40, 0, base_thickness
    positions = [(x, y, z)]

    # Base rotation (L1)
    x += L1 * np.cos(θ1)
    y += L1 * np.sin(θ1)
    positions.append((x, y, z))

    # Lower arm (L2)
    z += L2 * np.sin(θ2)
    x += L2 * np.cos(θ1) * np.cos(θ2)
    y += L2 * np.sin(θ1) * np.cos(θ2)
    positions.append((x, y, z))

    # Center arm (L3)
    z += L3 * np.sin(θ2 + θ3)
    x += L3 * np.cos(θ1) * np.cos(θ2 + θ3)
    y += L3 * np.sin(θ1) * np.cos(θ2 + θ3)
    positions.append((x, y, z))

    # Upper arm (L4)
    z += L4 * np.sin(θ2 + θ3 + θ4)
    x += L4 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
    y += L4 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
    positions.append((x, y, z))

    # Neck/Gripper (L5)
    z += L5
    positions.append((x, y, z))

    return positions

def main():
    ESP32_IP = "192.168.129.37"
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
                    # angles = [int(angle) for angle in angles]
                    x_end, y_end, z_end = forward_kinematics(angles)[-1]

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
