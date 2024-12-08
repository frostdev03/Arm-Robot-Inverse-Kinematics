import cv2
import numpy as np
import websocket
from scipy.optimize import minimize

url = 'http://192.168.152.201:81/stream'  # Pastikan Anda menggunakan URL streaming yang benar

# Nilai HSV untuk warna yang ingin dideteksi
hsv_colors = {
    'Blue': ([84, 60, 7], [118, 192, 255]),
    'Yellow': ([0, 51, 123], [51, 255, 255]),
    'Red': ([111, 37, 81], [255, 255, 255]),
    'Green': ([43, 75, 0], [104, 255, 255])
}

# Panjang segmen lengan (cm), memperhatikan dimensi base
L1 = 7   # Jarak dari titik tengah ke tepi base
L2 = 24  # Lower arm
L3 = 17  # Center arm
L4 = 11  # Upper arm
L5 = 17  # Gripper
base_thickness = 13  # Ketebalan base (cm)


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

    z += L5
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


def inverse_kinematics_5dof(x_target, y_target, z_target):
    def objective_function(angles):
        end_effector_position = forward_kinematics(angles)[-1]
        x, y, z = end_effector_position
        
        # Multi-component error metric
        distance_error = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)
        angle_smoothness = np.sum(np.abs(np.diff(angles))) * 0.05
        angle_range_penalty = np.sum(np.square(np.clip(angles, -np.pi, np.pi))) * 0.1
        
        return distance_error + angle_smoothness + angle_range_penalty

    def workspace_constraints(angles):
        positions = forward_kinematics(angles)
        z_values = [pos[2] for pos in positions]
        return np.min(z_values)  # Ensure all z coordinates are non-negative

    # Multiple initial guess strategies
    initial_guesses = [
        [np.pi/4, np.pi/4, np.pi/4, np.pi/4, np.pi/4, np.pi/4],
        [np.pi/2, np.pi/3, np.pi/3, np.pi/4, np.pi/4, np.pi/4],
        [0, np.pi/2, np.pi/2, 0, 0, 0],
        [np.pi, np.pi/4, np.pi/4, np.pi/2, np.pi/2, 0]
    ]

    bounds = [
        (0, 2 * np.pi),  # Base rotation
        (0, np.pi),      # Lower arm
        (0, np.pi),      # Center arm
        (0, np.pi),      # Upper arm
        (0, np.pi),      # Neck
        (0, np.pi)       # Gripper
    ]

    best_result = None
    best_distance = float('inf')

    # Try multiple optimization methods
    methods = ['trust-constr']

    for method in methods:
        for initial_guess in initial_guesses:
            try:
                result = minimize(
                    objective_function, 
                    initial_guess, 
                    method=method,
                    bounds=bounds,
                    constraints=[{'type': 'ineq', 'fun': workspace_constraints}],
                    options={
                        'maxiter': 300,
                        'ftol': 1e-7,
                        'xtol': 1e-7
                    }
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
                print(f"Optimization attempt failed: {e}")

    if best_result and best_result.success:
        print(f"Successful optimization. Distance to target: {best_distance}")
        return best_result.x
    else:
        raise ValueError("Unable to find inverse kinematics solution across multiple methods")

def main():
    
    ESP32_IP = "192.168.152.73"  # Ganti dengan IP ESP32 Anda
    ESP32_PORT = 81

    # URL WebSocket ESP32
    ws_url = f"ws://{ESP32_IP}:{ESP32_PORT}/"
    # Membuka kamera
    cap = cv2.VideoCapture(url)

    # Kernel untuk morfologi
    kernel = np.ones((5, 5), np.uint8)

    try:
        print(f"Menghubungkan ke WebSocket {ws_url}...")
        ws = websocket.create_connection(ws_url)
        print("Terhubung ke WebSocket.")
        
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
                            if cube_detected and cube_color:
                                label = f"{cube_color} Cube"
                                print(f"{cube_color} Cube Detected at X: {cube_center_x}, Y: {cube_center_y}")
                                
                                x_target = cube_center_x
                                y_target = cube_center_y
                                z_target = 0  # Z dapat ditentukan sesuai kebutuhan (misalnya, kedalaman kamera)
                                angles = inverse_kinematics_5dof(x_target, y_target, z_target)
                                angles_deg = [int(np.degrees(a) % 360) for a in angles]  # Konversi ke derajat bulat positif
                                print(f"Sudut yang dihitung (derajat): {angles_deg}")
                                
                                # Mengirim data ke WebSocket
                                message = "#" + "#".join([str(angle) for angle in angles_deg])
                                ws.send(message)
                                print(f"Data dikirim ke ESP32: {message}")
                                            
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
            
    except KeyboardInterrupt:
        print("Proses dihentikan oleh pengguna.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        # Pastikan semua sumber daya ditutup dengan benar
        cap.release()
        cv2.destroyAllWindows()
        ws.close()
        print("Kamera dan WebSocket telah ditutup.")

if __name__ == "__main__":
    main()