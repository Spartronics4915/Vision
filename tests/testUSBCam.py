#!/usr/bin/env python
# --------------------------------------------------------------------
# search for tegra_cam.py for add'l gstreamer and built-in tx1 camera support
# (tk1 doesn't have a built-in camera)

import sys
import argparse
import cv2
import numpy as np
import subprocess

windowName = "CameraDemo"

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description=
                                     "Capture and display live camera video on Jetson")
    parser.add_argument("--vid", dest="video_dev",
                        help="video device # of USB webcam (/dev/video?) [0]",
                        default=0, type=int)
    parser.add_argument("--width", dest="image_width",
                        help="image width [1920]",
                        default=320, type=int)
    parser.add_argument("--height", dest="image_height",
                        help="image width [1080]",
                        default=240, type=int)
    parser.add_argument("--fps", dest="fps",
                        help="FPS",
                        default=30, type=int)
    parser.add_argument("--exposure", dest="exposure",
                        help="exposure: [5, 20000]",
                        default=10, type=int)
    args = parser.parse_args()
    return args

def open_cam_usb(dev, width, height, fps, exposure):
    # We want to set width and height here, otherwise we could just do:
    #     return cv2.VideoCapture(dev)
    if False:
        # this fails on tk1 with our custom build of opencv 3.3.1
        # gstreamer has an advantage over OpenCL in configuring
        # the camera.
        gst_str = ("v4l2src device=/dev/video{} ! "
                   "video/x-raw, width=(int){}, height=(int){}, format=(string)RGB ! "
                   "videoconvert ! appsink").format(dev, width, height)
        return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
    else:
        cap = cv2.VideoCapture(dev)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps) # db: 10 is definitely slower than 60
        #ret_val, displayBuf = cap.read() 
        # exposure_auto of 1 means manual, 3 means aperture priority mode (camera-specific)
        # value must be set to one prior to setting exposure_absolute
        subprocess.call("v4l2-ctl --device=/dev/video%d "\
                        "--set-ctrl exposure_auto=1 "\
                        "--set-ctrl exposure_absolute=%d" % (dev, exposure),
                        shell=True)
        return cap

def open_window(windowName, width, height):
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName, width, height)
    cv2.moveWindow(windowName, 0, 0)
    cv2.setWindowTitle(windowName, "Camera Demo for Jetson TX2/TX1")

def read_cam(windowName, cap):
    showHelp = True
    showFullScreen = False
    helpText = "'Esc' to Quit, 'H' to Toggle Help, 'F' to Toggle Fullscreen"
    font = cv2.FONT_HERSHEY_PLAIN
    while True:
        if cv2.getWindowProperty(windowName, 0) < 0: # Check to see if the user closed the window
            # This will fail if the user closed the window; Nasties get printed to the console
            break;
        ret_val, displayBuf = cap.read();
        if showHelp == True:
            cv2.putText(displayBuf, helpText, (11,20), font, 1.0, (32,32,32), 4, cv2.LINE_AA)
            cv2.putText(displayBuf, helpText, (10,20), font, 1.0, (240,240,240), 1, cv2.LINE_AA)
        cv2.imshow(windowName, displayBuf)
        key = cv2.waitKey(10)
        if key == 27: # ESC key: quit program
            break
        elif key == ord('H') or key == ord('h'): # toggle help message
            showHelp = not showHelp
        elif key == ord('F') or key == ord('f'): # toggle fullscreen
            showFullScreen = not showFullScreen
            if showFullScreen == True: 
                cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL) 

if __name__ == "__main__":
    args = parse_args()
    print("Called with args:")
    print(args)
    print("OpenCV version: {}".format(cv2.__version__))

    cap = open_cam_usb(args.video_dev, args.image_width, args.image_height, args.fps, args.exposure)

    if not cap.isOpened():
        sys.exit("Failed to open camera!")

    open_window(windowName, args.image_width, args.image_height)
    read_cam(windowName, cap)
    
    cap.release()
    cv2.destroyAllWindows()
