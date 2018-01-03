# USAGE
# python fps_demo.py
# python fps_demo.py --display 1
#
# NB: this is currently hardcoded for PiVideoStream
#   and thus requires a raspberry pi
# NNB: this seems to show that use of threading isn't
#   helpful.
# NNNB: please refer to testPiCam.py for a faster
#   implementation.

from __future__ import print_function
from video import PiVideoStream
from video import FPS
import argparse
import cv2
import numpy as np
import sys
import algo


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
#args = vars(ap.parse_args())
args = ap.parse_args()

# single threaded --------------------------------------------------
# grab a pointer to the video stream and initialize the FPS counter
print("[INFO] sampling NONTHREADED frames from picam...")
vs = PiVideoStream(framerate=60) # nb: we don't call start here
fps = FPS().start()

# loop over some frames
while fps._numFrames < args.num_frames:
    # grab the frame from the stream and resize it to have a maximum
    # width of 400 pixels
    frame = vs.next()
    sys.stderr.write('-')
    frame = algo.processFrame(frame)

    # check to see if the frame should be displayed to our screen
    if args.display > 0:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
vs.shutdown()
cv2.destroyAllWindows()

# two threaded -------------------------------------------------------
# created a *threaded *video stream, allow the camera senor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from picam...")
vs = PiVideoStream(framerate=60).start()  # starts update loop in separate thread
fps = FPS().start()

# loop over some frames...this time using the threaded stream
lastFrameNum = -1
while fps._numFrames < args.num_frames:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
    f = vs.frameNum
    if f != lastFrameNum:
        frame = vs.read()
        frame = algo.processFrame(frame)
        lastFrameNum = f

        # check to see if the frame should be displayed to our screen
        if args.display > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

        fps.update()


# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
vs.stop()
cv2.destroyAllWindows()
