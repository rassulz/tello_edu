import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Настройки камеры
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)  # Используем первую камеру
cap.set(3, wCam)  # Устанавливаем ширину окна камеры
cap.set(4, hCam)  # Устанавливаем высоту окна камеры

pTime = 0  # Переменная для расчета FPS

# Инициализация детектора рук
detector = htm.HandDetector(detectionCon=0.7, maxHands=1)

# Инициализация управления громкостью
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# Инициализация переменных для громкости
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    if not success:
        print("Не удалось получить кадр с камеры")
        break

    # Обнаружение рук
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)

    if lmList:
        # Получение координат большого и указательного пальцев
        x1, y1 = lmList[4][1], lmList[4][2]  # Кончик большого пальца
        x2, y2 = lmList[8][1], lmList[8][2]  # Кончик указательного пальца
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Отображение точек и линии между пальцами
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Вычисление расстояния между пальцами
        length = math.hypot(x2 - x1, y2 - y1)

        # Масштабирование длины в диапазон громкости
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])

        # Установка громкости
        volume.SetMasterVolumeLevel(vol, None)

        # Индикатор "минимальной длины"
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Рисуем ползунок громкости
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # Расчет FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Отображение FPS на экране
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # Показ изображения
    cv2.imshow("Img", img)

    # Выход при нажатии ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
