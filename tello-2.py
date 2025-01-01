from djitellopy import tello
from time import sleep
import cv2
me = tello.Tello()
me.connect()
print(me.get_battery())
#me.takeoff()

#me.land()
#me.move_forward(15)
me.streamon()
while True:
    img = me.get_frame_read().frame
    img = cv2.resize('Image', img)
    cv2.waitKey(1)