#!/bin/bash -f

logdir=/var/tmp/rmslog
if [ ! -d $logdir ]; then
  mkdir -p $logdir
  mkdir $logdir/00
  mkdir $logdir/01
  mkdir $logdir/02
  mkdir $logdir/03
  mkdir $logdir/04
  mkdir $logdir/05
  mkdir $logdir/06
  mkdir $logdir/07
  mkdir $logdir/08
  mkdir $logdir/09
fi

webhome=/home/pi/spartronics/Vision/2019/rwsweb
cd /opt/rws
./webrtc-streamer \
  -conf "$webhome/etc/webrtc_streamer.conf" \
  -log $logdir

echo "rws terminated"

