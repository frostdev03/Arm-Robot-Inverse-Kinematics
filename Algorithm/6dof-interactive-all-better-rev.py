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
L6 = 5   # Gripper

base_thickness = 20  # Ketebalan base (cm)

# Fungsi Forward Kinematics dengan kontribusi z dari setiap joint
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
        (-np.pi/2, np.pi/2),  # Lower arm
        (-np.pi/2, np.pi/2),  # Center arm
        (-np.pi/2, np.pi/2),  # Upper arm
        (-np.pi/2, np.pi/2),  # Neck
        (-np.pi/2, np.pi/2)   # Gripper
    ]
    result = minimize(objective_function, initial_guess, args=(x_target, y_target, z_target), bounds=bounds)

    if result.success:
        return result.x
    else:
        raise ValueError("Tidak ditemukan solusi")

# Fungsi untuk menggambar posisi lengan robot
def plot_arm(angles, x_target, y_target, z_target):
    positions = forward_kinematics(angles)
    x_coords, y_coords, z_coords = zip(*positions)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x_coords, y_coords, z_coords, '-o', markersize=10, lw=3, label="Robot Arm")
    ax.scatter(x_target, y_target, z_target, color='red', s=100, label="Target Location")
    ax.set_xlim([0, 80])
    ax.set_ylim([-80, 80])
    ax.set_zlim([0, 80])
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_zlabel("Z Position")
    plt.title("6-DOF Robot Arm")
    plt.legend()
    plt.show()

# Target posisi dalam 3D
x_target, y_target, z_target = 50, 30, 0  # Misalnya target dengan z = 0

# Menyelesaikan inverse kinematics dan menampilkan hasil
try:
    theta1, theta2, theta3, theta4, theta5, theta6 = inverse_kinematics_6dof(x_target, y_target, z_target)
    print(f"Calculated Angles: Theta1 = {np.degrees(theta1):.2f}°, Theta2 = {np.degrees(theta2):.2f}°, Theta3 = {np.degrees(theta3):.2f}°, Theta4 = {np.degrees(theta4):.2f}°, Theta5 = {np.degrees(theta5):.2f}°, Theta6 = {np.degrees(theta6):.2f}°")

    # Menampilkan posisi end-effector dan menghitung error pada X, Y, Z
    end_effector_position = forward_kinematics([theta1, theta2, theta3, theta4, theta5, theta6])[-1]
    x_end, y_end, z_end = end_effector_position

    # Menghitung error pada setiap sumbu
    error_x = abs(x_end - x_target)
    error_y = abs(y_end - y_target)
    error_z = abs(z_end - z_target)

    print(f"End-effector position: ({x_end:.2f}, {y_end:.2f}, {z_end:.2f})")
    print(f"Error in X: {error_x:.2f} cm")
    print(f"Error in Y: {error_y:.2f} cm")
    print(f"Error in Z: {error_z:.2f} cm")

    # Validasi apakah error cukup kecil untuk pick (Z error < 2 cm)
    if error_z < 3:  # Toleransi error Z lebih kecil dari 2 cm
        print("End-effector mencapai target!")
    else:
        print("End-effector gagal mencapai target.")

    plot_arm([theta1, theta2, theta3, theta4, theta5, theta6], x_target, y_target, z_target)
except ValueError as e:
    print(e)
