import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

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

    # Validasi agar tetap dalam rentang ruang kerja (0 - 80 cm)
    x_physical = max(0, min(x_physical, physical_workspace_x))
    y_physical = max(0, min(y_physical, physical_workspace_y))

    return x_physical, y_physical

# Fungsi untuk forward kinematics
def forward_kinematics(angles):
    θ1, θ2, θ3, θ4, θ5, θ6 = angles
    x, y, z = 0, 0, base_thickness
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

# Fungsi untuk membuat dataset
def generate_dataset(num_samples=1000):
    angles_data = []
    target_data = []
    
    for _ in range(num_samples):
        # Randomly generate angles within valid ranges
        angles = np.random.uniform([0, 0, -np.pi/2, -np.pi/2, 0, -np.pi/6], [2*np.pi, np.pi/2, np.pi/2, np.pi/2, L5, np.pi/6])
        
        # Get end-effector position using forward kinematics
        position = forward_kinematics(angles)[-1]
        x, y, z = position
        
        # Store data
        angles_data.append(angles)
        target_data.append([x, y, z])
    
    angles_data = np.array(angles_data)
    target_data = np.array(target_data)
    
    return angles_data, target_data

# Generate dataset
angles_data, target_data = generate_dataset()

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(target_data, angles_data, test_size=0.2)

# Build the neural network model
model = Sequential()
model.add(Dense(64, input_dim=3, activation='relu'))  # Input layer (x, y, z)
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(6))  # Output layer (θ1, θ2, θ3, θ4, θ5, θ6)

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X_train, y_train, epochs=100, batch_size=32)

# Evaluate the model
loss = model.evaluate(X_test, y_test)
print(f'Model Loss: {loss}')

# Predict angles for a new target
x_camera = 210
y_camera = 160
x_target, y_target = camera_to_physical(x_camera, y_camera)
print(f"Converted Camera Coordinates to Physical: x_target={x_target}, y_target={y_target}")

z_target = 10  # Example height

predicted_angles = model.predict(np.array([[x_target, y_target, z_target]]))
print(f"Predicted Angles: {predicted_angles}")

# Visualize the predicted angles with forward kinematics
angles = predicted_angles.flatten()
positions = forward_kinematics(angles)
x_coords, y_coords, z_coords = zip(*positions)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(x_coords, y_coords, z_coords, '-o', markersize=10, lw=3, label="Robot Arm")
ax.scatter(x_target, y_target, z_target, color='red', s=100, label="Target Location")
ax.set_xlim([0, 80])
ax.set_ylim([0, 80])
ax.set_zlim([0, 80])
ax.set_xlabel("X Position (cm)")
ax.set_ylabel("Y Position (cm)")
ax.set_zlabel("Z Position (cm)")
plt.legend()
plt.title("6-DOF Robot Arm - Neural Network IK")
plt.show()
