#!/usr/bin/env python
'''
  A Simple mjpg stream http server for the Raspberry Pi Camera
  inspired by https://gist.github.com/n3wtron/4624820
'''
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import io
import time
import picam
import algo

s_first=True
s_picam=None
s_mainPage="""
<html><head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
</head><body>
<img src="/cam.mjpg"/>
</body></html>"""

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global s_first
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type',
                 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            stream = io.BytesIO()
            try:
                for i in s_picam.cam.capture_continuous(stream, "jpeg", 
                                                quality=5,
                                                use_video_port=True):
                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',len(stream.getvalue()))
                    self.end_headers()
                    val = stream.getvalue()
                    if s_first:
                        print(len(val))
                        print(val)
                        s_first = False

                    self.wfile.write(val)
                    stream.seek(0)
                    stream.truncate()

            except KeyboardInterrupt:
               print "get interrupted" 

            return
        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(s_mainPage)
            return

def main():
  global s_picam
  s_picam = picam.PiCam(resolution=(320, 240), framerate=60,
                        auto=True);
  try:
    server = HTTPServer(('',5080),CamHandler)
    print "server started"
    server.serve_forever()
  except KeyboardInterrupt:
    print "aborting server"
    s_picam.stop()
    server.socket.close()

if __name__ == '__main__':
  main()

