#!/bin/bash -f

webhome=/home/pi/spartronics/Vision/2019/rwsweb
cd /opt/rws
./webrtc-streamer \
  -conf "$webhome/etc/webrtc_streamer.conf" \
  -log /var/log/rws

echo "rws terminated"

