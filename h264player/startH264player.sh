#!/bin/sh
#
# To wire this into frcvision's startup machinery, invoke
# this script from ~/runCamera as follows:
#
#   exec /home/pi/spartronics/Vision/h264player/startH264player.sh
#
# or copy it to ~/startH264player.sh, then 'source' it:
#
#   . ./startH264player.sh
#
#
echo "Starting h264player ----------------------------"
cd /home/pi/spartronics/Vision/h264player
exec node appRaspi.js

