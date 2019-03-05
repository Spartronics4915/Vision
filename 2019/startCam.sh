#!/bin/bash -f
uv4l -f \
 --driver raspicam \
 --vflip=yes \
 --hflip=yes \
 --auto-video_nr \
 --enable-server \
 --server-option '--enable-webrtc-audio=0' \
 --server-option '--webrtc-receive-audio=0' \
 --server-option '--webrtc-preferred-vcodec=3' \
 --server-option '--webrtc-hw-vcodec-maxbitrate=1500' \
 --server-option '--webrtc-enable-hw-codec'
