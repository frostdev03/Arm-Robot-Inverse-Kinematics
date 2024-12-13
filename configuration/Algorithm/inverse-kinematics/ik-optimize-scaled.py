import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Panjang segmen lengan (cm)
L1 = 7    # Jarak dari titik tengah ke tepi base
L2 = 24   # Lower arm
L3 = 17   # Center arm
L4 = 11   # Upper arm
L5 = 17   # Neck/Gripper
base_thickness = 13  # Ketebalan base (cm)

# Resolusi kamera
camera_resolution_x = 320
camera_resolution_y = 240

# Titik tengah kamera (pusat)
camera_center_x = camera_resolution_x / 2
camera_center_y = camera_resolution_y / 2

# Dimensi ruang kerja robot (cm)
physical_workspace_x = 45
physical_workspace_y = 40

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

# Fungsi Inverse Kinematics untuk 5 DOF
def inverse_kinematics_5dof(x_target, y_target, z_target):
    def objective_function(angles):
        end_effector_position = forward_kinematics(angles)[-1]
        x, y, z = end_effector_position
        distance_penalty = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)
        return distance_penalty

    bounds = [
        (0, 2 * np.pi),         # θ1 (base rotation)
        (-np.pi / 2, np.pi / 2),# θ2 (lower arm)
        (-np.pi / 2, np.pi / 2),# θ3 (center arm)
        (-np.pi / 2, np.pi / 2),# θ4 (upper arm)
        (0, L5)                 # L5 (neck/gripper)
    ]

    initial_guess = [np.pi / 4] * 4 + [L5 / 2]
    result = minimize(objective_function, initial_guess, bounds=bounds, method='Powell')

    if result.success:
        return result.x
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
    plt.title("5-DOF Robot Arm")
    plt.show()

# Input dari kamera
x_camera = 210
y_camera = 65

# Konversi ke koordinat fisik
x_target, y_target = camera_to_physical(x_camera, y_camera)
z_target = 0  # Target ketinggian end-effector

# Menyelesaikan inverse kinematics dan menggambar lengan
try:
    angles = inverse_kinematics_5dof(x_target, y_target, z_target)
    print("Sudut yang dihitung (derajat):", [np.degrees(a) for a in angles])
    plot_arm(angles, x_target, y_target, z_target)
except ValueError as e:
    print(e)
