import KeyPressModule as kp
from djitellopy import tello
import time
import cv2

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())  # Fix typo: battery instead of bettery
global img
me.streamon()


def getKeyboardInput():
    lr, fb, up, yv = 0, 0, 0, 0
    speed = 50

    if kp.getKey("LEFT"): lr = -speed  # Move left
    elif kp.getKey("RIGHT"): lr = speed  # Move right

    if kp.getKey("UP"): fb = speed  # Move forward
    elif kp.getKey("DOWN"): fb = -speed  # Move backward

    if kp.getKey("w"): up = speed  # Move up
    elif kp.getKey("s"): up = -speed  # Move down

    if kp.getKey("a"): yv = -speed  # Yaw left
    elif kp.getKey("d"): yv = speed  # Yaw right

    if kp.getKey("q"): 
        me.land()
        time.sleep(3)  # Land the drone
    if kp.getKey("e"): 
        me.takeoff()  # Take off

    if kp.getKey('z'):
        cv2.imwrite(f'/Users/rasul/Documents/Python/tello_edu/Resources/Images{time.time()}.jpg', img)
        time.sleep(0.4)

    return [lr, fb, up, yv]

while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    img = me.get_frame_read().frame
    img = cv2.resize(img, (600, 400))
    cv2.imshow("Image", img)
    cv2.waitKey(1)

