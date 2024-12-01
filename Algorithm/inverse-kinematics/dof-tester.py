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

# Fungsi untuk menggambar posisi lengan robot
def plot_arm(angles):
    positions = forward_kinematics(angles)
    x_coords, y_coords, z_coords = zip(*positions)

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x_coords, y_coords, z_coords, '-o', markersize=10, lw=3, label="Robot Arm")
    ax.set_xlim([0, 80])
    ax.set_ylim([-80, 80])
    ax.set_zlim([0, 80])
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_zlabel("Z Position")
    plt.title("6-DOF Robot Arm Position")
    plt.legend()
    plt.show()

def manual_angle_control():
    # Default angles (semua diset ke 0)
    angles = [0, 0, 0, 0, 0, 0]
    
    while True:
        # Tampilkan sudut saat ini
        print("\nSudut saat ini (dalam derajat):")
        for i, angle in enumerate(angles, 1):
            print(f"Joint {i}: {np.degrees(angle):.2f}°")
        
        # Pilihan menu
        print("\nPilih opsi:")
        print("1. Ubah sudut joint")
        print("2. Tampilkan posisi lengan")
        print("3. Keluar")
        
        choice = input("Masukkan pilihan (1/2/3): ")
        
        if choice == '1':
            # Memilih joint untuk diubah
            try:
                joint = int(input("Masukkan nomor joint (1-6): ")) - 1
                if 0 <= joint < 6:
                    # Sudut dalam derajat
                    new_angle = float(input("Masukkan sudut baru (dalam derajat): "))
                    # Konversi ke radian
                    angles[joint] = np.radians(new_angle)
                else:
                    print("Nomor joint tidak valid!")
            except ValueError:
                print("Input tidak valid!")
        
        elif choice == '2':
            # Tampilkan posisi lengan
            plot_arm(angles)
        
        elif choice == '3':
            break
        
        else:
            print("Pilihan tidak valid!")

# Jalankan kontrol manual
if __name__ == "__main__":
    manual_angle_control()