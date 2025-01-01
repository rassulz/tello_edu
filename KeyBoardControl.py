import KeyPressModule as kp
from djitellopy import tello
from time import sleep

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())  # Fix typo: battery instead of bettery

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
        me.land()  # Land the drone
    if kp.getKey("e"): 
        me.takeoff()  # Take off

    return [lr, fb, up, yv]

while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)

