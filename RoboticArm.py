import cv2
import mediapipe as mp
import numpy as np
import time



# Initialize MediaPipe Hands
wCAM, hCAM = 640, 480
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(3, wCAM)
cap.set(4, hCAM)
pTime = 0


while cap.isOpened():
    ret, frame = cap.read()
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(frame,f'FPS: {int(fps)}',(450,40), cv2.FONT_HERSHEY_PLAIN,3,(255,0,0), 3)
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = hand_landmarks.landmark
            fingers = []   # RESET every frame
            h,w,c = frame.shape

            # ---- THUMB ----
            if landmarks[5].x < landmarks[4].x:
                fingers.append(1)
            else:
                fingers.append(0)

            # ---- OTHER 4 FINGERS ----
            tips_id = [8, 12, 16, 20]
            pip_id = [6, 10, 14, 18]
            thumb_tip = hand_landmarks.landmark[4]
            pinky_tip = hand_landmarks.landmark[20]
            thumb_x = int(thumb_tip.x *w)
            pinky_x = int(pinky_tip.x * w)

            if thumb_x < pinky_x:
                direction = "Right"
            else:
                direction = "LEFT"

            for tip, pip in zip(tips_id, pip_id):
                if landmarks[tip].y < landmarks[pip].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total_finger = fingers.count(1)

            cv2.putText(frame, f"Fingers: {total_finger}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, direction, (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("MediaPipe Hands Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break