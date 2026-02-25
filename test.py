import cv2
import mediapipe as mp
import time
import math
import serial
import struct

# ---------------- SERIAL ----------------
SERIAL_PORT = 'COM4'
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
time.sleep(2)
ser.reset_input_buffer()

print("Waiting for ESP32...")

while True:
    if ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()
        if line == "READY":
            break

print("ESP32 Connected\n")

# ---------------- CAMERA ----------------
wCAM, hCAM = 1280, 1080
cap = cv2.VideoCapture(0)
cap.set(3, wCAM)
cap.set(4, hCAM)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# ---------------- ROBOT STATE ----------------
base_angle = shoulder_angle = elbow_angle = 90
gripper = 0
prev_base = prev_shoulder = prev_elbow = 90
prev_gripper = 0

XY_SENS = 0.6
Z_SENS = 300

alpha = 0.85
smooth_base = smooth_shoulder = smooth_elbow = 90
smooth_z = None

DEADBAND = 2
MIN_SEND_DIFF = 3

# ---------------- PACKET FUNCTION ----------------
def send_arm_data(a1, a2, a3, claw):
    header = 0xAA
    checksum = (a1 + a2 + a3 + claw) % 256
    packet = struct.pack('BBBBBB', header, a1, a2, a3, claw, checksum)
    ser.write(packet)

    start = time.time()
    while time.time() - start < 0.08:
        if ser.in_waiting:
            if ser.readline().decode(errors='ignore').strip() == "OK":
                return True
    return False

# ---------------- MAIN LOOP ----------------
pTime = 0

while True:
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    h, w, _ = frame.shape

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]

        lm = []
        for lmData in handLms.landmark:
            cx = int(lmData.x * w)
            cy = int(lmData.y * h)
            cz = lmData.z
            lm.append((cx, cy, cz))

        # -------- SCALE INVARIANT PINCH --------
        x1,y1,_ = lm[4]
        x2,y2,_ = lm[8]
        x3,y3,_ = lm[5]
        x4,y4,_ = lm[17]

        pinch_dist = math.hypot(x2-x1, y2-y1)
        hand_scale = math.hypot(x4-x3, y4-y3)
        ratio = pinch_dist/hand_scale if hand_scale else 1

        if ratio < 0.35:
            gripper = 1
        elif ratio > 0.55:  
            gripper = 0
        print(gripper)

        pinch_color = (0,0,255) if gripper else (0,255,0)
        cv2.circle(frame, (x1,y1), 10, pinch_color, 2)
        cv2.circle(frame, (x2,y2), 10, pinch_color, 2)
        cv2.line(frame, (x1,y1), (x2,y2), pinch_color, 2)
        cv2.putText(frame, f"Pinch Ratio: {ratio:.2f}", (20,50), 0, 0.8, pinch_color, 2)

        # -------- POSITION --------
        px,py,pz = lm[9]
        dx = px - w//2
        dy = py - h//2

        cv2.circle(frame, (px,py), 8, (255,0,255), -1)
        cv2.line(frame, (w//2,h//2), (px,py), (255,0,255), 2)

        if smooth_z is None:
            smooth_z = pz
        smooth_z = alpha*smooth_z + (1-alpha)*pz

        target_base = int(max(0,min(180,90 + dx*XY_SENS)))
        target_shoulder = int(max(10,min(170,90 - dy*XY_SENS)))
        target_elbow = int(max(10,min(170,90 - smooth_z*Z_SENS)))

        smooth_base = alpha*smooth_base + (1-alpha)*target_base
        smooth_shoulder = alpha*smooth_shoulder + (1-alpha)*target_shoulder
        smooth_elbow = alpha*smooth_elbow + (1-alpha)*target_elbow

        base_angle = int(smooth_base)
        shoulder_angle = int(smooth_shoulder)
        elbow_angle = int(smooth_elbow)

        changed = (
            abs(base_angle-prev_base)>MIN_SEND_DIFF or
            abs(shoulder_angle-prev_shoulder)>MIN_SEND_DIFF or
            abs(elbow_angle-prev_elbow)>MIN_SEND_DIFF or
            gripper!=prev_gripper
        )

        if changed:
            if send_arm_data(base_angle,shoulder_angle,elbow_angle,gripper):
                prev_base,prev_shoulder,prev_elbow,prev_gripper = base_angle,shoulder_angle,elbow_angle,gripper

        mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

        # -------- HUD --------
        cv2.putText(frame, f"Base: {base_angle}", (20,100), 0, 0.8, (0,255,0),2)
        cv2.putText(frame, f"Shoulder: {shoulder_angle}", (20,130),0,0.8,(0,255,0),2)
        cv2.putText(frame, f"Elbow: {elbow_angle}", (20,160),0,0.8,(0,255,0),2)
        cv2.putText(frame, f"Grip: {gripper}", (20,190),0,0.8,(0,255,0),2)

    # FPS
    cTime = time.time()
    fps = 1/(cTime-pTime) if pTime else 0
    pTime = cTime

    cv2.putText(frame,f"FPS:{int(fps)}",(550,40),0,0.8,(255,0,0),2)
    cv2.imshow("Gesture Control MeArm",frame)

    if cv2.waitKey(1)&0xFF==27:
        break

cap.release()
ser.close()
cv2.destroyAllWindows()