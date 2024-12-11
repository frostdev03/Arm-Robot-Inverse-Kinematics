import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

# Fungsi untuk memvisualisasikan robot
def plot_robot(angles):
    positions = forward_kinematics(angles)
    x = [pos[0] for pos in positions]
    y = [pos[1] for pos in positions]
    z = [pos[2] for pos in positions]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, '-o', label='Robot Arm')

    ax.set_title('Simulasi Robot Arm 5 DOF')
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    ax.legend()
    plt.show()

# Fungsi untuk memperbarui plot saat nilai input teks diubah
def update_plot():
    try:
        angles = [
            np.radians(float(entry_theta1.get())),
            np.radians(float(entry_theta2.get())),
            np.radians(float(entry_theta3.get())),
            np.radians(float(entry_theta4.get())),
            np.radians(float(entry_theta5.get()))
        ]
        plot_robot(angles)
    except ValueError:
        print("Masukkan nilai yang valid untuk semua sudut.")

# Membuat GUI menggunakan Tkinter
root = tk.Tk()
root.title("Robot Arm 5 DOF - Control Panel")

# Input teks untuk setiap sudut
label_theta1 = tk.Label(root, text="Theta 1 (Base Rotation):")
label_theta1.pack()
entry_theta1 = tk.Entry(root)
entry_theta1.insert(0, "45")  # Set default to 45 degrees
entry_theta1.pack()

label_theta2 = tk.Label(root, text="Theta 2 (Lower Arm):")
label_theta2.pack()
entry_theta2 = tk.Entry(root)
entry_theta2.insert(0, "45")
entry_theta2.pack()

label_theta3 = tk.Label(root, text="Theta 3 (Center Arm):")
label_theta3.pack()
entry_theta3 = tk.Entry(root)
entry_theta3.insert(0, "45")
entry_theta3.pack()

label_theta4 = tk.Label(root, text="Theta 4 (Upper Arm):")
label_theta4.pack()
entry_theta4 = tk.Entry(root)
entry_theta4.insert(0, "45")
entry_theta4.pack()

label_theta5 = tk.Label(root, text="Theta 5 (Neck/Gripper):")
label_theta5.pack()
entry_theta5 = tk.Entry(root)
entry_theta5.insert(0, "0")
entry_theta5.pack()

# Tombol untuk memperbarui plot
update_button = tk.Button(root, text="Update Plot", command=update_plot)
update_button.pack()

# Menjalankan aplikasi Tkinter
root.mainloop()
