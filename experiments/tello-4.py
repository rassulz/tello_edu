import cv2
import mediapipe as mp
from djitellopy import Tello
import time

# Инициализация Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Инициализация Tello
tello = Tello()
tello.connect()
print(f"Батарея: {tello.get_battery()}%")

# Функция для вычисления направления движения
def get_thumb_direction(landmarks, img_width, img_height):
    thumb_tip = landmarks[4]  # Вершина большого пальца
    thumb_base = landmarks[2]  # Основание большого пальца

    # Координаты в пикселях
    thumb_tip_x = int(thumb_tip.x * img_width)
    thumb_tip_y = int(thumb_tip.y * img_height)
    thumb_base_x = int(thumb_base.x * img_width)
    thumb_base_y = int(thumb_base.y * img_height)

    # Направление: вверх, вниз, влево, вправо
    if abs(thumb_tip_y - thumb_base_y) > abs(thumb_tip_x - thumb_base_x):
        if thumb_tip_y < thumb_base_y:
            return "up"
        else:
            return "down"
    else:
        if thumb_tip_x > thumb_base_x:
            return "right"
        else:
            return "left"

# Инициализация камеры
cap = cv2.VideoCapture(0)

tello.takeoff()
time.sleep(2)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Отразим изображение и переведем в RGB
        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Распознавание руки
        results = hands.process(img_rgb)
        img_height, img_width, _ = frame.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                direction = get_thumb_direction(landmarks, img_width, img_height)

                # Отображение направления на экране
                cv2.putText(frame, f"Direction: {direction}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Управление дроном
                if direction == "up":
                    tello.move_up(20)
                elif direction == "down":
                    tello.move_down(20)
                elif direction == "left":
                    tello.move_left(20)
                elif direction == "right":
                    tello.move_right(20)

        # Показ изображения
        cv2.imshow("Tello Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    tello.land()
    cap.release()
    cv2.destroyAllWindows()
