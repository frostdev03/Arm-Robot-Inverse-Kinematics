import numpy as np
from scipy.optimize import minimize
import websocket  # Pustaka websocket-client

# Panjang segmen lengan (cm), memperhatikan dimensi base
L1 = 7   # Jarak dari titik tengah ke tepi base
L2 = 24  # Lower arm
L3 = 17  # Center arm
L4 = 11  # Upper arm
L5 = 2   # Neck gripper
L6 = 5   # Gripper

base_thickness = 20  # Ketebalan base (cm)

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

# Fungsi Objective untuk meminimalkan jarak ke target
def objective_function(angles, x_target, y_target, z_target):
    end_effector_position = forward_kinematics(angles)[-1]
    x, y, z = end_effector_position
    distance = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)
    return distance

# Fungsi Inverse Kinematics menggunakan optimisasi
def inverse_kinematics_6dof(x_target, y_target, z_target):
    initial_guess = [0, 0, 0, 0, 0, 0]
    bounds = [
        (0, 2 * np.pi),  # Base
        (0, np.pi),      # Lower arm
        (0, np.pi),      # Center arm
        (0, np.pi),      # Upper arm
        (0, np.pi),      # Neck
        (0, np.pi)       # Gripper
    ]
    result = minimize(objective_function, initial_guess, args=(x_target, y_target, z_target), bounds=bounds)

    if result.success:
        return result.x
    else:
        raise ValueError("Tidak ditemukan solusi")

# Fungsi utama untuk komunikasi WebSocket
def main():
    # Alamat IP ESP32
    ESP32_IP = "192.168.137.131"  # Ganti dengan IP ESP32 Anda
    ESP32_PORT = 81

    # URL WebSocket ESP32
    ws_url = f"ws://{ESP32_IP}:{ESP32_PORT}/"

    try:
        print(f"Menghubungkan ke WebSocket {ws_url}...")
        ws = websocket.create_connection(ws_url)
        print("Terhubung ke WebSocket.")

        while True:
            try:
                # Meminta input posisi target dari pengguna
                x_target = float(input("Masukkan posisi target X (cm): "))
                y_target = float(input("Masukkan posisi target Y (cm): "))
                z_target = float(input("Masukkan posisi target Z (cm): "))

                # Menghitung sudut inverse kinematics
                angles = inverse_kinematics_6dof(x_target, y_target, z_target)
                angles_deg = [int(np.degrees(a) % 360) for a in angles]  # Konversi ke derajat bulat positif
                print(f"Sudut yang dihitung (derajat): {angles_deg}")

                # Mengirim data ke WebSocket
                message = "#" + "#".join([str(angle) for angle in angles_deg]) + "#"
                print(f"Mengirim data ke WebSocket: {message}")
                ws.send(message)

            except ValueError as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print("\nMenutup koneksi...")
                break

        ws.close()
        print("Koneksi WebSocket ditutup.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
