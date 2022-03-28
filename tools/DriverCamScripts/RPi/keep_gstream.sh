#!/bin/bash

target=${1:-10.49.15.5}
port=${2:-5805}

while true
do
	check=`/home/pi/check_gstream.sh`
	if [ -z "$check" ]; then
		now=`date`
		echo "Restarting $now"
		/home/pi/gstreamit.sh $target $port > /dev/null 2>&1 &
	else
		sleep 30
	fi
done
