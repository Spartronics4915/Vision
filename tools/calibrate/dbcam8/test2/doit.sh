#!/bin/bash -f

#
# 60 seconds of frames captured each 4 seconds.
#
sleep 2
raspistill -t 60000 -tl 4000 -w 640 -h 480 -o chessboard.%04d.jpg

