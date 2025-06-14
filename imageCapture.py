import cv2
'''
me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()

while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow("Image", img)
    cv2.waitKey(1)
    
encapsuler dans une classe
'''
def get_frame(tello):
    img = tello.get_frame_read().frame
    return cv2.resize(img, (360, 240))