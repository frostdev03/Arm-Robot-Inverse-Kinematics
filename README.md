# Arm Robot with Inverse Kinematics (5 DoF)

This repository showcases a robotic arm project controlled by an ESP-32 microcontroller using Inverse Kinematics. The robotic arm is designed to perform precise movements, enabling tasks such as object manipulation in a defined workspace. It incorporates advanced algorithms for movement control and real-time adjustments.

## Features

- **Manual Control:** For controling robot manually.
- **Inverse Kinematics:** For precise control of the robot's arm positions.
- **ESP-32 Integration:** Provides wireless connectivity and control.
- **Object Detection:** Integration with cameras for identifying target objects.

## Hardware Requirements

- ESP-32 Devkit V1 microcontroller
- ESP-32 CAM Ai Thinker or any camera module 
- Servos and stepper motors
- Power supply (suitable for servo operation)

## Software Requirements

- Arduino IDE
- Necessary Arduino libraries (see `libraries,txt` or source files)
- Python

## Setup

1. **Hardware Assembly:** Assemble the robot arm with servos, motors, and ESP-32 as per the wiring instructions.
2. **Software Installation:**
   - Upload the code to the ESP-32 using Arduino IDE.
   - Install required Python packages if simulations are used.
   - Connect and access the camera (automation).
   - Control manually in browser using websocket (just write the ESP32 IP address in ur browser).
3. **Run the System:** Power on the ESP-32 and control the arm using the provided control mechanisms.

## Main Program

- websocket_bismillah: Code for ESP32.
- accessing_camera: Code for ESP32-CAM.
- main: Main program for algorithm.

## Usage

- Use the algorithm to calculate arm positions based on desired end-effector coordinates.
- Fine-tune servo angles for optimal movement.
- Monitor the system using the connected interface for real-time feedback.

## Future Enhancements

- Enhanced precision using advanced IK solvers.
- Integration of machine learning for autonomous task handling.
- Expansion of object detection capabilities.

## Screenshots

<img src="https://github.com/user-attachments/assets/2f7f13a1-ddfe-4c00-a1a9-3f03bd8d3ddd" alt="Screenshot of robot control interface" width="500">
<img src="https://github.com/user-attachments/assets/037d5610-ae41-44bc-a78f-7c18993b74a0" alt="Screenshot of object detection" width="500">

Cheers
