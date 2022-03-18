#!/bin/bash


export checkit=`ps -ef | grep gst-launch | grep -v grep | awk '{print $2}'`
if [ ! -z "$checkit" ]; then echo "Running"; fi
