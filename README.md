Gesture-Controlled Robotic Arm

A real-time robotic arm controlled using hand gestures detected through computer vision. The system tracks hand movements using MediaPipe and translates them into servo motor commands via serial communication.

Overview

This project demonstrates:

Real-time hand tracking

Gesture-to-servo angle mapping

Serial communication between laptop and microcontroller

Multi-servo coordination

The goal was to build an intuitive human-machine interaction system without physical controllers.

System Workflow

Webcam captures live video

MediaPipe detects 21 hand landmarks

Python calculates angles from landmark positions

Angle values sent via Serial

Microcontroller drives servos

Robotic arm mirrors hand movement

Technologies Used

Software

Python

OpenCV

MediaPipe

PySerial

Arduino IDE

Hardware

ESP32 / Arduino

4x Servo Motors
Communication

Baud Rate: 115200

Data format:

<base,shoulder,elbow,gripper>

Example:

<90,120,75,30>

Angles are clamped within safe limits before actuation.

Challenges Faced

Servo jitter due to hand tremor
→ Solved using smoothing logic and update threshold

Power instability from servo load
→ Used external regulated supply

Lighting affecting detection
→ Tested under controlled lighting conditions

Performance

Latency: ~120–180 ms

Frame rate: 20–30 FPS

Stable multi-servo response
External 5V power supply

Robotic arm structure (3D printed / acrylic)
