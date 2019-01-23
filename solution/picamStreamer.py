#!/usr/bin/env python

'''
  A Simple mjpg stream http server for the Raspberry Pi Camera
  inspired by https://gist.github.com/n3wtron/4624820
'''
from http.server import BaseHTTPRequestHandler,HTTPServer
import io
import time
import picam
import algo

s_first=True
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
        print(self.path)
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type',
                 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            stream = io.BytesIO()
            cam = None
            try:
                time.sleep(2) # wait for shutdown of alt stream
                cam = picam.PiCam(resolution=(320, 240), framerate=60, auto=True)
                for i in cam.cam.capture_continuous(stream, "jpeg", 
                                                quality=5,
                                                use_video_port=True):
                    self.wfile.write(bytes("--jpgboundary\n",'utf-8'))
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',len(stream.getvalue()))
                    self.end_headers()
                    val = stream.getvalue()
                    if s_first:
                        #print(len(val))
                        #print(val)
                        s_first = False

                    self.wfile.write(val)
                    stream.seek(0)
                    stream.truncate()

            except Exception as e: print(e)

            print("done streaming")

            if cam:
                cam.stop() # triggers PiCamera.close()
            else:
                print("(cam init problem)")

            stream.seek(0)
            stream.truncate()

            return

        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(bytes(s_mainPage,'utf-8'))
            return

def main():
  try:
    server = HTTPServer(('',5080),CamHandler)
    print ("server started")
    server.serve_forever()
  except KeyboardInterrupt:
    print ("aborting server")
    server.socket.close()

if __name__ == '__main__':
  main()

