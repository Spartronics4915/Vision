@echo off
if [%1]==[] (
	echo "Port required"
	exit /b
)

gst-launch-1.0 udpsrc port=%1 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! fpsdisplaysink sync=false text-overlay=false > NUL 2>&1
