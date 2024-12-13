import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.optimize import minimize

# Panjang segmen lengan (cm)
L1 = 7
L2 = 24
L3 = 17
L4 = 11
L5 = 17
base_thickness = 13

# Fungsi Forward Kinematics
def forward_kinematics(angles):
    θ1, θ2, θ3, θ4, θ5 = angles
    x, y, z = -40, 0, base_thickness
    positions = [(x, y, z)]

    x += L1 * np.cos(θ1)
    y += L1 * np.sin(θ1)
    positions.append((x, y, z))

    z += L2 * np.sin(θ2)
    x += L2 * np.cos(θ1) * np.cos(θ2)
    y += L2 * np.sin(θ1) * np.cos(θ2)
    positions.append((x, y, z))

    z += L3 * np.sin(θ2 + θ3)
    x += L3 * np.cos(θ1) * np.cos(θ2 + θ3)
    y += L3 * np.sin(θ1) * np.cos(θ2 + θ3)
    positions.append((x, y, z))

    z += L4 * np.sin(θ2 + θ3 + θ4)
    x += L4 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
    y += L4 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
    positions.append((x, y, z))

    x += L5 * np.cos(θ1) * np.cos(θ2 + θ3 + θ4)
    y += L5 * np.sin(θ1) * np.cos(θ2 + θ3 + θ4)
    z += L5 * np.sin(θ5)
    positions.append((x, y, z))

    return positions

# Fungsi Inverse Kinematics
# def inverse_kinematics_5dof(x_target, y_target, z_target):
#     def objective_function(angles):
#         end_effector_position = forward_kinematics(angles)[-1]
#         x, y, z = end_effector_position

#         # Penalti jarak ke target
#         distance_penalty = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)

#         # Penalti sudut yang mustahil
#         impossible_penalty = 0
#         θ1, θ2, θ3, θ4, θ5 = angles

#         # Contoh: Hindari sudut antara segmen terlalu tajam
#         if np.abs(θ3 - θ2) > np.radians(180):  # Sesuaikan batas sudut
#             impossible_penalty += 1000

#         # Hindari sudut total yang terlalu bengkok
#         if np.abs(θ3 + θ4) > np.radians(90):
#             impossible_penalty += 1000

#         return distance_penalty + impossible_penalty

#     def generate_initial_guess():
#         return [0, np.pi / 4, np.pi / 6, np.pi / 6, 0]

#     bounds = [
#         (-2 * np.pi, 2 * np.pi),  # Base rotation (-360° hingga 360°)
#         (0, np.pi),               # Lower arm (0° hingga 180°)
#         (0, np.pi),               # Center arm (0° hingga 180°)
#         (0, np.pi),               # Upper arm (0° hingga 180°)
#         (-2 * np.pi, 2 * np.pi)   # Neck/Gripper rotation (-360° hingga 360°)
#     ]

#     result = minimize(
#         objective_function,
#         generate_initial_guess(),
#         method='SLSQP',
#         bounds=bounds
#     )

#     if result.success:
#         return result.x
#     else:
#         raise ValueError("Tidak dapat menemukan solusi inverse kinematics")

def inverse_kinematics_5dof(    x_target, y_target, z_target):
    target =     x_target, y_target, z_target = target

    θ1 = np.arctan2(y_target, x_target)  # Rotasi basis
    r = np.sqrt(x_target**2 + y_target**2) - L1
    z = z_target - base_thickness
    d = np.sqrt(r**2 + z**2)

    θ2 = np.arctan2(z, r)  # Estimasi awal
    θ3 = 0  # Sesuaikan jika perlu
    θ4 = 0  # Sesuaikan jika perlu
    θ5 = 0  # Gripper default

    return [θ1, θ2, θ3, θ4, θ5]

# Fungsi untuk memvisualisasikan robot
def plot_robot(positions, target=None):
    """
    Visualisasi robot dalam ruang kerja 3D.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Extract positions
    x = [pos[0] for pos in positions]
    y = [pos[1] for pos in positions]
    z = [pos[2] for pos in positions]

    # Plot lengan robot
    ax.plot(x, y, z, '-o', label='Robot Arm')

    # Plot target jika tersedia
    if target:
        ax.scatter(target[0], target[1], target[2], c='r', marker='x', label='Target')

    # Set judul dan label
    ax.set_title('Simulasi Robot Arm 5 DOF')
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    
    ax.legend()
    plt.show()

# Contoh penggunaan
if __name__ == "__main__":
    # Koordinat target
    target = (-7.75, 9, 10.00)

    # Hitung sudut dengan inverse kinematics
    angles = inverse_kinematics_5dof(*target)

    # Konversi radian ke derajat dan tampilkan
    angles_degrees = np.degrees(angles)
    print(f"Sudut dalam derajat: {angles_degrees}")

    # Hitung posisi berdasarkan sudut
    positions = forward_kinematics(angles)

    # Plot robot
    plot_robot(positions, target)
