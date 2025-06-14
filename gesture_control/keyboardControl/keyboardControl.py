from djitellopy import tello
import keyPressModule as kp
from time import sleep

kp.init()
me = tello.Tello()
me.connect()
print(f"battery is {me.get_battery()}")

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kp.getKey("LEFT"): lr = -speed
    elif kp.getKey("RIGHT"): lr = speed

    if kp.getKey("UP"): fb = speed
    elif kp.getKey("DOWN"): fb = -speed

    if kp.getKey("w"): ud = speed
    elif kp.getKey("s"): ud = -speed

    if kp.getKey("a"): yv = speed
    elif kp.getKey("d"): yv = -speed

    if kp.getKey("q"): me.land()
    if kp.getKey("e"): me.takeoff()

    return [lr, fb, ud, yv]

while True:
    vals = getKeyboardInput()
    print(f"keyboard inputs are : {vals}")
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)