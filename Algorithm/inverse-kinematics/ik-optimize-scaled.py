import cv2
import numpy as np
import websocket
from scipy.optimize import minimize
# URL streaming dari kamera ESP32-CAM
url = 'http://192.168.61.201:81/stream'  # Ganti dengan URL streaming yang benar

# Nilai HSV untuk warna yang ingin dideteksi
hsv_colors = {
    'Blue': ([56, 40, 102], [118, 192, 255]),
    'Yellow': ([10, 20, 187], [255, 255, 255]),
    'Red': ([111, 37, 81], [255, 255, 255]),
    'Green': ([20, 41, 136], [255, 255, 255])
}

# Panjang segmen lengan (cm), memperhatikan dimensi base
L1 = 7   # Jarak dari titik tengah ke tepi base
L2 = 24  # Lower arm
L3 = 17  # Center arm
L4 = 11  # Upper arm
L5 = 2   # Neck gripper
L6 = 15  # Gripper
base_thickness = 20  # Ketebalan base (cm)

# Resolusi kamera
camera_resolution_x = 640
camera_resolution_y = 480

# Titik tengah kamera (pusat)
camera_center_x = camera_resolution_x / 2
camera_center_y = camera_resolution_y / 2

# Dimensi ruang kerja robot (cm)
physical_workspace_x = 80
physical_workspace_y = 80

# Hitung skala
scale_x = physical_workspace_x / camera_resolution_x
scale_y = physical_workspace_y / camera_resolution_y

# Fungsi untuk mengubah koordinat kamera menjadi koordinat fisik
def camera_to_physical(x_camera, y_camera):
    x_physical = (x_camera - camera_center_x) * scale_x
    y_physical = (y_camera - camera_center_y) * scale_y
    return x_physical, y_physical

# Fungsi Forward Kinematics
def forward_kinematics(angles):
    θ1, θ2, θ3, θ4, θ5, θ6 = angles
    x, y, z = 0, 0, base_thickness  # Awalnya berada pada base
    positions = [(x, y, z)]
    
    # Joint 1 (Base)
    x += L1 * np.cos(θ1)
    y += L1 * np.sin(θ1)
    positions.append((x, y, z))  # Z tidak berubah pada base

    # Joint 2 (Lower arm)
    z += L2 * np.sin(θ2)
    x += L2 * np.cos(θ1) * np.cos(θ2)
    y += L2 * np.sin(θ1) * np.cos(θ2)
    positions.append((x, y, z))

    # Joint 3 (Center arm)
    z += L3 * np.sin(θ2 + θ3)
    x += L3 * np.cos(θ1) * np.cos(θ2 + θ3)
    y += L3 * np.sin(θ1) * np.cos(θ2 + θ3)
    positions.append((x, y, z))

    # Joint 4 (Upper arm)
    z += L4 * np.sin(θ2 + θ3 + θ4)
    x += L4 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
    y += L4 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
    positions.append((x, y, z))

    # Joint 5 (Neck gripper)
    z += L5 * np.sin(θ2 + θ3 + θ4 + θ5)
    x += L5 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4 + θ5)
    y += L5 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4 + θ5)
    positions.append((x, y, z))

    # Joint 6 (Gripper/End-effector)
    z += L6 * np.sin(θ2 + θ3 + θ4 + θ5 + θ6)
    x += L6 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4 + θ5 + θ6)
    y += L6 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4 + θ5 + θ6)
    positions.append((x, y, z))

    return positions

def objective_function(angles, x_target, y_target, z_target):
    end_effector_position = forward_kinematics(angles)[-1]
    x, y, z = end_effector_position
    
    # Tambahkan penalty yang lebih kompleks
    distance_penalty = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)
    
    # Penalty untuk perubahan sudut yang terlalu besar
    angle_change_penalty = np.sum(np.abs(np.diff(angles))) * 0.05
    
    # Penalty untuk posisi sendi yang tidak natural
    joint_position_penalty = np.sum(np.abs(np.sin(angles))) * 0.1
    
    # Bobot untuk setiap jenis penalty
    return (
        distance_penalty + 
        angle_change_penalty + 
        joint_position_penalty
    )

# Fungsi Inverse Kinematics menggunakan optimisasi
def inverse_kinematics_6dof(x_target, y_target, z_target):
    def objective_function(angles):
        end_effector_position = forward_kinematics(angles)[-1]
        x, y, z = end_effector_position
        distance = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)
        
        # Tambahkan penalty untuk sudut yang terlalu ekstrem
        angle_penalty = np.sum(np.abs(angles)) * 0.1
        return distance + angle_penalty

    def workspace_constraints(angles):
        # Pastikan semua z koordinat tidak negatif
        positions = forward_kinematics(angles)
        return min(pos[2] for pos in positions)

    # Metode inisialisasi awal yang lebih baik
    def generate_initial_guess():
        return [
            np.random.uniform(0, 2 * np.pi),   # Base
            np.random.uniform(0, np.pi/2),     # Lower arm
            np.random.uniform(0, np.pi/2),     # Center arm
            np.random.uniform(0, np.pi/2),     # Upper arm
            np.random.uniform(0, np.pi/2),     # Neck
            np.random.uniform(0, np.pi/2)      # Gripper
        ]

    bounds = [
        (0, 2 * np.pi),  # Base
        (0, np.pi),      # Lower arm
        (0, np.pi),      # Center arm
        (0, np.pi),      # Upper arm
        (0, np.pi),      # Neck
        (0, np.pi)       # Gripper
    ]

    best_result = None
    best_distance = float('inf')

    for _ in range(10):  # Coba 10 kali dengan initial guess berbeda
        initial_guess = generate_initial_guess()
        
        try:
            result = minimize(
                objective_function, 
                initial_guess, 
                method='SLSQP',  # Metode optimasi yang lebih baik
                bounds=bounds,
                constraints={'type': 'ineq', 'fun': workspace_constraints}
            )

            if result.success:
                # Hitung jarak ke target
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

# Fungsi utama untuk komunikasi WebSocket dan deteksi warna
def main():
    # Alamat IP ESP32
    ESP32_IP = "192.168.61.73"  # Ganti dengan IP ESP32 Anda
    ESP32_PORT = 81

    # URL WebSocket ESP32
    ws_url = f"ws://{ESP32_IP}:{ESP32_PORT}/"

    # Membuka kamera
    cap = cv2.VideoCapture(url)
    kernel = np.ones((5, 5), np.uint8)  # Kernel untuk operasi morfologi

    try:
        print(f"Menghubungkan ke WebSocket {ws_url}...")
        ws = websocket.create_connection(ws_url)
        print("Terhubung ke WebSocket.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Ubah ke HSV untuk deteksi warna
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Deteksi tepi dengan Canny
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            edges = cv2.dilate(edges, kernel, iterations=1)
            edges = cv2.erode(edges, kernel, iterations=1)

            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            cube_detected = False
            cube_color = None
            cube_center_x, cube_center_y = 0, 0

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:
                    perimeter = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

                    if len(approx) == 4:  # Bentuk persegi panjang
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
                                if mask_area > (w * h) * 0.5:
                                    cube_color = color_name
                                    break

            # Jika kubus dan warnanya terdeteksi, kirim posisi target ke robot arm
            if cube_detected and cube_color:
                print(f"{cube_color} Cube Detected at X: {cube_center_x}, Y: {cube_center_y}")
                # Tentukan posisi target (X, Y, Z)
                x_target = cube_center_x
                y_target = cube_center_y
                z_target = 10  # Z dapat ditentukan sesuai kebutuhan (misalnya, kedalaman kamera)

                # Hitung sudut inverse kinematics
                angles = inverse_kinematics_6dof(x_target, y_target, z_target)
                angles_deg = [int(np.degrees(a) % 360) for a in angles]  # Konversi ke derajat bulat positif
                print(f"Sudut yang dihitung (derajat): {angles_deg}")

                # Mengirim data ke WebSocket
                message = "#" + "#".join([str(angle) for angle in angles_deg])
                ws.send(message)
                print(f"Data dikirim ke ESP32: {message}")

            # Menampilkan hasil video deteksi warna dan kontur
            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Kesalahan: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
