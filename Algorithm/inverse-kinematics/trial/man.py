import cv2
import numpy as np
import websocket

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
L5 = 17  # Gripper = neck
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

# Fungsi sederhana untuk menghitung sudut berdasarkan posisi x dan y
def calculate_angles(x_target, y_target):
    # Anggap x_target dan y_target sudah dalam koordinat fisik
    # Menghitung sudut berdasarkan posisi objek relatif terhadap lengan robot
    # Ini menggunakan pendekatan percabangan if-else, berdasarkan posisi target

    # Perkiraan sudut untuk base (θ1)
    if x_target < 0:
        θ1 = np.pi / 2  # Angka perkiraan, sesuaikan dengan tuning Anda
    elif x_target > 0:
        θ1 = -np.pi / 2  # Angka perkiraan, sesuaikan dengan tuning Anda
    else:
        θ1 = 0

    # Perkiraan sudut untuk lower arm (θ2)
    if y_target < 10:
        θ2 = np.pi / 4  # Angka perkiraan, sesuaikan dengan tuning Anda
    elif y_target > 30:
        θ2 = np.pi / 3  # Angka perkiraan, sesuaikan dengan tuning Anda
    else:
        θ2 = np.pi / 6

    # Perkiraan sudut untuk center arm (θ3)
    if x_target > 50:
        θ3 = np.pi / 2  # Angka perkiraan, sesuaikan dengan tuning Anda
    else:
        θ3 = np.pi / 3  # Angka perkiraan, sesuaikan dengan tuning Anda

    # Perkiraan sudut untuk upper arm (θ4)
    if y_target > 20:
        θ4 = np.pi / 4  # Angka perkiraan, sesuaikan dengan tuning Anda
    else:
        θ4 = np.pi / 6  # Angka perkiraan, sesuaikan dengan tuning Anda

    # Perkiraan sudut untuk neck (θ5)
    θ5 = 0  # Menganggap gripper tetap stabil

    # Perkiraan sudut untuk gripper (θ6)
    θ6 = 0  # Menganggap gripper tetap stabil

    return [θ1, θ2, θ3, θ4, θ5, θ6]

def main():
    ESP32_IP = "192.168.152.37"  # Ganti dengan IP ESP32 Anda
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
                                angles = calculate_angles(x_target, y_target)
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
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            # Tampilkan frame hasil deteksi
            cv2.imshow('Detected Cube', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        ws.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
