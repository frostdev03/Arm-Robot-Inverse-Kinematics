import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy.optimize import minimize

hsv_colors = {
    'Blue': ([56, 40, 102], [118, 192, 255]),
    'Yellow': ([10, 20, 187], [255, 255, 255]),
    'Red': ([111, 37, 81], [255, 255, 255]),
    'Green': ([20, 41, 136], [255, 255, 255])
}

# Panjang segmen lengan (cm)
L1 = 7    # Jarak dari titik tengah ke tepi base
L2 = 26   # Lower arm
L3 = 17   # Center arm
L4 = 11   # Upper arm
L5 = 17   # neck Gripper
base_thickness = 13  # Ketebalan base (cm)

# Resolusi kamera
camera_resolution_x = 640
camera_resolution_y = 480

# Dimensi ruang kerja robot (cm)
physical_workspace_x = 100
physical_workspace_y = 100

# Hitung skala
scale_x = physical_workspace_x / camera_resolution_x
scale_y = physical_workspace_y / camera_resolution_y

# Fungsi untuk mengubah koordinat kamera menjadi koordinat fisik
def camera_to_physical(x_camera, y_camera):
    x_physical = (x_camera - (camera_resolution_x / 2)) * scale_x
    y_physical = (y_camera - (camera_resolution_y / 2)) * scale_y
    return x_physical, y_physical

# # Fungsi Forward Kinematics untuk 5-DOF
# def forward_kinematics(angles):
#     θ1, θ2, θ3, θ4, θ5 = angles
#     x, y, z = -50, 0, base_thickness
#     positions = [(x, y, z)]

#     # Base rotation (L1, hanya rotasi di bidang X-Y)
#     x += L1 * np.cos(θ1)
#     y += L1 * np.sin(θ1)
#     positions.append((x, y, z))

#     # Lower arm (L2)
#     z += L2 * np.sin(θ2)
#     x += L2 * np.cos(θ1) * np.cos(θ2)
#     y += L2 * np.sin(θ1) * np.cos(θ2)
#     positions.append((x, y, z))

#     # Center arm (L3)
#     z += L3 * np.sin(θ2 + θ3)
#     x += L3 * np.cos(θ1) * np.cos(θ2 + θ3)
#     y += L3 * np.sin(θ1) * np.cos(θ2 + θ3)
#     positions.append((x, y, z))

#     # Upper arm (L4)
#     z += L4 * np.sin(θ2 + θ3 + θ4)
#     x += L4 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
#     y += L4 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
#     positions.append((x, y, z))

#     # Gripper (L5)
#     z += L5
#     positions.append((x, y, z))

#     return positions

def forward_kinematics(angles):
    """
    Hitung posisi setiap joint berdasarkan sudut.
    """
    θ1, θ2, θ3, θ4, θ5 = angles
    x, y, z = -50, 0, base_thickness  # Base berada di z = base_thickness
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

    # Gripper (L5)
    z += L5
    positions.append((x, y, z))

    return positions


# def inverse_kinematics_optimized(x_target, y_target, z_target):
#     def objective(angles):
#         positions = forward_kinematics(angles)
#         end_effector = positions[-1]
#         error = np.sqrt((end_effector[0] - x_target)**2 +
#                         (end_effector[1] - y_target)**2 +
#                         (end_effector[2] - z_target)**2)
#         return error

#     initial_guess = [0, 0, 0, 0, 0]  # Starting angles
#     bounds = [(-np.pi, np.pi) for _ in range(5)]  # Angle limits

#     result = minimize(objective, initial_guess, bounds=bounds, method='SLSQP')
#     if not result.success:
#         raise ValueError("Optimization failed to find a valid solution.")
#     return result.x

def enforce_angle_limits(angles):
    limited_angles = [
        np.clip(angles[0], -2 * np.pi, 2 * np.pi),  # L1
        np.clip(angles[1], 0, np.pi),               # L2
        np.clip(angles[2], 0, np.pi),               # L3
        np.clip(angles[3], 0, np.pi),               # L4
        np.clip(angles[4], -2 * np.pi, 2 * np.pi)   # L5
    ]
    return limited_angles

# def inverse_kinematics_optimized_with_limits(x_target, y_target, z_target):
#     def objective(angles):
#         positions = forward_kinematics(angles)
#         end_effector = positions[-1]
#         error = np.sqrt((end_effector[0] - x_target)**2 +
#                         (end_effector[1] - y_target)**2 +
#                         (end_effector[2] - z_target)**2)
#         return error

#     # Inisialisasi sudut awal
#     initial_guess = [0, np.pi/4, np.pi/4, np.pi/4, 0]  # Sudut awal dalam radian

#     # Batasan sudut sesuai spesifikasi servo
#     bounds = [
#         (-2 * np.pi, 2 * np.pi),  # L1: bebas rotasi (-360 hingga 360 derajat)
#         (0, np.pi),               # L2: terbatas 0-180 derajat
#         (0, np.pi),               # L3: terbatas 0-180 derajat
#         (0, np.pi),               # L4: terbatas 0-180 derajat
#         (-2 * np.pi, 2 * np.pi)   # L5: bebas rotasi (-360 hingga 360 derajat)
#     ]

#     # Optimasi dengan batasan
#     result = minimize(objective, initial_guess, bounds=bounds, method='SLSQP')
#     if not result.success:
#         raise ValueError("Optimasi gagal menemukan solusi valid.")
    
#     # Enforce batas sudut setelah optimasi
#     angles = enforce_angle_limits(result.x)
#     return angles

def inverse_kinematics_optimized_with_limits(x_target, y_target, z_target):
    """
    Hitung sudut joint menggunakan optimasi dengan batasan sudut.
    """
    def objective(angles):
        positions = forward_kinematics(angles)
        end_effector = positions[-1]
        error = np.sqrt((end_effector[0] - x_target)**2 +
                        (end_effector[1] - y_target)**2 +
                        (end_effector[2] - z_target)**2)
        return error

    # Inisialisasi sudut awal
    initial_guess = [0, np.pi/4, np.pi/4, np.pi/4, 0]  # Sudut awal dalam radian

    # Batasan sudut sesuai spesifikasi servo
    bounds = [
        (-2 * np.pi, 2 * np.pi),  # L1: bebas rotasi (-360 hingga 360 derajat)
        (0, np.pi),               # L2: terbatas 0-180 derajat
        (0, np.pi),               # L3: terbatas 0-180 derajat
        (0, np.pi),               # L4: terbatas 0-180 derajat
        (-2 * np.pi, 2 * np.pi)   # L5: bebas rotasi (-360 hingga 360 derajat)
    ]

    # Optimasi dengan batasan
    result = minimize(objective, initial_guess, bounds=bounds, method='SLSQP')
    if not result.success:
        raise ValueError("Optimasi gagal menemukan solusi valid.")

    # Enforce batas sudut setelah optimasi
    angles = enforce_angle_limits(result.x)
    return angles


# Fungsi untuk menggambar posisi lengan robot
def plot_arm(angles, x_target, y_target, z_target):
    positions = forward_kinematics(angles)
    x_coords, y_coords, z_coords = zip(*positions)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x_coords, y_coords, z_coords, '-o', markersize=10, lw=3, label="Robot Arm")
    ax.scatter(x_target, y_target, z_target, color='red', s=100, label="Target Location")
    ax.set_xlim([-50, 50])
    ax.set_ylim([-50, 50])
    ax.set_zlim([0, 100])
    ax.set_xlabel("X Position (cm)")
    ax.set_ylabel("Y Position (cm)")
    ax.set_zlabel("Z Position (cm)")
    plt.legend()
    plt.title("5-DOF Robot Arm")
    plt.show()

# Input dari kamera
x_camera = 100
y_camera = 300

# # Konversi ke koordinat fisik
# x_target, y_target = camera_to_physical(x_camera, y_camera)
# z_target = 0  # Target ketinggian end-effector

x_target, y_target, z_target = 17, 0, 0  # Tepat di batas minimum horizontal dan vertikal



def validate_target(x_target, y_target, z_target):
    """
    Validasi apakah target berada dalam jangkauan robot.
    """
    r = np.sqrt(x_target**2 + y_target**2)  # Jarak horizontal dari base
    max_reach = L2 + L3 + L4 + L5          # Jangkauan maksimum horizontal
    min_reach = L5                         # Jangkauan minimum horizontal (sekitar 17 cm)

    # Validasi target
    if r > max_reach or r < min_reach:
        raise ValueError("Target berada di luar jangkauan horizontal robot.")
    if z_target < 0 or z_target > (base_thickness + L2 + L3 + L4 + L5):
        raise ValueError("Target berada di luar jangkauan vertikal robot.")


# Menyelesaikan inverse kinematics dan menggambar lengan
try:
    # Validasi target
    validate_target(x_target, y_target, z_target)

    # Hitung sudut dengan IK yang diperbaiki
    angles = inverse_kinematics_optimized_with_limits(x_target, y_target, z_target)
    print("Sudut yang dihitung (derajat):", [np.degrees(a) for a in angles])

    # Debug posisi end-effector
    positions = forward_kinematics(angles)
    end_effector = positions[-1]
    print("Posisi End-Effector:", end_effector)
    print("Posisi Target:", (x_target, y_target, z_target))

    # Plot lengan robot
    plot_arm(angles, x_target, y_target, z_target)
except ValueError as e:
    print("Error:", e)