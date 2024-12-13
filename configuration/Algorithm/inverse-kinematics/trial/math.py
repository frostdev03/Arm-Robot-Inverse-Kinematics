# import math

# # Panjang segmen lengan (cm)
# L1 = 7   # Jarak dari base ke pivot pertama
# L2 = 24  # Lower arm
# L3 = 17  # Center arm

# def inverse_kinematics(x, y, z):
#     # Base rotation
#     theta1 = math.atan2(y, x)
    
#     # Effective length and height
#     r = math.sqrt(x**2 + y**2)
#     h = z - L1
    
#     # Compute joint angles
#     d = math.sqrt(r**2 + h**2)  # Panjang efektif
#     theta2 = math.atan2(h, r) + math.acos((L2**2 + d**2 - L3**2) / (2 * L2 * d))
#     theta3 = math.acos((L2**2 + L3**2 - d**2) / (2 * L2 * L3))
    
#     return math.degrees(theta1), math.degrees(theta2), math.degrees(theta3)

# # Contoh penggunaan
# x_target, y_target, z_target = 20, 10, 30
# theta1, theta2, theta3 = inverse_kinematics(x_target, y_target, z_target)

# print(f"Theta1: {theta1:.2f}°")
# print(f"Theta2: {theta2:.2f}°")
# print(f"Theta3: {theta3:.2f}°")

import numpy as np

# Fungsi untuk menghitung panjang vektor
def vector_length(vector):
    return np.sqrt(np.sum(np.square(vector)))

# Fungsi inverse kinematics sederhana
def inverse_kinematics(x, y, z, link_lengths):
    """
    Menghitung sudut servo berdasarkan target posisi x, y, z.
    Args:
        x, y, z: Koordinat posisi target end-effector
        link_lengths: Panjang tiap segmen robot arm [L1, L2, L3]

    Returns:
        List berisi sudut tiap servo dalam derajat [theta1, theta2, theta3]
    """
    L1, L2, L3 = link_lengths

    # Hitung sudut theta1 (rotasi pada basis)
    theta1 = np.arctan2(y, x)

    # Hitung proyeksi jarak horizontal dan vertikal
    r = np.sqrt(x**2 + y**2)  # Jarak horizontal
    z_eff = z - L1  # Ketinggian efektif setelah link 1

    # Hitung jarak ke target
    d = np.sqrt(r**2 + z_eff**2)

    # Cek apakah target dapat dijangkau
    if d > (L2 + L3):
        raise ValueError("Target berada di luar jangkauan.")

    # Gunakan hukum cosinus untuk mencari sudut theta2 dan theta3
    cos_theta2 = (L2**2 + d**2 - L3**2) / (2 * L2 * d)
    sin_theta2 = np.sqrt(1 - cos_theta2**2)
    theta2 = np.arctan2(z_eff, r) - np.arctan2(sin_theta2, cos_theta2)

    cos_theta3 = (L2**2 + L3**2 - d**2) / (2 * L2 * L3)
    sin_theta3 = np.sqrt(1 - cos_theta3**2)
    theta3 = np.arctan2(sin_theta3, cos_theta3)

    # Konversi sudut ke derajat
    theta1_deg = np.degrees(theta1)
    theta2_deg = np.degrees(theta2)
    theta3_deg = np.degrees(theta3)

    return [theta1_deg, theta2_deg, theta3_deg]

# Contoh penggunaan
if __name__ == "__main__":
    # Panjang link (dalam cm)
    link_lengths = [10, 15, 20]  # Contoh panjang link

    # Target posisi end-effector
    target_x = 15
    target_y = 10
    target_z = 25

    try:
        angles = inverse_kinematics(target_x, target_y, target_z, link_lengths)
        print("Sudut servo (dalam derajat):", angles)
    except ValueError as e:
        print("Error:", e)
