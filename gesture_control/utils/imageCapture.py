import cv2

def get_frame(tello):
    img = tello.get_frame_read().frame
    return cv2.resize(img, (640, 480))