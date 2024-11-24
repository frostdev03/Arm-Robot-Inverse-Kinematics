import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Panjang tiap link
L1 = 7  # Base ke shoulder
L2 = 13  # Shoulder ke elbow
L3 = 12  # Elbow ke wrist
L4 = 10  # Wrist ke wrist pitch
L5 = 8   # Wrist pitch ke wrist roll
L6 = 6   # Wrist roll ke gripper

# Target posisi
x_target, y_target, z_target = 60, 20, 0  # Koordinat target

def forward_kinematics(angles):
    """
    Menghitung posisi setiap joint berdasarkan sudut
    """
    θ1, θ2, θ3, θ4, θ5, θ6 = angles
    x, y, z = 0, 0, 20  # Base dimulai dari z = 20
    positions = [(x, y, z)]

    # Joint 1 (Base - Tidak mengubah z)
    x += L1 * np.cos(θ1)
    y += L1 * np.sin(θ1)
    positions.append((x, y, z))  # z tetap 20

    # Joint 2 (Shoulder - Mulai memengaruhi z)
    z += L2 * np.sin(θ2)  # z dipengaruhi oleh sudut θ2
    x += L2 * np.cos(θ1) * np.cos(θ2)
    y += L2 * np.sin(θ1) * np.cos(θ2)
    positions.append((x, y, z))

    # Joint 3 (Elbow - Menambah kontribusi pada z)
    z += L3 * np.sin(θ2 + θ3)  # Akumulasi sudut θ2 dan θ3
    x += L3 * np.cos(θ1) * np.cos(θ2 + θ3)
    y += L3 * np.sin(θ1) * np.cos(θ2 + θ3)
    positions.append((x, y, z))

    # Joint 4 (Wrist Pitch - Menambah perubahan pada z)
    z += L4 * np.sin(θ2 + θ3 + θ4)
    x += L4 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
    y += L4 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
    positions.append((x, y, z))

    # Joint 5 (Wrist Roll - Menyesuaikan arah gripper)
    z += L5 * np.sin(θ2 + θ3 + θ4 + θ5)
    x += L5 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4 + θ5)
    y += L5 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4 + θ5)
    positions.append((x, y, z))

    # Joint 6 (Gripper/End-Effector - Akhir)
    z += L6 * np.sin(θ2 + θ3 + θ4 + θ5 + θ6)
    x += L6 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4 + θ5 + θ6)
    y += L6 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4 + θ5 + θ6)
    positions.append((x, y, z))

    return positions

def objective(angles):
    """
    Menghitung total error antara posisi end-effector dan target
    """
    positions = forward_kinematics(angles)
    x_end, y_end, z_end = positions[-1]

    # Error posisi
    error_x = abs(x_end - x_target)
    error_y = abs(y_end - y_target)
    error_z = abs(z_end - z_target)

    # Total error
    return error_x + error_y + error_z

# Batas sudut untuk semua joint
bounds = [
    (0, 2 * np.pi),  # Base
    (-np.pi, np.pi), # Shoulder
    (-np.pi, np.pi), # Elbow
    (-np.pi, np.pi), # Wrist Pitch
    (-np.pi, np.pi), # Wrist Roll
    (-np.pi, np.pi)  # Gripper
]

# Optimisasi
initial_angles = [0, 0, 0, 0, 0, 0]  # Sudut awal
result = minimize(objective, initial_angles, bounds=bounds)

# Hasil sudut optimal
optimal_angles = result.x
print(f"Optimal Angles: {optimal_angles}")

# Hitung posisi end-effector setelah optimisasi
positions = forward_kinematics(optimal_angles)
x_vals, y_vals, z_vals = zip(*positions)

# Error akhir
x_end, y_end, z_end = positions[-1]
error_x = abs(x_end - x_target)
error_y = abs(y_end - y_target)
error_z = abs(z_end - z_target)

print(f"End-effector Position: ({x_end:.2f}, {y_end:.2f}, {z_end:.2f})")
print(f"Error - X: {error_x:.2f}, Y: {error_y:.2f}, Z: {error_z:.2f}")

# Plot hasil akhir
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(x_vals, y_vals, z_vals, marker='o', label='Robot Arm')
ax.scatter(x_target, y_target, z_target, color='red', label='Target', s=50)
ax.set_title('Robot Arm - Optimized to Target')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.show()
