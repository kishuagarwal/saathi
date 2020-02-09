import cv2
import numpy as np
import socket
from cStringIO import StringIO

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 50007))
    print 'Connected to the server'
    video_frame = client_socket.recv(1000 * 1024)
    print('data got', len(video_frame))
    video_frame = np.load(StringIO(video_frame))['frame']
    gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('video_frame', gray)
    import time
    cv2.waitKey(1)
    time.sleep(10)
    print 'Closing connection to server'
    client_socket.close()
