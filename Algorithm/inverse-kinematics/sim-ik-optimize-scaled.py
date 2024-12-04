import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Panjang segmen lengan (cm), memperhatikan dimensi base
L1 = 7   # Jarak dari titik tengah ke tepi base
L2 = 24  # Lower arm
L3 = 17  # Center arm
L4 = 11  # Upper arm
L5 = 2   # Neck gripper
L6 = 15   # Gripper
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

    # # Validasi agar tetap dalam rentang ruang kerja (0 - 80 cm)
    # x_physical = max(0, min(x_physical, physical_workspace_x))
    # y_physical = max(0, min(y_physical, physical_workspace_y))

    return x_physical, y_physical


# Fungsi Forward Kinematics
def forward_kinematics(angles):
    θ1, θ2, θ3, θ4, θ5, θ6 = angles
    x, y, z = -40, 0, base_thickness
    positions = [(x, y, z)]

    # Base rotation (L1, hanya rotasi di bidang X-Y)
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

    # Neck gripper (L5, hanya linear di z, tanpa perubahan sudut)
    z += L5
    positions.append((x, y, z))

    # Gripper (L6)
    z += L6 * np.sin(θ2 + θ3 + θ4 + θ6)  # Sudut gripper mengikuti keseluruhan rantai
    x += L6 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4 + θ6)
    y += L6 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4 + θ6)
    positions.append((x, y, z))

    return positions

# # Fungsi Inverse Kinematics
# def inverse_kinematics_6dof(x_target, y_target, z_target):
#     def objective_function(angles):
#         end_effector_position = forward_kinematics(angles)[-1]
#         print(f"Testing angles: {angles}, position: {end_effector_position}")
#         x, y, z = end_effector_position
#         distance_penalty = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)
        
#         if z < 0:
#             z_penalty = np.abs(z)  # Penalti proporsional dengan nilai negatif z
#         else:
#             z_penalty = 0
        
#         return distance_penalty + z_penalty * 10  # Penalti lebih besar jika z < 0
#         # return distance_penalty

#     # Batasan sudut untuk masing-masing motor
#     bounds = [
#         (0, 2 * np.pi),         # θ1 (base rotation)
#         (-np.pi / 2, np.pi / 2),# θ2 (lower arm)
#         (-np.pi / 2, np.pi / 2),# θ3 (center arm)
#         (-np.pi / 2, np.pi / 2),# θ4 (upper arm)
#         (0, L5),                # L5
#         (-np.pi / 6, np.pi / 6) # θ6
#     ]

#     initial_guess = [np.pi / 4] * 5 + [L5 / 2]  # Tambahkan L5 sebagai tebakan awal
#     # initial_guess = [np.pi / 4, np.pi / 4, np.pi / 4, np.pi / 4, L5 / 2, 0]  # Anggap semua sudut 45 derajat, L5 di tengah
#     result = minimize(objective_function, initial_guess, bounds=bounds, method='Powell')

#     if result.success:
#         return result.x
#     else:
#         raise ValueError("Tidak dapat menemukan solusi inverse kinematics")

def inverse_kinematics_6dof(x_target, y_target, z_target):
    def objective_function(angles):
        end_effector_position = forward_kinematics(angles)[-1]
        x, y, z = end_effector_position
        
        # Tambahkan penalty yang kompleks
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

    def workspace_constraints(angles):
        # Pastikan semua z koordinat tidak negatif
        positions = forward_kinematics(angles)
        return min(pos[2] for pos in positions)

    # Metode inisialisasi awal yang lebih baik
    def generate_initial_guess():
        return [
            np.random.uniform(0, 2 * np.pi),   # Base
            np.random.uniform(0, np.pi),       # Lower arm
            np.random.uniform(0, np.pi),       # Center arm
            np.random.uniform(0, np.pi),       # Upper arm
            np.random.uniform(0, np.pi),       # Neck
            np.random.uniform(0, np.pi)        # Gripper
        ]

    bounds = [
        (0, 2 * np.pi),  # Base
        (0, np.pi),      # Lower arm
        (0, np.pi),      # Center arm
        (0, np.pi),      # Upper arm
        (0, L5),      # Neck
        (0, np.pi)       # Gripper
    ]

    # Coba beberapa kali dengan initial guess berbeda
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

                # Pilih solusi dengan jarak paling dekat
                if distance < best_distance:
                    best_result = result
                    best_distance = distance

        except Exception as e:
            print(f"Optimasi gagal: {e}")

    if best_result and best_result.success:
        return best_result.x
    else:
        raise ValueError("Tidak dapat menemukan solusi inverse kinematics")

# Fungsi untuk menggambar posisi lengan robot
def plot_arm(angles, x_target, y_target, z_target):
    positions = forward_kinematics(angles)
    x_coords, y_coords, z_coords = zip(*positions)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x_coords, y_coords, z_coords, '-o', markersize=10, lw=3, label="Robot Arm")
    ax.scatter(x_target, y_target, z_target, color='red', s=100, label="Target Location")
    ax.set_xlim([-40, 40])
    ax.set_ylim([-40, 40])
    ax.set_zlim([0, 80])
    ax.set_xlabel("X Position (cm)")
    ax.set_ylabel("Y Position (cm)")
    ax.set_zlabel("Z Position (cm)")
    plt.legend()
    plt.title("6-DOF Robot Arm")
    plt.show()

# Input dari kamera
x_camera = 210
y_camera = 65

# Konversi ke koordinat fisik
x_target, y_target = camera_to_physical(x_camera, y_camera)
z_target = 0  # Target ketinggian end-effector

# Menyelesaikan inverse kinematics dan menggambar lengan
# Tambahkan setelah perhitungan inverse kinematics
try:
    angles = inverse_kinematics_6dof(x_target, y_target, z_target)
    print("Sudut yang dihitung (derajat):", [np.degrees(a) for a in angles])

    # Dapatkan posisi end-effector dari hasil forward kinematics
    end_effector_position = forward_kinematics(angles)[-1]
    x_end_effector, y_end_effector, z_end_effector = end_effector_position

    # Cetak koordinat target dan end-effector
    print("Koordinat Target:")
    print(f"x_target: {x_target:.2f}, y_target: {y_target:.2f}, z_target: {z_target:.2f}")
    print("Koordinat End-Effector:")
    print(f"x_end_effector: {x_end_effector:.2f}, y_end_effector: {y_end_effector:.2f}, z_end_effector: {z_end_effector:.2f}")

    # Hitung error
    error_x = x_target - x_end_effector
    error_y = y_target - y_end_effector
    error_z = z_target - z_end_effector
    print("Error Koordinat:")
    print(f"Error x: {error_x:.2f}, Error y: {error_y:.2f}, Error z: {error_z:.2f}")

    # Plot lengan robot
    plot_arm(angles, x_target, y_target, z_target)
except ValueError as e:
    print(e)

