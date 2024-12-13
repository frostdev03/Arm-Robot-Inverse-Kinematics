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

# Fungsi Inverse Kinematics
def inverse_kinematics_5dof(x_target, y_target, z_target):
    def objective_function(angles):
        end_effector_position = forward_kinematics(angles)[-1]
        x, y, z = end_effector_position

        # Penalty jarak ke target
        distance_penalty = np.sqrt((x - x_target)**2 + (y - y_target)**2 + (z - z_target)**2)

        # Penalty untuk perubahan sudut yang terlalu besar
        angle_change_penalty = np.sum(np.abs(np.diff(angles))) * 0.05

        # Penalty untuk posisi sendi yang tidak natural
        joint_position_penalty = np.sum(np.abs(np.sin(angles))) * 0.1

        return distance_penalty + angle_change_penalty + joint_position_penalty

    def workspace_constraints(angles):
        # Pastikan semua z koordinat tidak negatif
        positions = forward_kinematics(angles)
        return min(pos[2] for pos in positions)

    def generate_initial_guess():
        return [np.pi / 6, np.pi / 4, np.pi / 6, np.pi / 6, L5 / 2]

    bounds = [
        (-np.pi, np.pi),  # Base
        (0, np.pi),       # Lower arm
        (0, np.pi),       # Center arm
        (0, np.pi),       # Upper arm
        (0, L5)           # Gripper
    ]

    # Optimasi untuk mendapatkan sudut terbaik
    best_result = None
    best_distance = float('inf')

    for _ in range(10):  # Coba 10 kali dengan initial guess berbeda
        initial_guess = generate_initial_guess()

        try:
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints={'type': 'ineq', 'fun': workspace_constraints}
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
            print(f"Optimasi gagal: {e}")

    if best_result and best_result.success:
        return best_result.x
    else:
        raise ValueError("Tidak dapat menemukan solusi inverse kinematics")

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
