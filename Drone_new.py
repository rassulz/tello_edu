import cv2
import numpy as np
from djitellopy import Tello
import KeyPressModule as kp
import math
from time import sleep

# Параметры дрона и PID-регулятора
fSpeed = 117 / 10  # Скорость вперёд в см/с (15 см/с)
aSpeed = 360 / 10  # Угловая скорость в градусах/с (50 град/с)
interval = 0.25
dInterval = fSpeed * interval
aInterval = aSpeed * interval
x, y = 500, 500
yaw = 0
kp.init()

me = Tello()
me.connect()
print(f"Battery: {me.get_battery()}%")
me.streamon()

# Параметры карты
points = [(0, 0), (0, 0)]

# Параметры PID для отслеживания лица
w, h = 360, 240
fbRange = [6200, 6800]
pid = [0.4, 0.4, 0]
pError = 0


def getKeyboardInput():
    global x, y, yaw
    lr, fb, ud, yv = 0, 0, 0, 0
    d = 0

    if kp.getKey("LEFT"):
        lr = -15
        d = dInterval
    elif kp.getKey("RIGHT"):
        lr = 15
        d = -dInterval

    if kp.getKey("UP"):
        fb = 15
        d = dInterval
    elif kp.getKey("DOWN"):
        fb = -15
        d = -dInterval

    if kp.getKey("w"):
        ud = 15
    elif kp.getKey("s"):
        ud = -15

    if kp.getKey("a"):
        yv = -50
        yaw -= aInterval
    elif kp.getKey("d"):
        yv = 50
        yaw += aInterval

    if kp.getKey("q"):
        me.land()
        sleep(3)
    if kp.getKey("e"):
        me.takeoff()

    sleep(interval)

    x += int(d * math.cos(math.radians(yaw)))
    y += int(d * math.sin(math.radians(yaw)))

    return [lr, fb, ud, yv, x, y]


def drawPoints(img, points):
    for point in points:
        cv2.circle(img, point, 5, (0, 0, 255), cv2.FILLED)

    cv2.circle(img, points[-1], 8, (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'({(points[-1][0] - 500) / 100},{(points[-1][1] - 500) / 100})m',
                (points[-1][0] + 10, points[-1][1] + 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)


def findFace(img):
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListC = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cx, cy = x + w // 2, y + h // 2
        area = w * h
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]


def trackFace(info, w, pid, pError):
    area = info[1]
    x, y = info[0]
    fb = 0

    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))

    if fbRange[0] < area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20

    if x == 0:
        speed = 0
        error = 0

    me.send_rc_control(0, fb, 0, speed)
    return error


while True:
    # Получение данных от клавиатуры
    keyboard_vals = getKeyboardInput()

    # Получение видео с камеры дрона
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w, h))

    # Отслеживание лица
    img, face_info = findFace(img)
    pError = trackFace(face_info, w, pid, pError)

    # Построение карты маршрута
    map_img = np.zeros((1000, 1000, 3), np.uint8)
    if points[-1][0] != keyboard_vals[4] or points[-1][1] != keyboard_vals[5]:
        points.append((keyboard_vals[4], keyboard_vals[5]))
    drawPoints(map_img, points)

    # Отображение окон
    cv2.imshow("Face Tracking", img)
    cv2.imshow("Route Map", map_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break

cv2.destroyAllWindows()
