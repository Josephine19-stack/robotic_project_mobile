from djitellopy import tello

def init_tello_video():
    me = tello.Tello()
    me.connect()
    return me

def init_stream(me):
    me.streamon()
    return me

def close_stream(me):
    me.streamoff()