import picamera
import picamera.array
import picamera.streams
import time
import io
import cv2
import numpy as np
with picamera.PiCamera(resolution = (1920,1080), framerate = 30) as camera:
    stream = io.BytesIO()
    cap = camera.capture_continuous(stream, format="jpeg", use_video_port=True)
    while True:   
        startTime = time.monotonic() 
        frame = next(cap)
        #startTime = time.monotonic()
        stream.seek(0)
        
        stream.truncate()
       
        #frame = np.fromstring(frame)

        #image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        
        print(str(frame))
        endTime = time.monotonic()
        print("Delta T: {}".format(endTime-startTime))
