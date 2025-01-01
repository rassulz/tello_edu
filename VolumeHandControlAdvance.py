import cv2
import mediapipe as mp
from djitellopy import Tello

# Инициализация Tello
drone = Tello()
drone.connect()
drone.streamon()

# Инициализация Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Функция для распознавания жестов
def recognize_gesture(hand_landmarks):
    if hand_landmarks:
        landmarks = hand_landmarks[0].landmark
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
        wrist = landmarks[mp_hands.HandLandmark.WRIST]

        # Жест "ОК"
        thumb_index_dist = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        if thumb_index_dist < 0.05:
            return "OK"

        # Жест "Ладонь"
        palm_open = all(landmark.y < wrist.y for landmark in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip])
        if palm_open:
            return "PALM"

    return None

# Основной цикл обработки
with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) as hands:
    while True:
        # Получение кадра с камеры дрона
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (640, 480))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Распознавание жестов
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = recognize_gesture(results.multi_hand_landmarks)
                if gesture == "OK":
                    drone.send_rc_control(0, 30, 0, 0)  # Лететь вперед
                elif gesture == "PALM":
                    drone.send_rc_control(0, -30, 0, 0)  # Лететь назад
                else:
                    drone.send_rc_control(0, 0, 0, 0)  # Остановиться

        # Показ изображения
        cv2.imshow("Tello Camera", frame)

        # Обработка нажатий клавиш
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Завершить программу
            break
        elif key == ord('e'):  # Взлет
            drone.takeoff()
        elif key == ord('l'):  # Посадка
            drone.land()

# Завершение
drone.streamoff()
cv2.destroyAllWindows()
