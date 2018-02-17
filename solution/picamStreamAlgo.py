#!/usr/bin/env python
'''
  A Simple mjpg stream http server for the Raspberry Pi Camera
  inspired by https://gist.github.com/n3wtron/4624820
  This variant runs the default algorithm on the stream, then
  runs a jpeg compressor on the result. This is sent over the
  wfile socket.
'''
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import time
import picam
import algo
import cv2
import sys

s_first = True
s_proof = True  # delete when defaultAlgo is working
s_picam=None
s_jpgParam = [int(cv2.IMWRITE_JPEG_QUALITY), 5]
s_mainPage="""
<html><head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
</head><body>
<img src="/cam.mjpg" width="640" height="480" />
</body></html>"""

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global s_first
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            try:
                while True:
                    camframe = s_picam.next()
                    if s_proof:
                        frame = algo.hsvAlgo(camframe)
                    else:
                        dx, frame = algo.defaultAlgo(camframe, display=True, 
                                                debug=False)
                    rc, jpg = cv2.imencode('.jpg', frame, s_jpgParam)
                    if not rc:
                        continue

                    if s_first:
                        print(jpg.size)
                        s_first = False

                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length', jpg.size)
                    self.end_headers()
                    self.wfile.write(jpg.tostring())

            except KeyboardInterrupt:
                print("Cam handler interrupted")

            return
        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(s_mainPage)
            return

def main():
    global s_picam

    if s_proof:
        s_picam = picam.PiCam(resolution=(320, 240), framerate=60, auto=True);
    else:
        s_picam = picam.PiCam(resolution=(320, 240), framerate=60);

    s_picam.start()

    try:
        server = HTTPServer(('',5080),CamHandler)
        print "server started"
        server.serve_forever()

    except KeyboardInterrupt:
        print("server stopped")
        s_picam.stop()
        server.socket.close()

if __name__ == '__main__':
  main()

