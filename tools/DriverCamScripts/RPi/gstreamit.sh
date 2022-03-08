#!/bin/bash

target=${1:-10.49.15.20}
port=${2:-5805}

raspivid -t 0 -w 640 -h 480 -fps 10 -rot 0 -b 2000000 -o - | gst-launch-1.0 -e -vvv fdsrc ! h264parse ! rtph264pay pt=96 config-interval=5 ! udpsink host=$target port=$port
