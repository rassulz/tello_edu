import KeyPressModule as kp
from djitellopy import tello
import time
import cv2

# Initialize the drone
kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
global img
me.streamon()

# Function to handle mouse click events and display RGB values
def mouseRGB(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # When left mouse button is clicked
        colorsBGR = img[y, x]  # Get the BGR values of the pixel
        colorsRGB = (colorsBGR[2], colorsBGR[1], colorsBGR[0])  # Convert BGR to RGB
        print(f"RGB Value at ({x}, {y}) is {colorsRGB}")  # Print RGB values
        cv2.putText(img, f'RGB: {colorsRGB}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (255, 255, 255), 2)

def getKeyboardInput():
    lr, fb, up, yv = 0, 0, 0, 0
    speed = 50

    # Drone movement commands
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
        time.sleep(3)  
    if kp.getKey("e"): 
        me.takeoff()  # Take off

    if kp.getKey('z'):  # Save an image when 'z' is pressed
        cv2.imwrite(f'/Users/rasul/Documents/Python/tello_edu/Resources/Images{time.time()}.jpg', img)
        time.sleep(0.4)

    return [lr, fb, up, yv]

# Main loop
while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    img = me.get_frame_read().frame  # Get the current frame
    img = cv2.resize(img, (600, 400))  # Resize the frame
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    cv2.imshow("Image", img)

    # Set mouse callback to detect RGB values
    cv2.setMouseCallback("Image", mouseRGB)

    cv2.waitKey(1)
